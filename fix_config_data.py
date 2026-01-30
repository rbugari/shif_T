import asyncio
import os
from apps.api.services.persistence_service import SupabasePersistence
from dotenv import load_dotenv

load_dotenv()

async def cleanup_configs():
    db = SupabasePersistence()
    print("Scanning for corrupted configurations...")
    
    res = db.client.table("projects").select("id, config").execute()
    for p in res.data:
        config = p.get("config")
        if config and "config" in config:
            print(f"Fixing project {p['id']}...")
            nested = config.pop("config")
            # Flatten: keep top level, but fill missing from nested if any
            new_config = {**nested, **config}
            db.client.table("projects").update({"config": new_config}).eq("id", p["id"]).execute()
            print(f"  New config: {new_config}")

if __name__ == "__main__":
    asyncio.run(cleanup_configs())
