import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Ensure apps/api is in path to resolve 'services' imports if code uses relative style expecting specific root
sys.path.append(os.path.join(os.getcwd(), "apps", "api"))

from services.migration_orchestrator import MigrationOrchestrator
from services.persistence_service import SupabasePersistence
from utils.logger import logger

# Force Debug Mode
os.environ["DEBUG_MODE"] = "true"
logger.debug_mode = True

async def verify_debug():
    print("--- Starting Debug Verification ---")
    
    # 1. Setup Test Project (ensure DRAFTING state)
    project_name = "debug-test"
    db = SupabasePersistence()
    project_id = await db.get_or_create_project(project_name)
    print(f"Project ID: {project_id}")
    
    # Ensure Drafting state so Orchestrator runs
    await db.update_project_status(project_id, "DRAFTING")

    # 2. Run Migration (Limit 1 to avoid cost/time)
    print("Running migration with limit=1...")
    orchestrator = MigrationOrchestrator(project_id)
    
    # Mock some data if needed?
    # Ideally standard test project has data. 
    # If not, let's assume 'test23' exists or just rely on dry run
    # Actually, let's use 'test23' if it exists as it has data
    real_project_id = "test23"
    orchestrator = MigrationOrchestrator(real_project_id)
    
    # Check if we need to set drafting for test23
    await db.update_project_status(real_project_id, "DRAFTING")

    try:
        await orchestrator.run_full_migration(limit=1)
    except Exception as e:
        print(f"Orchestrator failed (expected if no files): {e}")

    print("\n--- Check Console for [DEBUG] Logs ---")

if __name__ == "__main__":
    asyncio.run(verify_debug())
