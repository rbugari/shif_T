import os
import re
import json
from typing import List, Dict, Any

try:
    from apps.api.services.persistence_service import PersistenceService
except ImportError:
    try:
        from services.persistence_service import PersistenceService
    except ImportError:
        from ..persistence_service import PersistenceService

class ProfilerService:
    """
    The Global Profiler (Agent 3.1)
    Analyzes all Stage 2 output files to detect cross-package patterns, 
    shared connections, and dependency candidates.
    """

    def __init__(self):
        pass

    def analyze_codebase(self, project_id: str, log: List[str] = None) -> Dict[str, Any]:
        """
        Executes the profiling logic.
        1. Scans .py files in {project}/Output
        2. Generates Global Profile
        """
        if log is None: log = []
        
        # Resolve project path robustly
        project_path = PersistenceService.ensure_solution_dir(project_id)
        log.append(f"[Profiler] Target Project Directory: {project_path}")

        input_dir = os.path.join(project_path, "Output")
        profile_output = os.path.join(project_path, "Refined", "profile_metadata.json")

        if not os.path.exists(input_dir):
            error_msg = f"Input directory not found: {input_dir}"
            log.append(f"[Profiler] ERROR: {error_msg}")
            return {"error": error_msg, "total_files": 0}

        py_files = [f for f in os.listdir(input_dir) if f.endswith(".py")]
        log.append(f"[Profiler] Found {len(py_files)} Python files in Output.")
        
        shared_connections = {}
        bronze_candidates = {}
        
        for py_file in py_files:
            file_path = os.path.join(input_dir, py_file)
            log.append(f"[Profiler] Analyzing file: {py_file}...")
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
                # Detect JDBC URLs (Basic Heuristic)
                jdbc_matches = re.findall(r'option\("url",\s*"([^"]+)"\)', content)
                for jdbc in jdbc_matches:
                    log.append(f"[Profiler]   > Found JDBC Connection: {jdbc}")
                    if jdbc not in shared_connections:
                        shared_connections[jdbc] = []
                    shared_connections[jdbc].append(py_file)

        profile_data = {
            "analyzed_files": py_files,
            "shared_connections": shared_connections,
            "bronze_candidates": bronze_candidates,
            "total_files": len(py_files)
        }

        # Ensure output dir exists
        os.makedirs(os.path.dirname(profile_output), exist_ok=True)
        
        with open(profile_output, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, indent=4)
        
        log.append(f"[Profiler] Profile metadata saved to {profile_output}")

        return profile_data
