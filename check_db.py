import sys
sys.path.append('apps/api')
from dotenv import load_dotenv
load_dotenv()
import asyncio
from services.persistence_service import SupabasePersistence

async def main():
    db = SupabasePersistence()
    # Try finding by name ORACLE1
    uuid = await db.get_project_id_by_name('ORACLE1')
    print(f"UUID for ORACLE1: {uuid}")
    if uuid:
        meta = await db.get_project_metadata(uuid)
        print(f"Meta: {meta}")
        
        # Check config
        config = meta.get("config", {})
        print(f"Config: {config}")
        
        # Check if source_tech is set
        print(f"source_tech: {config.get('source_tech')}")
        
    else:
        print("Project ORACLE1 not found by name")
        
    # Also check by ID 'oracle1' just in case
    meta_id = await db.get_project_metadata("oracle1") 
    print(f"Meta for ID 'oracle1': {meta_id}")

if __name__ == "__main__":
    asyncio.run(main())
