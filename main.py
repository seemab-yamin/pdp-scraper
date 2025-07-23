import sys
from utils import get_page_source, extract_script_tag_data, clean_html_source

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <URL>")
        # sys.exit(1)
        # TODO
        url = "https://www.sephora.com/product/dior-rouge-dior-lipstick-P467760?skuId=2751006"
        url = "https://www.sephora.com/product/fenty-beauty-rihanna-gloss-bomb-stix-high-shine-gloss-stick-P511572"
    else:
        url = sys.argv[1]
    source_code = get_page_source(url)
    if source_code:
        print("Successfully fetched page source.")
        with open("source_code.html", "w") as f:
            f.write(source_code)
    else:
        print("Failed to fetch page source.")
        sys.exit(1)

    script_data_list = extract_script_tag_data(source_code)
    if script_data_list:
        print(f"Number of <script> tags with content: {len(script_data_list)}")
    else:
        print("No <script> tags found with content.")

    cleaned_html = clean_html_source(source_code)
    print("\n--- Cleaned HTML Source ---")
    