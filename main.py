import requests
import pandas as pd
import re

def extract_make_model_year(title): 
    match = re.match(r"(?P<make>\w+)\s+(?P<model>[A-Za-z0-9\-]+)?\s+(?P<year>\d{4})?", title)
    if match:
        return match.group("make"), match.group("model"), match.group("year")
    return None, None, None

# def extract_condition(title):
#     title_lower = title.lower()
#     if "foreign used" in title_lower:
#         return "foreign used"
#     elif "nigerian used" in title_lower or "local used" in title_lower:
#         return "local used"
#     elif "brand new" in title_lower or "new" in title_lower:
#         return "new"
#     return "unknown"
def extract_condition(condition):
    condition_lower = condition.lower()
    if "foreign used" in condition_lower:
        return "foreign used"
    elif "nigerian used" in condition_lower or "local used" in condition_lower:
        return "local used"
    elif "brand new" in condition_lower or "new" in condition_lower:
        return "new"
    return "unknown"


def extract_transmission(transmission):
    transmission_lower = transmission.lower()
    if "automatic" in transmission_lower:
        return "automatic"
    elif "manual" in transmission_lower:
        return "manual"
    return "unknown"

def fetch_json_data(page):
    url = "https://jiji.ng/api_web/v1/listing"
    params = {
        "slug": "cars",
        "page": page,
        "webp": "true"
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"[Page {page}] Request error: {e}")
        return []
    except ValueError:
        print(f"[Page {page}] Failed to decode JSON. Response text:")
        print(response.text[:500])
        return []

    adverts = data.get("adverts_list", {}).get("adverts", [])
    if not isinstance(adverts, list):
        print(f"[Page {page}] Expected a list, got {type(adverts)}. Full response:")
        print(data)
        return []

    return adverts

def get_attr_value(attrs, key_name):
    for attr in attrs:
        if attr.get("name", "").lower() == key_name.lower():
            return attr.get("value", "").strip()
    return "unknown"

def main():
    all_ads = []

    for page in range(1, 100):
        ads = fetch_json_data(page)
        print(f"Page {page}: {len(ads)} ads found")

        for ad in ads:
            if isinstance(ad, dict):
                attrs = ad.get("attrs", [])
                title = ad.get("title", "")
                condition_ = get_attr_value(attrs, "Condition")
                transmission_ = get_attr_value(attrs, "Transmission")
                make, model, year = extract_make_model_year(title)
                condition = extract_condition(condition_)
                transmission = extract_transmission(transmission_)
                # price = ad.get("price_title", {}).get("value", None)
                price = ad.get("price_title", "")
                location = ad.get("region_name", "")

                if price:  # Only include if price is present
                    all_ads.append({
                        "title": title,
                        "make": make,
                        "model": model,
                        "year": year,
                        "condition": condition,
                        "transmission": transmission,
                        "location": location,
                        "price": price
                    })

    if all_ads:
        df = pd.DataFrame(all_ads)
        df.to_csv("jiji_car_data_refined.csv", index=False)
        print("Scraping complete. Data saved to 'jiji_car_data_refined.csv'")
    else:
        print("No ads scraped.")

if __name__ == "__main__":
    main()



