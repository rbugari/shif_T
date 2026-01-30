import asyncio
import os
import json
from apps.api.services.persistence_service import SupabasePersistence
from dotenv import load_dotenv

load_dotenv()

async def diagnose_project(project_name):
    db = SupabasePersistence()
    print(f"--- Diagnostic for {project_name} ---")
    
    project_id = await db.get_project_id_by_name(project_name)
    if not project_id:
        print(f"ERROR: Project '{project_name}' not found in DB.")
        return

    print(f"Project UUID: {project_id}")
    
    # Check Metadata
    meta = await db.get_project_metadata(project_id)
    print(f"Metadata: {json.dumps(meta, indent=2)}")
    
    # Check Assets
    assets = await db.get_project_assets(project_id)
    print(f"Total Assets: {len(assets)}")
    for a in assets:
        print(f"  - {a['filename']} ({a['type']}, selected={a['selected']})")
        
    # Check Layout
    layout = await db.get_project_layout(project_id)
    if layout:
        print(f"Layout: Found ({len(layout.get('nodes', []))} nodes, {len(layout.get('edges', []))} edges)")
    else:
        print("Layout: NOT FOUND")

if __name__ == "__main__":
    import sys
    name = "Demo1"
    if len(sys.argv) > 1:
        name = sys.argv[1]
    asyncio.run(diagnose_project(name))
