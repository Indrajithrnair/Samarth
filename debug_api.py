from data_scraper import DataScraper
import requests

ds = DataScraper()
url = f"{ds.api_base}/resource/{ds.dataset_ids['crop_production']}"
params = {
    "api-key": ds.api_key,
    "format": "json", 
    "limit": 5
}

print("Testing API call...")
print(f"URL: {url}")
print(f"Params: {params}")

r = requests.get(url, params=params)
print(f"Status: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    print(f"Response keys: {list(data.keys())}")
    records = data.get('records', [])
    print(f"Records found: {len(records)}")
    if records:
        print(f"Sample record: {records[0]}")
else:
    print(f"Error: {r.text}")