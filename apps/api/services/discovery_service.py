import os
import re
import json
from typing import List, Dict, Any
from .persistence_service import PersistenceService
from .drivers.base_driver import IBaseDriver
from .drivers.ssis_driver import SSISDriver
from .drivers.sql_driver import SQLDriver

class DiscoveryService:
    # Initialize Drivers
    drivers: List[IBaseDriver] = [
        SSISDriver(),
        SQLDriver()
    ]



    @staticmethod
    def generate_manifest(project_id: str) -> Dict[str, Any]:
        """
        Generates a comprehensive 'Triage Manifest' for Agent A.
        Includes structure, snippets of logic, and detected invocations.
        Uses Pluggable Drivers for technology-specific analysis.
        """
        project_path = PersistenceService.ensure_solution_dir(project_id)
        
        inventory = []
        tech_counts = {}
        active_drivers = set()
        
        # 1. Deep Scan - RESTRICTED TO TRIAGE/SOURCE FOLDER
        triage_path = os.path.join(project_path, PersistenceService.STAGE_TRIAGE)
        print(f"DEBUG: Scanning strictly: {triage_path}")
        
        if not os.path.exists(triage_path):
             print(f"DEBUG: Triage folder NOT found at {triage_path}. Returning empty.")
             pass 

        for root, dirs, files in os.walk(triage_path):
            if '.git' in dirs: dirs.remove('.git')
            if '__pycache__' in dirs: dirs.remove('__pycache__')
            if PersistenceService.STAGE_DRAFTING in dirs: dirs.remove(PersistenceService.STAGE_DRAFTING)
            if PersistenceService.STAGE_REFINEMENT in dirs: dirs.remove(PersistenceService.STAGE_REFINEMENT)

            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, project_path).replace("\\", "/")
                
                # Basic Classification
                ext = file.split('.')[-1].lower() if '.' in file else 'no_ext'
                tech_counts[ext] = tech_counts.get(ext, 0) + 1
                
                # Deep Content Analysis via Drivers
                analysis = DiscoveryService._analyze_file_content(full_path, ext)
                if analysis.get("_driver_used"):
                    active_drivers.add(analysis["_driver_used"])
                
                print(f"DEBUG_SCAN: Adding file {rel_path} (Type: {ext})")  # <--- DEBUG PRINT

                inventory.append({
                    "path": rel_path,
                    "name": file,
                    "type": DiscoveryService._map_extension_to_type(ext),
                    "size": os.path.getsize(full_path),
                    "signatures": analysis["signatures"],
                    "invocations": analysis["invocations"],
                    "snippet": analysis["snippet"], 
                    "metadata": analysis.get("metadata", {})
                })
        
        print(f"DEBUG_SCAN: Total files found in inventory: {len(inventory)}")

        # 2. Construct Manifest
        return {
            "project_id": project_id,
            "root_path": project_path,
            "tech_stats": tech_counts,
            "file_inventory": inventory
        }

    @staticmethod
    def _map_extension_to_type(ext: str) -> str:
        if ext == 'dtsx': return 'SSIS_PACKAGE'
        if ext == 'sql': return 'SQL_SCRIPT'
        if ext == 'py': return 'PYTHON_SCRIPT'
        if ext == 'ipynb': return 'NOTEBOOK'
        if ext in ['json', 'xml', 'config', 'yaml', 'yml']: return 'CONFIG'
        return 'OTHER'

    @staticmethod
    def _analyze_file_content(file_path: str, ext: str) -> Dict[str, Any]:
        """Reads file, extracts snippets, and delegates to Drivers if available."""
        signatures = []
        invocations = []
        snippet_lines = []
        metadata = {}
        
        # Skip binary or huge files
        if ext in ['exe', 'dll', 'png', 'jpg', 'zip']:
            return {"signatures": [], "invocations": [], "snippet": "[BINARY FILE]", "metadata": {}}

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content_str = f.read()
                
                # Snippet (first 20 lines)
                lines = content_str.splitlines()
                snippet_lines = lines[:20] 
                
                # --- PLUGGABLE DRIVER LOGIC ---
                driver_handled = False
                driver_name = None
                for driver in DiscoveryService.drivers:
                    if driver.can_handle(ext):
                        try:
                            result = driver.analyze_content(file_path, content_str)
                            signatures.extend(result.get("signatures", []))
                            invocations.extend(result.get("invocations", []))
                            metadata.update(result.get("metadata", {}))
                            driver_handled = True
                            driver_name = driver.__class__.__name__
                            break 
                        except Exception as driver_err:
                            signatures.append(f"Driver {driver.__class__.__name__} Error: {str(driver_err)}")

                # --- FALLBACK LOGIC IF NO DRIVER ---
                if not driver_handled:
                    # Generic Python scan
                    if ext == 'py':
                        if 'pyspark' in content_str: signatures.append("PySpark")
                        if 'pandas' in content_str: signatures.append("Pandas")
                        if 'os.system' in content_str: invocations.append("System Call (os.system)")

        except Exception as e:
            snippet_lines = [f"Error reading file: {str(e)}"]

        return {
            "signatures": signatures,
            "invocations": list(set(invocations)), # unique
            "snippet": "\n".join(snippet_lines),
            "metadata": metadata,
            "_driver_used": driver_name
        }
    
    @staticmethod
    def scan_project(project_id: str) -> Dict[str, Any]:
        """Legacy wrapper: returns the simple assets list expected by frontend initially."""
        manifest = DiscoveryService.generate_manifest(project_id)
        # Map manifest back to simple assets list
        simple_assets = []
        for item in manifest["file_inventory"]:
             simple_type = 'package' if item['type'] == 'SSIS_PACKAGE' else \
                           'script' if 'SCRIPT' in item['type'] else \
                           'config' if 'CONFIG' in item['type'] else 'unused'
             
             status = 'connected' if item['invocations'] else 'pending'
             
             simple_assets.append({
                 "id": item["path"],
                 "name": item["name"],
                 "type": simple_type,
                 "status": status,
                 "tags": item["signatures"],
                 "path": item["path"],
                 "dependencies": [] # populated by Agent A now
             })
             
        return {"assets": simple_assets}
