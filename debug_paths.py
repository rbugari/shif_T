import os
import sys

# Add apps/api to path to mimic server environment
sys.path.append(os.path.join(os.getcwd(), "apps", "api"))

try:
    from services.persistence_service import PersistenceService
    print("Imported PersistenceService from services.persistence_service")
except ImportError:
    try:
        from apps.api.services.persistence_service import PersistenceService
        print("Imported PersistenceService from apps.api.services.persistence_service")
    except ImportError:
        print("Could not import PersistenceService")
        sys.exit(1)

project_id = "base"
path = PersistenceService.ensure_solution_dir(project_id)
print(f"Calculated Path for '{project_id}': {path}")
print(f"Exists? {os.path.exists(path)}")

output_path = os.path.join(path, "Output")
print(f"Output Path: {output_path}")
print(f"Output Exists? {os.path.exists(output_path)}")

if os.path.exists(output_path):
    files = os.listdir(output_path)
    print(f"Files in Output ({len(files)}): {files}")
