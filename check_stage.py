import os
import sys

# Add apps/api to path
sys.path.append(os.path.join(os.getcwd(), "apps", "api"))

try:
    from services.persistence_service import SupabasePersistence
    import asyncio
except ImportError:
    print("Could not import SupabasePersistence")
    sys.exit(1)

async def check_stage():
    db = SupabasePersistence()
    project_id = "01416b6a-4af6-41c0-b805-3765176faf6d"
    
    print(f"Checking stage for {project_id}...")
    try:
        data = await db.get_project_metadata(project_id)
        if data:
            print(f"Project Name: {data.get('name')}")
            print(f"Repo URL: {data.get('repo_url')}")
            print(f"Status: {data.get('status')}") # TRIAGE, DRAFTING, etc.
            
            # Stage is usually stored in 'stage' column, but get_project_metadata only selects name, repo_url, status.
            # Let's inspect the raw fetch in persistence if needed, or just modify this script to fetch all.
            res = db.client.table("projects").select("*").eq("id", project_id).execute()
            if res.data:
                full_data = res.data[0]
                print(f"FULL DATA - Stage: {full_data.get('stage')}")
        else:
            print("Project not found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_stage())
