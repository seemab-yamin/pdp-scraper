# pdp-scraper
A generic Product Details Page(PDP) Scraper to scrape all page variants from any PDP. 

## Test Product Pages:
- https://www.sephora.com/product/nudestix-mini-beachy-nudes-3pc-kit-P482053
- https://www.sephora.com/product/fenty-beauty-rihanna-gloss-bomb-stix-high-shine-gloss-stick-P511572
- https://www.ulta.com/p/macximal-sleek-satin-lipstick-pimprod2047503\
- https://www.harveynichols.com/amiri/sunset-skate-panelled-suede-sneakers-24401-crem-alabaster-birch-210193/
- https://www.spacenk.com/uk/makeup/lips/lipstick/insanely-saturated-lip-colour-MUK200048934.html


## Prompt Designing:
### System Prompt
You are an expert e-commerce products data extraction assistant.
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
}

### User Prompt
Raw Input:\n
{{script_data}}
\n\n
Please extract the product data as described above and output ONLY a single, well-structured JSON object as your response. 
Do not include any explanation or extra text. The output must be valid JSON.

## LLM Limitations:
- Output Token Limit is 8k approximately. Example [this](https://www.spacenk.com/uk/makeup/lips/lip-gloss/balm-dotcom-lip-balm-UK200057237.html) webpage data couldn't be processed completed because we ran out of output token and result in an incomplete output. 