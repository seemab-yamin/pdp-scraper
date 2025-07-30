import sys
import re
import json
from utils import (
    get_page_source,
    extract_script_tag_data,
    extract_product_data,
    construct_outfile_name,
)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <URL>")
        sys.exit(1)
    else:
        url = sys.argv[1]
    outfile_name = construct_outfile_name(url)
    print(f"Output file name: {outfile_name}")

    source_code = get_page_source(url)
    if source_code:
        print("Successfully fetched page source.")
        with open(f"{outfile_name}.html", "w") as f:
            f.write(source_code)
    else:
        print("Failed to fetch page source.")
        sys.exit(1)

    script_data_list = extract_script_tag_data(source_code)
    if script_data_list:
        print(f"Number of <script> tags with content: {len(script_data_list)}")
    else:
        print("No <script> tags found with content.")

    # find the largest length item from script_data_list first sort by decending order and select the first item
    script_data_list.sort(key=len, reverse=True)
    script_data = script_data_list[0]

    # write script_data to a file
    with open("script_data.txt", "w", encoding="utf-8") as f:
        f.write(script_data)

    # preprocess script_data to remove any noise data like any word that contains "seo" or "schema"
    script_data = re.sub(r"\bseo\b", "", script_data, flags=re.IGNORECASE)
    script_data = re.sub(r"\bschema\b", "", script_data, flags=re.IGNORECASE)

    # remove extra whitespace
    script_data = re.sub(r"\s+", " ", script_data)
    # remove extra newlines
    script_data = re.sub(r"\n+", "\n", script_data)

    # remove stop words
    stop_words = ["the", "and", "is", "in", "to", "a"]
    script_data = " ".join(
        word for word in script_data.split() if word.lower() not in stop_words
    )

    llm_model = "gemini-2.0-flash-lite"
    temperature = 0.3
    product_data = extract_product_data(script_data, llm_model, temperature)
    if not product_data:
        print("No product data found.")
        sys.exit(1)
    if "variants" in product_data and isinstance(product_data["variants"], list):
        print(f"Number of variants: {len(product_data['variants'])}")
    else:
        print("No variants found or variants data is not a list.")

    with open(f"{outfile_name}.json", "w", encoding="utf-8") as f:
        json.dump(product_data, f, ensure_ascii=False, indent=2)
