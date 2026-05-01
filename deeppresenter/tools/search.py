import asyncio
import os
import re
from io import BytesIO
from pathlib import Path
from typing import Any, Literal

import aiohttp
import httpx
import markdownify
from fake_useragent import UserAgent
from fastmcp import FastMCP
from PIL import Image
from playwright.async_api import TimeoutError
from trafilatura import extract

from deeppresenter.utils.constants import (
    MAX_RETRY_INTERVAL,
    MCP_CALL_TIMEOUT,
    RETRY_TIMES,
)
from deeppresenter.utils.log import debug, set_logger, warning
from deeppresenter.utils.webview import PlaywrightConverter, playwright_lifespan

mcp = FastMCP(name="Search", lifespan=playwright_lifespan)

FAKE_UA = UserAgent()

# Yandex Search API
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY", "")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID", "")
YANDEX_SEARCH_URL = "https://searchapi.api.cloud.yandex.net/v2/web/search"
YANDEX_IMAGES_URL = "https://searchapi.api.cloud.yandex.net/v2/image/search"
YANDEX_SEARCH_TYPE = os.getenv("YANDEX_SEARCH_TYPE", "SEARCH_TYPE_RU")

# Tavily
TAVILY_KEYS = [
    i.strip()
    for i in os.getenv("TAVILY_API_KEY", "").split(",")
    if i.strip().startswith("tvly")
]
TAVILY_API_URL = "https://api.tavily.com/search"

debug(f"{len(YANDEX_API_KEY)} Yandex API key loaded")
debug(
    f"Yandex folder_id: {YANDEX_FOLDER_ID[:16]}..."
    if YANDEX_FOLDER_ID
    else "No Yandex folder_id"
)
debug(f"{len(TAVILY_KEYS)} TAVILY keys loaded")


# ── Yandex helpers ─────────────────────────────────────────────────────────────


async def _yandex_search_request(query: str, limit: int = 5) -> dict[str, Any]:
    import base64
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "query": {"searchType": YANDEX_SEARCH_TYPE, "queryText": query},
        "folderId": YANDEX_FOLDER_ID,
        "pageSize": limit,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            YANDEX_SEARCH_URL, headers=headers, json=payload
        ) as response:
            if response.status == 200:
                result = await response.json()
                xml_data = base64.b64decode(result.get("rawData", ""))
                from xml.etree import ElementTree as ET
                root = ET.fromstring(xml_data)
                ns = {"y": "http://www.yandex.ru/searchapi"}
                results = []
                for doc in root.findall(".//y:doc", ns)[:limit]:
                    results.append({
                        "title": doc.find("y:title", ns).text if doc.find("y:title", ns) is not None else "",
                        "url": doc.find("y:url", ns).text if doc.find("y:url", ns) is not None else "",
                        "displayed_link": doc.find("y:displayed-url", ns).text if doc.find("y:displayed-url", ns) is not None else "",
                        "content": doc.find("y:snippet", ns).text if doc.find("y:snippet", ns) is not None else "",
                    })
                return {"results": results}
            body = await response.text()
            warning(f"Yandex Search Error [{response.status}] body={body}")
            response.raise_for_status()
    raise RuntimeError("Yandex Search request failed")


async def _yandex_images_request(query: str, limit: int = 4) -> dict[str, Any]:
    import base64
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "query": {"searchType": YANDEX_SEARCH_TYPE, "queryText": query},
        "folderId": YANDEX_FOLDER_ID,
        "docsOnPage": limit,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            YANDEX_IMAGES_URL, headers=headers, json=payload
        ) as response:
            if response.status == 200:
                result = await response.json()
                xml_data = base64.b64decode(result.get("rawData", ""))
                from xml.etree import ElementTree as ET
                root = ET.fromstring(xml_data)
                ns = {"y": "http://www.yandex.ru/searchapi"}
                images = []
                for doc in root.findall(".//y:doc", ns)[:limit]:
                    image_props = doc.find("y:image/y:properties", ns)
                    if image_props is not None:
                        images.append({
                            "url": image_props.find("y:image-url", ns).text if image_props.find("y:image-url", ns) is not None else "",
                            "thumbnail": image_props.find("y:thumbnail-url", ns).text if image_props.find("y:thumbnail-url", ns) is not None else "",
                            "description": doc.find("y:title", ns).text if doc.find("y:title", ns) is not None else query,
                        })
                return {"results": images}
            body = await response.text()
            warning(f"Yandex Images Error [{response.status}] body={body}")
            response.raise_for_status()
    raise RuntimeError("Yandex Images request failed")


# ── Tavily helpers ─────────────────────────────────────────────────────────────


async def _tavily_request(idx: int, params: dict) -> dict[str, Any]:
    headers = {"Content-Type": "application/json", "User-Agent": FAKE_UA.random}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            TAVILY_API_URL, headers=headers, json=params
        ) as response:
            if response.status == 200:
                return await response.json()
            body = await response.text()
            if response.status == 429:
                await asyncio.sleep(MAX_RETRY_INTERVAL)
            else:
                await asyncio.sleep(RETRY_TIMES)
            warning(f"TAVILY Error [{idx:02d}] [{response.status}] body={body}")
            response.raise_for_status()
    raise RuntimeError("TAVILY request failed after retries")


async def _tavily_search(**kwargs) -> dict[str, Any]:
    last_error = None
    for idx, api_key in enumerate(TAVILY_KEYS, start=1):
        try:
            params = {**kwargs, "api_key": api_key}
            return await _tavily_request(idx, params)
        except Exception as e:
            warning(f"TAVILY search error with key {api_key[:16]}...: {e}")
            last_error = e
    raise RuntimeError(
        f"TAVILY search failed after {len(TAVILY_KEYS)} retries"
    ) from last_error


# ── Search tools (only one backend registered) ────────────────────────────────

if YANDEX_API_KEY and YANDEX_FOLDER_ID:

    @mcp.tool()
    async def search_web(
        query: str,
        max_results: int = 3,
        time_range: Literal["month", "year"] | None = None,
    ) -> dict:
        """
        Search the web via Yandex Search API

        Args:
            query: Search keywords
            max_results: Maximum number of search results, default 3
            time_range: Time range filter (not supported by Yandex, kept for API compatibility)

        Returns:
            dict: with fields:
                - query: the search query
                - total_results: number of results returned
                - results: list of dicts with title, url, displayed_link, content
        """
        debug(f"search_web via Yandex query={query!r}")
        result = await _yandex_search_request(query, limit=max_results)
        results = [
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "displayed_link": item.get("domain", ""),
                "content": item.get("snippet", ""),
            }
            for item in result.get("results", [])
        ]
        return {"query": query, "total_results": len(results), "results": results}

    @mcp.tool()
    async def search_images(query: str) -> dict:
        """
        Search for web images via Yandex Search API

        Returns:
            dict: with fields:
                - query: the search query
                - total_results: number of results returned
                - images: list of dicts with url, thumbnail, description
        """
        debug(f"search_images via Yandex query={query!r}")
        result = await _yandex_images_request(query, limit=4)
        images = [
            {
                "url": item.get("image", {}).get("url", ""),
                "thumbnail": item.get("preview", {}).get("url", ""),
                "description": item.get("title", query),
            }
            for item in result.get("results", [])
        ]
        return {"query": query, "total_results": len(images), "images": images}

elif len(TAVILY_KEYS):

    @mcp.tool()
    async def search_web(
        query: str,
        max_results: int = 3,
        time_range: Literal["month", "year"] | None = None,
    ) -> dict:
        """
        Search the web via Tavily

        Args:
            query: Search keywords
            max_results: Maximum number of search results, default 3
            time_range: Time range filter, "month", "year", or None

        Returns:
            dict: with fields:
                - query: the search query
                - total_results: number of results returned
                - results: list of dicts with url, content
        """
        debug(f"search_web via Tavily query={query!r}")
        kwargs: dict[str, Any] = {
            "query": query,
            "max_results": max_results,
            "include_images": False,
        }
        if time_range:
            kwargs["time_range"] = time_range

        result = await _tavily_search(**kwargs)
        results = [
            {"url": item["url"], "content": item["content"]}
            for item in result.get("results", [])
        ]
        return {"query": query, "total_results": len(results), "results": results}

    @mcp.tool()
    async def search_images(query: str) -> dict:
        """
        Search for web images via Tavily

        Returns:
            dict: with fields:
                - query: the search query
                - total_results: number of results returned
                - images: list of dicts with url, description
        """
        debug(f"search_images via Tavily query={query!r}")
        result = await _tavily_search(
            include_image_descriptions=True,
        )
        images = [
            {"url": img["url"], "description": img["description"]}
            for img in result.get("images", [])
        ]
        return {"query": query, "total_results": len(images), "images": images}


# ── Other tools ───────────────────────────────────────────────────────────────


@mcp.tool()
async def fetch_url(url: str, body_only: bool = True) -> str:
    """
    Fetch web page content

    Args:
        url: Target URL
        body_only: If True, return only main content; otherwise return full page, default True
    """

    async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
        try:
            resp = await client.head(url)

            # Some servers may return error on HEAD; fall back to GET
            if resp.status_code >= 400:
                resp = await client.get(url, stream=True)

            content_type = resp.headers.get("Content-Type", "").lower()
            content_dispo = resp.headers.get("Content-Disposition", "").lower()

            if "attachment" in content_dispo or "filename=" in content_dispo:
                return f"URL {url} is a downloadable file (Content-Disposition: {content_dispo})"

            if not content_type.startswith("text/html"):
                return f"URL {url} returned {content_type}, not a web page"

        # Do not block Playwright: ignore errors from httpx for banned/blocked HEAD requests
        except Exception:
            pass

    async with PlaywrightConverter() as converter:
        try:
            await converter.page.goto(
                url, wait_until="domcontentloaded", timeout=MCP_CALL_TIMEOUT // 2 * 1000
            )
            html = await converter.page.content()
        except TimeoutError:
            return f"Timeout when loading URL: {url}"
        except Exception as e:
            return f"Failed to load URL {url}: {e}"

    markdown = markdownify.markdownify(html, heading_style=markdownify.ATX)
    markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip()
    if body_only:
        result = extract(
            html,
            output_format="markdown",
            with_metadata=True,
            include_links=True,
            include_images=True,
            include_tables=True,
        )
        return result or markdown

    return markdown


@mcp.tool()
async def download_file(url: str, output_file: str) -> str:
    """
    Download a file from a URL and save it to a local path.
    """
    workspace = Path(os.getcwd())
    output_path = Path(output_file).resolve()
    assert output_path.is_relative_to(workspace), (
        f"Access denied: path outside allowed workspace: {workspace}"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    suffix = Path(output_path).suffix.lower()
    ext_format_map = Image.registered_extensions()
    for retry in range(RETRY_TIMES):
        try:
            await asyncio.sleep(retry)
            async with httpx.AsyncClient(
                headers={"User-Agent": FAKE_UA.random},
                follow_redirects=True,
                verify=False,
            ) as client:
                async with client.stream("GET", url) as response:
                    response.raise_for_status()
                    data = await response.aread()
            try:
                with Image.open(BytesIO(data)) as img:
                    img.load()
                    save_format = ext_format_map.get(suffix, img.format)
                    note = ""
                    if img.format == "WEBP" or suffix == ".webp":
                        output_path = output_path.with_suffix(".png")
                        save_format = "PNG"
                        note = " (converted from WEBP to PNG)"
                    img.save(output_path, format=save_format)
                    width, height = img.size
                    return f"File downloaded to {output_path} (resolution: {width}x{height}){note}"
            except Exception:
                with open(output_path, "wb") as f:
                    f.write(data)
            break
        except Exception:
            pass
    else:
        return f"Failed to download file from {url}"

    return f"File downloaded to {output_path}"


if __name__ == "__main__":
    work_dir = Path(os.environ["WORKSPACE"])
    assert work_dir.exists(), f"Workspace {work_dir} does not exist."
    os.chdir(work_dir)
    set_logger(f"search-{work_dir.stem}", work_dir / ".history" / "search.log")

    mcp.run(show_banner=False)
