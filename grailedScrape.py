import pandas as pd
import requests
import time

#
def scrape_balenciaga_items():
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9,ko-KR;q=0.8,ko;q=0.7',
        'Connection': 'keep-alive',
        'Origin': 'https://www.grailed.com',
        'Referer': 'https://www.grailed.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'x-algolia-api-key': 'bc9ee1c014521ccf312525a4ef324a16',
        'x-algolia-application-id': 'MNRWEFSS2Q',
    }

    all_items = []

    #JSON string to requests API for data
    # data = '{"requests":[{"indexName":"Listing_by_heat_production","params":"analytics=true&clickAnalytics=true&enableABTest=false&enablePersonalization=false&facetFilters=%5B%5B%22designers.name%3ABalenciaga%22%5D%5D&facets=%5B%22designers.name%22%2C%22category_path%22%2C%22department%22%2C%22category_size%22%2C%22price_i%22%2C%22condition%22%2C%22location%22%2C%22badges%22%2C%22strata%22%5D&filters=&getRankingInfo=true&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=40&maxValuesPerFacet=100&numericFilters=%5B%22price_i%3E%3D0%22%2C%22price_i%3C%3D1000000%22%5D&page=0&personalizationImpact=0&query=&tagFilters=&userToken=2538683"},{"indexName":"Listing_by_heat_production","params":"analytics=false&clickAnalytics=false&enableABTest=false&enablePersonalization=false&facets=designers.name&filters=&getRankingInfo=true&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=0&maxValuesPerFacet=100&numericFilters=%5B%22price_i%3E%3D0%22%2C%22price_i%3C%3D1000000%22%5D&page=0&personalizationImpact=0&query=&userToken=2538683"},{"indexName":"Listing_by_heat_production","params":"analytics=false&clickAnalytics=false&enableABTest=false&enablePersonalization=false&facetFilters=%5B%5B%22designers.name%3ABalenciaga%22%5D%5D&facets=price_i&filters=&getRankingInfo=true&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=0&maxValuesPerFacet=100&page=0&personalizationImpact=0&query=&userToken=2538683"}]}'
    data = '{"requests":[{"indexName":"Listing_by_heat_production","params":"facetFilters=%5B%5B%22designers.name%3ABalenciaga%22%5D%5D&hitsPerPage=40&page=0"}]}'

    #Sends POST request to Grailed's Algolia API
    response = requests.post(
        'https://mnrwefss2q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.14.3)%3B%20Browser%3B%20JS%20Helper%20(3.11.3)%3B%20react%20(18.2.0)%3B%20react-instantsearch%20(6.39.1)',
        headers=headers,
        data=data,
    )

    #if the request was successful, convert the API response into a Python dictionary
    if response.status_code == 200:
        # Parse the JSON response
        result = response.json()
        # Extract relevant data from the response
        hits = result['results'][0]['hits']
        # Return the scraped data
        return hits
    else:
        print("Failed to scrape data. Status code:", response.status_code)
        return None

# Scrape Balenciaga items
balenciaga_items = scrape_balenciaga_items()

# Convert scraped data to pandas DataFrame
if balenciaga_items:
    cleaned_data = []
    for item in balenciaga_items:
       cleaned_data.append({
            "title": item.get("title"),
            "price": item.get("price_i"),
            "currency" : "USD",
            "size": item.get("size"),
            "condition": item.get("condition"),
            "color": item.get("color"),
            "designer": item.get("designer_name"),
            "url": f"https://www.grailed.com/listings/{item.get('id')}",
            "image": item.get("media", {}).get("thumb_url"),
        })
    df = pd.DataFrame(cleaned_data)
    # Print DataFrame
    print(df.head())
    df.to_csv("balenciaga_items.csv", index=False, encoding="utf-8")
else:
    print("No data scraped for Balenciaga items.")
