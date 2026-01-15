import os
import shutil
from typing import Dict, Any, Optional, List
from supabase import create_client, Client

class PersistenceService:
    print("LOADING PersistenceService v2 - WITH initialize_project_from_source")
    BASE_DIR = os.path.join(os.getcwd(), "solutions")

    @classmethod
    def ensure_solution_dir(cls, solution_name: str) -> str:
        """Creates a directory for the specific solution if it doesn't exist."""
        # Sanitize name
        folder_name = "".join([c if c.isalnum() else "_" for c in solution_name])
        path = os.path.join(cls.BASE_DIR, folder_name)
        os.makedirs(path, exist_ok=True)
        return path

    @classmethod
    def robust_rmtree(cls, path: str):
        """Robustly deletes a directory tree, handling read-only files (Windows .git issue)."""
        import stat

        def on_error(func, path, exc_info):
            # Check if it's a permission error (Access denied)
            if not os.access(path, os.W_OK):
                # Change to writable and retry
                os.chmod(path, stat.S_IWUSR)
                func(path)
            else:
                raise # Re-raise if it's not a permission issue

        if os.path.exists(path):
            shutil.rmtree(path, onerror=on_error)

    @classmethod
    def delete_project_directory(cls, project_id: str) -> bool:
        """Deletes the project directory from the filesystem."""
        try:
            # We assume project_id maps to folder name. If not, we might need a lookup, 
            # but for this app we enforce project_id ~ folder_name (sanitized)
            # However, ensure_solution_dir sanitizes. We should probably replicate that logic or assume robust_rmtree handles it.
            # Best effort: try to look for the folder
            
            # Simple approach: Re-sanitize just in case, or list dirs to find match. 
            # Given ensure_solution_dir implementation:
            folder_name = "".join([c if c.isalnum() else "_" for c in project_id])
            path = os.path.join(cls.BASE_DIR, folder_name)
            
            if os.path.exists(path):
                print(f"Deleting directory: {path}")
                cls.robust_rmtree(path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting directory {project_id}: {e}")
            return False

    @classmethod
    def save_transformation(cls, solution_name: str, task_name: str, code: str) -> str:
        """Saves a transpiled PySpark task to the solution directory."""
        dir_path = cls.ensure_solution_dir(solution_name)
        # Sanitize task name for filename
        filename = "".join([c if c.isalnum() else "_" for c in task_name]) + ".py"
        file_path = os.path.join(dir_path, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
            
        return file_path

    @classmethod
    def save_documentation(cls, solution_name: str, doc_name: str, content: str) -> str:
        """Saves governance/technical documentation to the solution directory."""
        dir_path = cls.ensure_solution_dir(solution_name)
        filename = doc_name + ".md"
        file_path = os.path.join(dir_path, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return file_path

    @classmethod
    def initialize_project_from_source(cls, project_id: str, source_type: str, file_path: str = None, github_url: str = None, overwrite: bool = False) -> bool:
        """Initializes a project directory from a ZIP file or GitHub Repo. Handles overwrite logic."""
        import zipfile
        import subprocess

        try:
            project_dir = cls.ensure_solution_dir(project_id)
            
            # Check if exists and handle overwrite
            if any(os.scandir(project_dir)):
                if not overwrite:
                    print(f"Error: Project directory {project_dir} is not empty and overwrite=False.")
                    return False
                
                print(f"Cleaning existing directory for {project_id} (overwrite=True)...")
                cls.robust_rmtree(project_dir)
                # Re-create the empty dir
                project_dir = cls.ensure_solution_dir(project_id)

            if source_type == "zip" and file_path:
                # Extract ZIP
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(project_dir)
                # Cleanup temporary ZIP
                if os.path.exists(file_path):
                    os.remove(file_path)
                print(f"Project {project_id} initialized from ZIP.")
                
            elif source_type == "github" and github_url:
                # Git Clone
                subprocess.run(["git", "clone", github_url, project_dir], check=True)
                print(f"Project {project_id} initialized from GitHub.")
                
            return True
        except Exception as e:
            print(f"Error initializing project: {e}")
            return False

class SupabasePersistence:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.client: Client = create_client(url, key)

    async def get_or_create_project(self, name: str) -> str:
        """Finds or creates a project by name and returns its UUID."""
        res = self.client.table("projects").select("id").eq("name", name).execute()
        if res.data:
            return res.data[0]["id"]
        
        res = self.client.table("projects").insert({"name": name, "stage": "1"}).execute()
        return res.data[0]["id"]

    async def list_projects(self) -> List[Dict[str, Any]]:
        """Returns a list of all projects."""
        res = self.client.table("projects").select("*").execute()
        return res.data if res.data else []

    async def delete_project(self, project_id: str) -> bool:
        """Deletes the project and its assets from the database."""
        try:
            # Supabase should handle cascade if configured, but let's be explicit if needed.
            # Assuming 'projects' deletion deletes related 'assets' via FK cascade.
            self.client.table("projects").delete().eq("id", project_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting project {project_id} from DB: {e}")
            return False

    async def get_project_id_by_name(self, name: str) -> Optional[str]:
        """Resolves a project name (slug) to its UUID."""
        res = self.client.table("projects").select("id").eq("name", name).execute()
        if res.data:
            return res.data[0]["id"]
        return None

    async def get_project_name_by_id(self, project_id: str) -> Optional[str]:
        """Resolves a project UUID to its name."""
        res = self.client.table("projects").select("name").eq("id", project_id).execute()
        if res.data:
            return res.data[0]["name"]
        return None

    async def save_asset(self, project_id: str, filename: str, content: str, asset_type: str, file_hash: str) -> str:
        """Saves an asset (e.g. .dtsx file) to the database."""
        # Clean existing assets with same hash for same project to avoid duplicates if desired
        # Or just insert new one.
        data = {
            "project_id": project_id,
            "filename": filename,
            "content": content,
            "type": asset_type,
            "hash": file_hash
        }
        res = self.client.table("assets").insert(data).execute()
        return res.data[0]["id"]

    async def save_transformation(self, asset_id: str, source_code: str, target_code: str, status: str = "completed") -> str:
        """Saves a transformation record."""
        data = {
            "asset_id": asset_id,
            "source_code": source_code,
            "target_code": target_code,
            "status": status
        }
        res = self.client.table("transformations").insert(data).execute()
        return res.data[0]["id"]

    async def update_project_stage(self, project_id_or_name: str, stage: str) -> bool:
        """Updates the stage of a project. Handles both UUID and Name."""
        try:
            # 1. Resolve to UUID if needed
            project_uuid = project_id_or_name
            if "-" not in project_id_or_name:
                resolved = await self.get_project_id_by_name(project_id_or_name)
                if resolved:
                    project_uuid = resolved

            self.client.table("projects").update({"stage": stage}).eq("id", project_uuid).execute()
            return True
        except Exception as e:
            print(f"Error updating stage for {project_id_or_name}: {e}")
            return False

    async def save_project_layout(self, project_id_or_name: str, layout_data: Dict[str, Any]) -> str:
        """Saves the graph layout as a JSON asset. Handles both UUID and Name."""
        import json
        
        # 1. Resolve to UUID if needed
        project_uuid = project_id_or_name
        if "-" not in project_id_or_name: # Simple heuristic for UUID
            resolved = await self.get_project_id_by_name(project_id_or_name)
            if resolved:
                project_uuid = resolved
            else:
                # Fallback: Create project if it doesn't exist? 
                # For layout save, we probably should ensure project exists.
                project_uuid = await self.get_or_create_project(project_id_or_name)

        content = json.dumps(layout_data)
        res = self.client.table("assets").select("id").eq("project_id", project_uuid).eq("type", "LAYOUT").execute()
        
        if res.data:
            asset_id = res.data[0]["id"]
            self.client.table("assets").update({"content": content}).eq("id", asset_id).execute()
            return asset_id
        else:
            return await self.save_asset(project_uuid, "layout.json", content, "LAYOUT", "v1")

    async def get_project_layout(self, project_id_or_name: str) -> Optional[Dict[str, Any]]:
        """Retrieves the graph layout. Handles both UUID and Name."""
        import json

        # 1. Resolve to UUID if needed
        project_uuid = project_id_or_name
        if "-" not in project_id_or_name:
            resolved = await self.get_project_id_by_name(project_id_or_name)
            if resolved:
                project_uuid = resolved
            else:
                return None # Not found

        res = self.client.table("assets").select("content").eq("project_id", project_uuid).eq("type", "LAYOUT").execute()
        if res.data:
            try:
                return json.loads(res.data[0]["content"])
            except:
                return None
        return None

    async def reset_project_data(self, project_id: str) -> bool:
        """Clears all assets and resets stage for a project."""
        try:
            # Delete all assets for the project
            self.client.table("assets").delete().eq("project_id", project_id).execute()
            # Reset stage to 1 (Discovery)
            self.client.table("projects").update({"stage": "1"}).eq("id", project_id).execute()
            return True
        except Exception as e:
            print(f"Error resetting project {project_id}: {e}")
            return False

