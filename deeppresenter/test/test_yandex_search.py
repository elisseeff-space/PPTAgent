import pytest

from deeppresenter.tools.search import (
    YANDEX_API_KEY,
    YANDEX_FOLDER_ID,
    _yandex_search_request,
    _yandex_images_request,
)


@pytest.mark.skipif(
    not YANDEX_API_KEY or not YANDEX_FOLDER_ID, reason="Yandex credentials not set"
)
@pytest.mark.asyncio
async def test_yandex_search():
    result = await _yandex_search_request("Python programming", limit=3)
    assert "results" in result
    assert len(result["results"]) > 0
    first_result = result["results"][0]
    assert "title" in first_result
    assert "url" in first_result


@pytest.mark.skipif(
    not YANDEX_API_KEY or not YANDEX_FOLDER_ID, reason="Yandex credentials not set"
)
@pytest.mark.asyncio
async def test_yandex_images():
    result = await _yandex_images_request("cat", limit=2)
    assert "results" in result
    assert len(result["results"]) > 0
    first_image = result["results"][0]
    assert "image" in first_image or "url" in first_image


@pytest.mark.asyncio
async def test_yandex_credentials_loaded():
    assert isinstance(YANDEX_API_KEY, str)
    assert isinstance(YANDEX_FOLDER_ID, str)
