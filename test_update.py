import sys
sys.path.append('apps/api')
from dotenv import load_dotenv
load_dotenv()
import asyncio
from services.persistence_service import SupabasePersistence

async def main():
    db = SupabasePersistence()
    uuid = await db.get_project_id_by_name('ORACLE1')
    if not uuid:
        print("Project ORACLE1 not found")
        return

    print(f"Updating config for {uuid}...")
    success = await db.update_project_config(uuid, {"source_tech": "ORACLE"})
    print(f"Update Success: {success}")

    meta = await db.get_project_metadata(uuid)
    print(f"New Config: {meta.get('config')}")

if __name__ == "__main__":
    asyncio.run(main())
