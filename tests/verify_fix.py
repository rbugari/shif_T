import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add project root and apps/api to path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, "apps", "api"))

from apps.api.main import app

def test_transpile_orchestrate_call():
    client = TestClient(app)
    
    # We need a valid project ID. 
    # Try to find one or use a dummy one if we just want to verify the import error is gone.
    # The error happened inside __init__, so even a failing orchestration (due to missing files) 
    # would pass the import check.
    
    project_id = "base" # extracted from solutions directory
    
    try:
        response = client.post("/transpile/orchestrate", json={"project_id": project_id})
        
        # If we got 500, check if it's the NameError or something else.
        if response.status_code == 500:
            print(f"500 Error: {response.text}")
            assert "PersistenceService" not in response.text
        else:
             print(f"Response: {response.status_code}")
             
    except Exception as e:
        pytest.fail(f"Exception raised: {e}")

if __name__ == "__main__":
    # verification script usage
    test_transpile_orchestrate_call()
