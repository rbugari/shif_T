import requests
import json

API_URL = "http://localhost:8000"
PROJECT_ID = "01416b6a-4af6-41c0-b805-3765176faf6d"

def check_api_stage():
    url = f"{API_URL}/projects/{PROJECT_ID}"
    print(f"Fetching project details from {url}...")
    try:
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            print("--- API RESPONSE ---")
            print(json.dumps(data, indent=2))
            
            stage = data.get("stage")
            print(f"\nDETECTED STAGE: {stage} (Type: {type(stage)})")
        else:
            print(f"Failed: {res.status_code}")
            print(res.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_api_stage()
