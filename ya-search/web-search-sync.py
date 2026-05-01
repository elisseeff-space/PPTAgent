#!/usr/bin/env python3
        
from __future__ import annotations
from typing import Literal, cast

import os

from dotenv import load_dotenv
from yandex_ai_studio_sdk import AIStudio

load_dotenv()
from yandex_ai_studio_sdk.search_api import (
    FamilyMode,
    FixTypoMode,
    GroupMode,
    Localization,
    SearchType,
    SortMode,
    SortOrder,
)

import pathlib

USER_AGENT = "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.112 Mobile Safari/537.36"


def main() -> None:

    sdk = AIStudio(
        folder_id=os.getenv("YANDEX_FOLDER_ID"),
        auth=os.getenv("YANDEX_AUTH"),
    )
    sdk.setup_default_logging()

    # you could pass any settings when creating the Search object
    search = sdk.search_api.web(
        "RU",
        family_mode=FamilyMode.MODERATE,
        # By default object configuration property values are set to None,
        # which corresponds to the "default" value which is
        # defined at the service's backend.
        # e.g. docs_in_group=None,
    )

    # but also you could reconfigure the Search object at any time:
    search = search.configure(
        # These are enum-type settings,
        # they could be passed as strings as shown below.
        search_type="ru",
        family_mode="strict",
        fix_typo_mode="off",
        group_mode="deep",
        localization="ru",
        sort_order="desc",
        sort_mode="by_time",
        docs_in_group=None,
        groups_on_page=6,
        max_passages=2,
        region="225",
        user_agent=USER_AGENT,
    )

    search_query = input("Enter the search query: ")
    if not search_query.strip():
        search_query = "Yandex Cloud"

    format_ = input("Choose format ([xml]/html): ")
    format_ = format_.strip() or "xml"
    assert format_.lower() in ("xml", "html")
    format_ = cast(Literal["html", "xml"], format_)

    for page in range(0, 10):
        search_result = search.run(search_query, format=format_, page=page)
        output_filename = (
            str(pathlib.Path(__file__).parent)
            + "/"
            + "page_"
            + str(page + 1)
            + "."
            + format_
        )
        file = open(output_filename, "a")
        file.write(search_result.decode("utf-8"))
        print(f"Page {page} saved to file {output_filename}")
        file.close()


if __name__ == "__main__":
    main()