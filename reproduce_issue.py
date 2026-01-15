import sys
import os

# Add project root to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'apps', 'api'))

from apps.api.services.persistence_service import PersistenceService

print(f"File location: {PersistenceService.__module__}")
print(f"Has ensure_solution_dir: {hasattr(PersistenceService, 'ensure_solution_dir')}")
print(f"Has initialize_project_from_source: {hasattr(PersistenceService, 'initialize_project_from_source')}")

try:
    PersistenceService.initialize_project_from_source("test_check", "source_check")
    print("Method execution attempted (it might fail on logic inside, but method exists)")
except TypeError:
    print("Method exists but signature might be wrong")
except AttributeError:
    print("CRITICAL: Method DOES NOT exist on class")
except Exception as e:
    print(f"Method exists, failed with: {e}")
