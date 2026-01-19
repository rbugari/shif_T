import requests
import json

API_URL = "http://localhost:8000"
PROJECT_ID = "01416b6a-4af6-41c0-b805-3765176faf6d"

def force_stage_update():
    url = f"{API_URL}/projects/{PROJECT_ID}/stage"
    payload = {"stage": "3"}
    
    print(f"Updating stage to 3 for {PROJECT_ID}...")
    try:
        res = requests.post(url, json=payload)
        if res.status_code == 200:
            print("Success! Stage updated.")
            print(res.json())
        else:
            print(f"Failed: {res.status_code}")
            print(res.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    force_stage_update()
