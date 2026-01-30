import asyncio
import os
from apps.api.services.persistence_service import SupabasePersistence
from dotenv import load_dotenv

load_dotenv()

async def test_update_config():
    db = SupabasePersistence()
    
    # Use Demo1 or a test project name
    project_name = "Demo1"
    
    # Test flat config update
    new_config = {
        "source_tech": "SSIS",
        "dest_tech": "SNOWFLAKE"
    }
    
    print(f"Testing config update for {project_name}...")
    success = await db.update_project_config(project_name, new_config)
    
    if success:
        print("Success! Config updated.")
        # Verify
        project_id = await db.get_project_id_by_name(project_name)
        res = db.client.table("projects").select("config").eq("id", project_id).execute()
        print(f"Current Config in DB: {res.data[0]['config']}")
    else:
        print("Failed to update config.")

if __name__ == "__main__":
    asyncio.run(test_update_config())
