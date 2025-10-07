import requests
import pandas as pd
import time
import random
from datetime import datetime
import os

def scrape_grailed(brand, category, style=None, listing_type="active"):
    """Scrape Grailed listings for a specific brand, category, and optional style/model."""
    
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "content-type": "application/x-www-form-urlencoded",
        "x-algolia-api-key": "bc9ee1c014521ccf312525a4ef324a16",
        "x-algolia-application-id": "MNRWEFSS2Q",
    }

    index = "Listing_by_heat_production" if listing_type == "active" else "Listing_sold_production"
    results = []
    page = 0

    while True:
        query_param = f"&query={requests.utils.quote(style)}" if style else ""
        payload = {
            "requests": [{
                "indexName": index,
                "params": (
                    "analytics=true&clickAnalytics=true&enableABTest=false"
                    f"&facetFilters=%5B%5B%22designers.name%3A{brand}%22%2C%22category_path%3A{category}%22%5D%5D"
                    f"{query_param}&hitsPerPage=40&page={page}"
                )
            }]
        }

        response = requests.post(
            "https://mnrwefss2q-dsn.algolia.net/1/indexes/*/queries",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            print(f"Request failed on page {page}: {response.status_code}")
            break

        data = response.json()
        hits = data["results"][0].get("hits", [])

        if not hits:
            print(f"No more {listing_type} listings found for {brand} {category} ({style}) at page {page}.")
            break

        print(f"Page {page}: {len(hits)} {listing_type} listings scraped for {brand} {category} ({style})")

        for item in hits:
            listing = {
                "status": listing_type,
                "brand": brand,
                "category": category,
                "style": style,
                "title": item.get("title"),
                "price": item.get("price_i"),
                "currency": "USD",
                "size": item.get("size"),
                "condition": item.get("condition"),
                "color": item.get("color"),
                "url": f"https://www.grailed.com/listings/{item.get('id')}",
                "image": item.get("media", {}).get("thumb_url"),
                "location": (
                    item["location"].get("city") if isinstance(item.get("location"), dict)
                    else item.get("location")
                ),
                "date_scraped": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            results.append(listing)

        page += 1
        time.sleep(random.uniform(1.2, 2.3))

    return results

if __name__ == "__main__":
    #Brand, category, style
    brands = {
        "Balenciaga": {"category": "Footwear", "styles": ["3XLS", "Venom Boots"]},
        "Dior Homme": {"category": "Jeans", "styles": ["Strip", "strip"]},
        "Enfants Riches Deprimes": {"category": "T-Shirts", "styles": None}  # None scrapes all
    }

    all_listings = []

    #Loop through each brand, category, and style
    for brand, info in brands.items():
        category = info["category"]
        styles = info.get("styles")
        if styles:
            for style in styles:
                all_listings.extend(scrape_grailed(brand, category, style, "active"))
                all_listings.extend(scrape_grailed(brand, category, style, "sold"))
        else:
            all_listings.extend(scrape_grailed(brand, category, None, "active"))
            all_listings.extend(scrape_grailed(brand, category, None, "sold"))

    #Save to csv
    filename = "grailed_listings.csv"
    if all_listings:
        df = pd.DataFrame(all_listings)
        if os.path.exists(filename):
            existing_df = pd.read_csv(filename)
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df.to_csv(filename, index=False, encoding="utf-8-sig")
            print(f"\nAppended {len(df)} new listings to existing '{filename}' file.")
        else:
            df.to_csv(filename, index=False, encoding="utf-8-sig")
            print(f"\nCreated '{filename}' and saved {len(df)} listings.")
    else:
        print("No data collected.")
