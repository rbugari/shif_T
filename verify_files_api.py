import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "apps", "api"))

try:
    from apps.api.services.persistence_service import PersistenceService
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def run_local_test():
    project_id = "01416b6a-4af6-41c0-b805-3765176faf6d" # base
    print(f"Scanning Files for {project_id}...")
    
    files = PersistenceService.get_project_files(project_id)
    
    print(f"\n--- FILE STRUCTURE ({type(files)}) ---")
    
    def print_tree(nodes, depth=0):
        for node in nodes:
            print("  " * depth + f"- {node['name']} ({node['type']})")
            if "children" in node:
                print_tree(node["children"], depth + 1)

    if isinstance(files, list):
        print_tree(files)
    else:
        print("ERROR: Expected list, got dict")
        print(files)

if __name__ == "__main__":
    run_local_test()
