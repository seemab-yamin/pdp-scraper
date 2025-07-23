import requests
from lxml import etree

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
  tags_to_remove = ['script', 'iframe', 'style', 'svg', 'header', 'nav', 'footer']

  # Iterate through the tags to remove and remove them from the tree
  for tag in tags_to_remove:
      # Use XPath to find all instances of the tag
      elements_to_remove = tree.xpath(f'//{tag}')
      for element in elements_to_remove:
          # Remove the element from its parent
          element.getparent().remove(element)

  # Serialize the modified tree back to a string (raw HTML)
  cleaned_html = etree.tostring(tree, encoding='unicode', method='html')

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
  script_contents = tree.xpath('//script/text()')

  return script_contents

def get_page_source(url):
  """Fetches the source code of a webpage.

  Args:
    url: The URL of the webpage.

  Returns:
    The source code of the webpage as a string, or None if an error occurs.
  """
  headers = {
  'accept-language': 'en-GB,en;q=0.9,ur-PK;q=0.8,ur;q=0.7,en-US;q=0.6',
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
  'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"macOS"',
  'sec-fetch-dest': 'document',
  }

  try:
    response = requests.get(url, headers=headers, timeout=10)  # Set a timeout to prevent hanging
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    return response.text
  except requests.exceptions.RequestException as e:
    print(f"Error fetching page from {url}: {e}")
    return None
  except Exception as e:
    print(f"An unexpected error occurred: {e}")
    return None
