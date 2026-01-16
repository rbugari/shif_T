import os
import json
import asyncio
from typing import Dict, Any, List

# Import all agents
from services.librarian_service import LibrarianService
from services.topology_service import TopologyService
from services.developer_service import DeveloperService
from services.compliance_service import ComplianceService

from services.persistence_service import PersistenceService, SupabasePersistence
try:
    from apps.api.utils.logger import logger
except ImportError:
    try:
        from utils.logger import logger
    except ImportError:
        from ..utils.logger import logger

class MigrationOrchestrator:
    """
    The Director: Manages the end-to-end migration lifecycle.
    Orchestrates the hand-offs between Librarian, Topology, Developer, and Compliance agents.
    """

    def __init__(self, project_id: str):
        self.project_id = project_id
        # Persistence Service should handle paths ideally, but keeping this for now
        # resolving absolute paths robustly
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # apps/api/services -> apps/api
        self.base_path = os.path.join(os.getcwd(), "solutions", project_id) # Solutions is relative to CWD usually
        self.output_path = os.path.join(self.base_path, "Output")
        
        # Load Platform Spec (Robust Path)
        self.spec_path = os.path.join(base_dir, "config", "platform_spec.json")
        try:
            with open(self.spec_path, "r") as f:
                self.platform_spec = json.load(f)
        except FileNotFoundError:
            # Fallback if base_dir calculation is off, try relative to CWD
            self.spec_path = os.path.abspath(os.path.join("apps", "api", "config", "platform_spec.json"))
            with open(self.spec_path, "r") as f:
                self.platform_spec = json.load(f)

        # Initialize Agents
        self.librarian = LibrarianService(project_id)
        self.topology = TopologyService(project_id)
        self.developer = DeveloperService()
        self.compliance = ComplianceService()
        self.persistence = SupabasePersistence()

    async def run_full_migration(self, limit: int = 0):
        """Executes the complete Shift-T loop."""
        logger.info(f"Starting Migration for {self.project_id}", "Orchestrator")
        
        # 0. Governance Check
        project_uuid = self.project_id
        
        status = await self.persistence.get_project_status(self.project_id)
        if status != "DRAFTING":
            logger.error(f"BLOCKED: Project status is '{status}'. Must be 'DRAFTING'.", "Orchestrator")
            return {
                "project_id": self.project_id,
                "error": f"Project is in {status} mode. Approve Triage first.",
                "succeeded": [],
                "failed": []
            }

        # 1. THE LIBRARIAN (Context)
        logger.info("Step 1: Librarian - Scanning Schema Context...", "Orchestrator")
        schema_ref = self.librarian.scan_project()
        logger.info(f"Found {len(schema_ref['tables'])} tables.", "Librarian")
        logger.debug("Schema Reference", "Librarian", schema_ref)

        # 2. THE TOPOLOGY ARCHITECT (Plan)
        logger.info("Step 2: Topology - Building Orchestration Plan...", "Orchestrator")
        topology_result = self.topology.build_orchestration_plan()
        orchestration = topology_result["orchestration"]
        package_metadatas = topology_result["package_metadatas"]
        
        logger.info(f"Generated DAG with {len(orchestration['dag_execution'])} phases.", "Topology")
        logger.debug("Orchestration Plan", "Topology", orchestration)

        # 3. EXECUTION LOOP (Developer + Compliance)
        logger.info("Step 3: Execution - Generating & Auditing Code...", "Orchestrator")
        
        results = {
            "project_id": self.project_id,
            "succeeded": [],
            "failed": []
        }

        # Create metadata lookup map
        metadata_map = { pm["package_name"]: pm for pm in package_metadatas }

        for phase in orchestration["dag_execution"]:
            logger.info(f"Entering Phase: {phase['phase']}", "Orchestrator")
            
            for pkg_name in phase["packages"]:
                if limit > 0 and len(results["succeeded"]) + len(results["failed"]) >= limit:
                    logger.warning(f"Limit Reached: Stopping after {limit} packages.", "Orchestrator")
                    break
                
                logger.info(f"Processing: {pkg_name}", "Orchestrator")
                
                # A. Prepare Task Context
                pm = metadata_map.get(pkg_name, {})
                task_def = {
                    "package_name": pkg_name,
                    "inputs": pm.get("inputs", []),
                    "outputs": pm.get("outputs", []),
                    "lookups": pm.get("lookups", [])
                }
                
                # B. DEVELOPER (Write)
                code_result = await self.developer.generate_code(task_def, self.platform_spec, schema_ref)
                notebook_content = code_result.get("notebook_content", "")
                
                if not notebook_content:
                    logger.error(f"Developer failed to generate code for {pkg_name}", "Orchestrator")
                    results["failed"].append({"package": pkg_name, "reason": "Empty code response"})
                    continue

                # C. COMPLIANCE (Audit)
                audit_report = await self.compliance.audit_code(notebook_content, self.platform_spec)
                
                status = audit_report.get("status", "UNKNOWN")
                logger.info(f"Audit Status: {status} (Score: {audit_report.get('score', 0)})", "Compliance")
                
                # Save Artifacts
                clean_name = pkg_name.replace(".dtsx", "")
                self._save_artifact(f"{clean_name}.py", notebook_content)
                self._save_artifact(f"{clean_name}_audit.json", json.dumps(audit_report, indent=2))
                
                if status == "APPROVED":
                    results["succeeded"].append(pkg_name)
                else:
                    results["failed"].append({
                        "package": pkg_name, 
                        "reason": "Audit Rejected", 
                        "violations": audit_report.get("violations")
                    })

        logger.info(f"Migration Complete. Succeeded: {len(results['succeeded'])}, Failed: {len(results['failed'])}", "Orchestrator")
        return results

    def _save_artifact(self, filename: str, content: str):
        path = os.path.join(self.output_path, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
