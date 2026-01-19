import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "apps", "api"))

try:
    from apps.api.services.refinement.refinement_orchestrator import RefinementOrchestrator
    # We need to ensure persistence service uses the correct path logic too, 
    # but since we updated the code on disk, importing it should work.
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def run_local_test():
    project_id = "01416b6a-4af6-41c0-b805-3765176faf6d" # base
    print(f"Running Refinement Locally for {project_id}...")
    
    orchestrator = RefinementOrchestrator()
    result = orchestrator.start_pipeline(project_id)
    
    print("\n--- LOCAL EXECUTION RESULT ---")
    print(f"Status: {result['status']}")
    print("\n--- DETAILED LOGS GENERATED ---")
    for line in result['log']:
        print(line)

if __name__ == "__main__":
    run_local_test()
