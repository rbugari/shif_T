
import os
import json
from .profiler_service import ProfilerService
from .architect_service import ArchitectService
from .refactoring_service import RefactoringService
from .ops_auditor_service import OpsAuditorService

try:
    from apps.api.services.persistence_service import PersistenceService
except ImportError:
    try:
        from services.persistence_service import PersistenceService
    except ImportError:
        from ..persistence_service import PersistenceService

class RefinementOrchestrator:
    """
    Orchestrates Phase 3 (Medallion Transformation).
    Sequence: Profiler -> Architect -> Refactoring -> Ops -> Workflow
    """

    def __init__(self):
        # Services are instantiated once.
        # They handle project path resolution internally/per request if needed, 
        # or we pass project_id to their methods.
        self.profiler = ProfilerService()
        self.architect = ArchitectService()
        self.refactorer = RefactoringService()
        self.ops_auditor = OpsAuditorService()

    def start_pipeline(self, project_id: str):
        log = []
        
        try:
            # 1. Profile (Agent P)
            log.append("[Profiler] Starting analysis...")
            profile_meta = self.profiler.analyze_codebase(project_id, log)
            log.append(f"[Profiler] Complete. Analyzed {profile_meta['total_files']} files.")
            
            # 2. Architect (Agent A)
            log.append("[Architect] Segmenting into Medallion Architecture (Bronze/Silver/Gold)...")
            architect_out = self.architect.refine_project(project_id, profile_meta, log)
            log.append(f"[Architect] Medallion structure created.")
            
            # 3. Refactoring (Agent R)
            log.append("[Refactoring] Applying Spark Optimizations and Security Controls...")
            refactor_out = self.refactorer.refactor_project(project_id, architect_out, log)
            log.append(f"[Refactoring] Optimized {refactor_out.get('optimized_files_count', 0)} files.")
            
            # 4. Ops Auditor (Agent O)
            log.append("[OpsAuditor] Validating operational readiness and generating DevOps assets...")
            ops_out = self.ops_auditor.audit_project(project_id, architect_out, log)
            log.append(f"[OpsAuditor] Audit result: {ops_out['status']}")
            
            log.append("[Refinement] Pipeline Complete.")

            # --- Persistence of Logs ---
            # Resolve project path robustly
            project_path = PersistenceService.ensure_solution_dir(project_id)
            
            with open(os.path.join(project_path, "refinement.log"), "w", encoding="utf-8") as f:
                f.write("\n".join(log))

            return {
                "status": "COMPLETED",
                "log": log,
                "artifacts": architect_out,
                "ops_audit": ops_out
            }
            
        except Exception as e:
            import traceback
            error_msg = f"Pipeline failed: {str(e)}\n{traceback.format_exc()}"
            log.append(error_msg)
            
            # Try to save error log too
            try:
                project_path = PersistenceService.ensure_solution_dir(project_id)
                with open(os.path.join(project_path, "refinement.log"), "w", encoding="utf-8") as f:
                    f.write("\n".join(log))
            except: 
                pass

            return {
                "status": "FAILED",
                "log": log,
                "error": str(e)
            }
