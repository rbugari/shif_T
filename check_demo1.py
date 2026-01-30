import sys
sys.path.append('apps/api')
from dotenv import load_dotenv
load_dotenv()
import asyncio
from services.persistence_service import SupabasePersistence

async def main():
    db = SupabasePersistence()
    # Check Demo1
    print("Searching for project 'Demo1'...")
    # Try case-insensitive or exact match
    res = db.client.table("projects").select("*").eq("name", "Demo1").execute()
    if not res.data:
         # Try lowercase
         res = db.client.table("projects").select("*").eq("name", "demo1").execute()
    
    if res.data:
        p = res.data[0]
        print(f"Project Found: {p['name']} (ID: {p['id']})")
        print(f"Status: {p.get('status')}")
        print(f"Config: {p.get('config')}")
    else:
        print("Project 'Demo1' NOT found.")

if __name__ == "__main__":
    asyncio.run(main())
