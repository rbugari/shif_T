import requests
import json
import os

API_URL = "http://localhost:8000/refine/start"
PROJECT_ID = "01416b6a-4af6-41c0-b805-3765176faf6d" # Project 'base'

payload = {
    "project_id": PROJECT_ID
}

print(f"Triggering Phase 3 Refinement for {PROJECT_ID}...")
try:
    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        data = response.json()
        print("\n--- STATUS: " + data.get("status", "UNKNOWN") + " ---")
        print("\n--- LOGS ---")
        for line in data.get("log", []):
            print(line)
        
        print("\n--- ARTIFACTS ---")
        refined_files = data.get("artifacts", {}).get("refined_files", {})
        for layer, files in refined_files.items():
            print(f"{layer.upper()}: {len(files)} files")
            for f in files[:3]: # Show first 3 only
                print(f"  - {os.path.basename(f)}")
            if len(files) > 3:
                print("  ... and more")
                
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"Request failed: {e}")
