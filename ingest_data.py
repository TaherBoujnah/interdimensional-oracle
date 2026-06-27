import requests
import json
import os

BASE_URL = "https://rickandmortyapi.com/api"
ENDPOINTS = ["character", "location", "episode"]
DATA_DIR = "data"

def fetch_all_data(endpoint):
    """Fetches all paginated data for a given endpoint."""
    all_results = []
    url = f"{BASE_URL}/{endpoint}"
    
    print(f"Fetching {endpoint.capitalize()}s...")
    
    while url:
        response = requests.get(url).json()
        all_results.extend(response.get("results", []))
        url = response.get("info", {}).get("next")
        
    return all_results

def main():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    for endpoint in ENDPOINTS:
        data = fetch_all_data(endpoint)
        file_path = os.path.join(DATA_DIR, f"{endpoint}s.json")
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print(f"Saved {len(data)} {endpoint}s to {file_path}")

if __name__ == "__main__":
    main()