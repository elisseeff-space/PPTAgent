#!/usr/bin/env python3

from __future__ import annotations

import os
import pathlib

from dotenv import load_dotenv
from yandex_ai_studio_sdk import AIStudio
from yandex_ai_studio_sdk.search_api import FamilyMode

load_dotenv()

EXAMPLE_FILE = pathlib.Path(__file__).parent / "image.jpg"


def main() -> None:
    sdk = AIStudio(
        folder_id=os.getenv("YANDEX_FOLDER_ID"),
        auth=os.getenv("YANDEX_AUTH"),
    )
    sdk.setup_default_logging()

    # You can pass initial configuration here:
    search = sdk.search_api.by_image(
        family_mode="moderate",
        site="ya.ru",
    )
    # Or configure the Search object later:
    search = search.configure(
        # family mode may be passed as a string or as a special enum value
        family_mode=FamilyMode.NONE,
    )

    # You can reset any config property back to its default value by passing None:
    search = search.configure(site=None)

    search_type = input(
        "Select a search type:\n1 — using a remote image URL (default)\n2 — using bytes data from './image.jpeg'\n\n"
    )
    if not search_type.strip():
        search_type = "1"

    if int(search_type) == 2:

        # The first search option is to search using bytes data:
        image_data = pathlib.Path(EXAMPLE_FILE).read_bytes()
        search_result = search.run(image_data)

    else:

        # The second search option is to search using a remote image url:
        # e.g. Photo of Leo Tolstoy
        url = "https://upload.wikimedia.org/wikipedia/commons/b/be/Leo_Tolstoy_1908_Portrait_%283x4_cropped%29.jpg"
        search_result = search.run_from_url(url)

    # You can examine the search_result structure via pprint
    # to get to know how to work with it:
    # pprint.pprint(search_result)
    # Search results can also be used in boolean context:
    if search_result:
        print(f"{len(search_result)} documents found")
    else:
        print("Nothing found")

    # The third search option is to search using the image's CBIR ID:
    # using CBIR ID is way faster than any other option,
    # but it requires to make at least one "heavy" request to get this ID.

    cbid_id = search_result.cbir_id
    search_result = search.run_from_id(cbid_id, page=1)

    while search_result:
        print(f"Page {search_result.page}:")
        output_filename = (
            str(pathlib.Path(__file__).parent)
            + "/"
            + "results_page_"
            + str(search_result.page)
            + ".txt"
        )
        file = open(output_filename, "a")
        for document in search_result:
            file.write(str(document) + "\n\n")
        print(f"Page {search_result.page} saved to file {output_filename}")
        file.close()

        # search_result.next_page() is a shortcut for
        # `.run_from_id(search_query.cbir_id, page=page + 1)`
        # with search configuration saved from the initial run;
        # last page + 1 will return an "empty" search_result;
        search_result = search_result.next_page()


if __name__ == "__main__":
    main()
