import requests
import re
from urllib.parse import urlparse
import os
import json
from lxml import etree
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
assert os.getenv("GOOGLE_API_KEY") is not None, "GOOGLE_API_KEY is not set"


def construct_outfile_name(url):
    # Parse the URL
    parsed = urlparse(url)
    # Remove query string and fragment
    path = parsed.path
    # Remove leading/trailing slashes
    path = path.strip("/")
    # Split path into parts, filter out empty, domain, and category-like segments
    parts = [
        p
        for p in path.split("/")
        if p
        and not re.match(
            r"^(category|categories|products?|shop|store|collections?)$", p, re.I
        )
    ]
    # If nothing left, use 'output'
    if not parts:
        filename = "output"
    else:
        filename = parts[-1]
    # Remove file extension if present
    filename = re.sub(r"\.[a-zA-Z0-9]+$", "", filename)
    # Remove non-alphanumeric characters
    filename = re.sub(r"[^a-zA-Z0-9_-]", "_", filename)
    return filename


def extract_json_from_response(text):
    # Try to extract JSON from a code block
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if match:
        json_str = match.group(1)
    else:
        # Fallback: try to find the first curly brace and parse from there
        idx = text.find("{")
        if idx != -1:
            json_str = text[idx:]
        else:
            raise ValueError("No JSON object found in response text.")

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        with open("failed_json_str.txt", "w", encoding="utf-8") as f:
            f.write(json_str)
        return None


def extract_product_data(script_data, llm_model="gemini-2.0-flash-lite"):
    system_instruction = """You are an expert e-commerce products data extraction assistant.
    You will be given a product details page data from script tags and you need to extract the following information:
    - Product name
    - Price (including currency)
    - SKU
    - Brand
    - Description (plain text)
    - Variants (image urls, size, color, etc.)
    - Availability status
    - Ratings
    - Reviews

    Note:
    Parse the provided script contents for embedded JSON, JavaScript variables, or data structures containing product information.
    Ignore unrelated scripts (analytics, tracking, etc.) unless they contain product data.
    Output the extracted product data as a single, well-structured JSON object.
    If multiple product variants are found, return a list of product variants.
    If any value contains HTML tags, clean it and provide plain and clean text value.
    Clean all the values from having trash values like \u00a0.
    
    The output will be a structured JSON:
    {
        "name": "...",
        "brand": "brand or manufacturer",
        "description": "plain text string",
        "variants": [
            {"size": "...", "color": "...", "price": "...", "currency": "...", "sku": "...", "images": ["...", "..."]}
        ],
        "availability": "Boolean value",
        "rating": "rating in float type",
        "reviews_count": "reviews count in integer type",
    }"""

    model = genai.GenerativeModel(
        "gemini-2.0-flash-lite", system_instruction=system_instruction
    )
    model.temperature = 0.3
    user_prompt = (
        "Raw Input:\n" + script_data + "\n\n"
        "Please extract the product data as described above and output ONLY a single, well-structured JSON object as your response. "
        "Do not include any explanation or extra text. The output must be valid JSON."
    )
    print(f"Sending prompt to model '{llm_model}'")
    response = model.generate_content(user_prompt)
    usage = response.usage_metadata
    print(f"Token usage metrics:")
    print(f"  Cached content token count: {usage.cached_content_token_count}")
    print(f"  Candidates token count:     {usage.candidates_token_count}")
    print(f"  Total token count:          {usage.total_token_count}")
    print(f"  Prompt token count:         {usage.prompt_token_count}")
    return extract_json_from_response(response.text)


def clean_html_source(html_source):
    """Cleans the HTML source by removing specified tags.

    Args:
      html_source: The HTML source code as a string.

    Returns:
      A string containing the cleaned HTML with specified tags removed.
    """
    if not html_source:
        return ""

    parser = etree.HTMLParser()
    tree = etree.fromstring(html_source, parser)

    # List of tags to remove
    tags_to_remove = ["script", "iframe", "style", "svg", "header", "nav", "footer"]

    # Iterate through the tags to remove and remove them from the tree
    for tag in tags_to_remove:
        # Use XPath to find all instances of the tag
        elements_to_remove = tree.xpath(f"//{tag}")
        for element in elements_to_remove:
            # Remove the element from its parent
            element.getparent().remove(element)

    # Serialize the modified tree back to a string (raw HTML)
    cleaned_html = etree.tostring(tree, encoding="unicode", method="html")

    return cleaned_html


def extract_script_tag_data(html_source):
    """Extracts the content of all <script> tags from HTML source using etree and XPath.

    Args:
      html_source: The HTML source code as a string.

    Returns:
      A list of strings, where each string is the content of a <script> tag.
    """
    if not html_source:
        return []

    parser = etree.HTMLParser()
    tree = etree.fromstring(html_source, parser)

    # XPath to select the content of all <script> tags
    script_contents = tree.xpath("//script/text()")

    return script_contents


def get_page_source(url):
    """Fetches the source code of a webpage.

    Args:
      url: The URL of the webpage.

    Returns:
      The source code of the webpage as a string, or None if an error occurs.
    """
    headers = {
        "accept-language": "en-GB,en;q=0.9,ur-PK;q=0.8,ur;q=0.7,en-US;q=0.6",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "document",
    }

    try:
        response = requests.get(
            url, headers=headers, timeout=10
        )  # Set a timeout to prevent hanging
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page from {url}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
