from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from typing import Dict, Any, List, Optional
from services.ssis_parser import SSISParser
from services.agent_a_service import AgentAService
from services.graph_service import GraphService
from services.agent_c_service import AgentCService
from services.agent_f_service import AgentFService
from services.agent_g_service import AgentGService
from services.persistence_service import PersistenceService, SupabasePersistence
from services.discovery_service import DiscoveryService
from supabase import create_client, Client

load_dotenv()

app = FastAPI(title="Shift-T API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/prompts/agent-a")
async def get_agent_a_prompt():
    """Returns the current default system prompt for Agent A."""
    agent_a = AgentAService()
    return {"prompt": agent_a._load_prompt()}

@app.get("/ping")
async def ping():
    return {"status": "ok"}



# Supabase Setup
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

@app.get("/")
async def root():
    return {"message": "Welcome to Shift-T API"}

@app.post("/ingest/dtsx")
async def ingest_dtsx(file: UploadFile = File(...)):
    """Ingest, analyze (Agent A), and build mesh (Agent B) for an SSIS package."""
    content = await file.read()
    content_str = content.decode('utf-8')
    
    # 1. Parse DTSX
    parser = SSISParser(content_str)
    summary = parser.get_summary()
    execs = parser.extract_executables()
    summary["executables"] = execs
    
    # 2. Agent A Discovery (Optional: background or async)
    agent_a = AgentAService()
    agent_a_report = await agent_a.analyze_package(summary)
    
    # 3. Agent B Graph Construction
    constraints = parser.extract_precedence_constraints()
    mesh = GraphService.build_mesh(execs, constraints)
    
    # 4. Persistence (Supabase)
    db = SupabasePersistence()
    project_id = await db.get_or_create_project(file.filename)
    asset_id = await db.save_asset(
        project_id, 
        file.filename, 
        content_str, 
        "DTSX", 
        parser.get_hash(content_str)
    )
    
    return {
        "filename": file.filename,
        "hash": parser.get_hash(content_str),
        "agent_a": agent_a_report,
        "mesh": mesh,
        "asset_id": asset_id
    }

class TranspileRequest(BaseModel):
    node_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None

@app.post("/transpile/task")
async def transpile_task(payload: TranspileRequest):
    """Chain Agent C (Interpreter) and Agent F (Critic) for a robust result."""
    node_data = payload.node_data
    context = payload.context or {}
    # 1. Generate initial code (Agent C)
    agent_c = AgentCService()
    c_result = await agent_c.transpile_task(node_data, context)
    
    if "error" in c_result:
        return c_result

    # 2. Audit and Optimize (Agent F)
    agent_f = AgentFService()
    f_result = await agent_f.review_code(node_data, c_result["pyspark_code"])
    
    # 3. Persistence (Local & Supabase)
    solution_name = context.get("solution_name", "DefaultProject")
    task_name = node_data.get("name", "UnnamedTask")
    
    local_path = PersistenceService.save_transformation(
        solution_name, 
        task_name, 
        f_result.get("optimized_code") or c_result["pyspark_code"]
    )
    
    # 4. Persistence (Supabase)
    asset_id = context.get("asset_id")
    if asset_id:
        db = SupabasePersistence()
        await db.save_transformation(
            asset_id,
            node_data.get("description", ""), # source info
            f_result.get("optimized_code") or c_result["pyspark_code"]
        )

    return {
        "interpreter": c_result,
        "critic": f_result,
        "final_code": f_result.get("optimized_code") or c_result["pyspark_code"],
        "saved_at": local_path
    }

@app.post("/transpile/all")
async def transpile_all(nodes: List[Dict[str, Any]], context: Dict[str, Any] = None):
    """Iteratively transpile all nodes in a mesh."""
    results = []
    agent_c = AgentCService()
    agent_f = AgentFService()
    db = SupabasePersistence()
    
    solution_name = context.get("solution_name", "BulkProject")
    asset_id = context.get("asset_id")

    for node in nodes:
        node_data = node.get("data", {})
        # Skip purely decorative or empty nodes
        if not node_data.get("label"):
            continue
            
        # 1. Generate
        c_res = await agent_c.transpile_task(node_data, context)
        if "error" in c_res:
            results.append({"node": node_data.get("label"), "status": "FAILED", "error": c_res["error"]})
            continue
            
        # 2. Audit
        f_res = await agent_f.review_code(node_data, c_res["pyspark_code"])
        final_code = f_res.get("optimized_code") or c_res["pyspark_code"]
        
        # 3. Save Local
        local_path = PersistenceService.save_transformation(
            solution_name,
            node_data.get("name", node_data.get("label")),
            final_code
        )
        
        # 4. Save Supabase
        if asset_id:
            await db.save_transformation(
                asset_id,
                node_data.get("description", ""), # source info
                final_code
            )
        
        results.append({
            "node": node_data.get("label"),
            "status": "SUCCESS",
            "score": f_res.get("score"),
            "path": local_path
        })
        
    return {"summary": results, "solution_path": os.path.join(PersistenceService.BASE_DIR, solution_name)}

@app.post("/governance/document")
async def generate_governance(project_name: str, mesh: Dict[str, Any], context: Dict[str, Any] = None):
    """Generates and persists technical/governance documentation."""
    # 1. Fetch transformations for this project from Supabase
    db = SupabasePersistence()
    asset_id = context.get("asset_id") if context else None
    
    transformations = []
    if asset_id:
        res = db.client.table("transformations").select("target_code").eq("asset_id", asset_id).execute()
        transformations = res.data

    # 2. Invoke Agent G
    agent_g = AgentGService()
    doc_content = await agent_g.generate_documentation(project_name, mesh, transformations)
    
    # 3. Save Local
    solution_name = context.get("solution_name", "GovernanceProject") if context else "GovernanceProject"
    local_path = PersistenceService.save_documentation(solution_name, "GOVERNANCE", doc_content)
    
    return {
        "status": "success",
        "documentation": doc_content,
        "saved_at": local_path
    }

@app.post("/projects/{project_id}/stage")
async def update_stage(project_id: str, payload: Dict[str, str]):
    db = SupabasePersistence()
    success = await db.update_project_stage(project_id, payload.get("stage"))
    return {"success": success}

@app.post("/projects/{project_id}/layout")
async def save_layout(project_id: str, layout: Dict[str, Any]):
    db = SupabasePersistence()
    asset_id = await db.save_project_layout(project_id, layout)
    return {"success": True, "asset_id": asset_id}

@app.get("/projects/{project_id}/layout")
async def get_layout(project_id: str):
    db = SupabasePersistence()
    layout = await db.get_project_layout(project_id)
    return layout or {}

@app.get("/projects/{project_id}/assets")
async def get_project_assets(project_id: str):
    """Returns a scanned inventory of project assets."""
    db = SupabasePersistence()
    project_folder = project_id
    if "-" in project_id: # Heuristic for UUID
        resolved_name = await db.get_project_name_by_id(project_id)
        if resolved_name:
            project_folder = resolved_name
            
    # We could cache this result in DB, but for Triage iterate fast, we scan live.
    return DiscoveryService.scan_project(project_folder)

class TriageParams(BaseModel):
    system_prompt: Optional[str] = None
    user_context: Optional[str] = None

@app.post("/projects/{project_id}/triage")
async def run_triage(project_id: str, params: TriageParams):
    """Re-runs the triage (discovery) process using agentic reasoning."""
    db = SupabasePersistence()
    
    # Resolve UUID or Name to the correct folder name
    project_folder = project_id
    if "-" in project_id: # Heuristic for UUID
        resolved_name = await db.get_project_name_by_id(project_id)
        if resolved_name:
            project_folder = resolved_name

    log_lines = []
    log_lines.append(f"[Start] Initializing Shift-T Triage Agent for Project: {project_id} (Folder: {project_folder})")
    
    # 1. Deep Scan (The Scanner / Pre-processing)
    log_lines.append("[Step 1] Running Deep Scanner (Python Engine)...")
    manifest = DiscoveryService.generate_manifest(project_folder)
    
    file_count = len(manifest["file_inventory"])
    tech_stats = manifest["tech_stats"]
    log_lines.append(f"   > Scanned {file_count} files.")
    log_lines.append(f"   > Tech Stack Detected: {tech_stats}")
    
    # 2. Agent A Analysis (The Detective)
    log_lines.append("[Step 2] Invoking Agent A (Mesh Architect)...")
    if params.system_prompt:
        log_lines.append("   > Applying custom System Prompt override.")
    
    agent_a = AgentAService()
    try:
        # Pass user_context as part of the system prompt or prepend to user message? 
        # Ideally we prepend it to the prompt.
        prompt = params.system_prompt
        if params.user_context:
            prompt = (prompt or "") + f"\n\n[USER CONTEXT CONSTRAINTS]:\n{params.user_context}"
            
        result = await agent_a.analyze_manifest(manifest, system_prompt_override=prompt)
        
        if "error" in result:
            log_lines.append(f"   [WARNING] Agent A returned an error: {result['error']}")
            if "raw_response" in result:
                 log_lines.append(f"   [DEBUG] Raw Response Snippet: {result['raw_response'][:200]}...")

        mesh_graph = result.get("mesh_graph", {})
        nodes = mesh_graph.get("nodes", [])
        edges = mesh_graph.get("edges", [])
        
        log_lines.append(f"   > Agent Analysis Complete.")
        log_lines.append(f"   > Identified {len(nodes)} Functional Nodes and {len(edges)} Dependencies.")
        
        if len(nodes) == 0:
            log_lines.append("   [CRITICAL] No functional nodes identified. Check manifest size or LLM constraints.")

        # Log Observations
        obs = result.get("triage_observations", [])
        for o in obs:
            log_lines.append(f"   [OBSERVATION] {o}")
            
    except Exception as e:
        log_lines.append(f"[ERROR] Agent A Failed: {str(e)}")
        return {
            "assets": [],
            "log": "\n".join(log_lines),
            "error": str(e)
        }

    # 3. Persistence (Supabase)
    log_lines.append("[Step 3] Persisting Mesh Graph...")
    db = SupabasePersistence()
    
    # We map the Agent's "nodes" back to the format our Frontend Graph expects (id, position, data)
    # The Agent returns semantically rich nodes. We need to layout or just save them.
    # For now, we save raw layout or let Frontend handle auto-layout.
    
    # Transform Agent Nodes to ReactFlow Nodes (basic)
    rf_nodes = []
    # Filter for graph: Only show CORE and SUPPORT nodes. IGNORED are for the inventory only.
    graph_eligible = [n for n in nodes if n.get("category") != "IGNORED"]
    
    for i, n in enumerate(graph_eligible):
        rf_nodes.append({
            "id": n["id"],
            "type": "custom", 
            "position": {"x": 200 + (i % 5 * 250), "y": 100 + (i // 5 * 150)}, # Better grid-like layout
            "data": { 
                "label": n["label"], 
                "category": n.get("category", "CORE"),
                "complexity": n.get("complexity", "LOW"),
                "status": "pending"
            }
        })
        
    rf_edges = []
    for e in edges:
        rf_edges.append({
            "id": f"e{e['from']}-{e['to']}",
            "source": e['from'],
            "target": e['to'],
            "label": e.get('type', 'SEQUENTIAL')
        })
        
    await db.save_project_layout(project_id, {"nodes": rf_nodes, "edges": rf_edges})
    log_lines.append("[Success] Graph saved to database.")
    
    # Map back to assets list for the grid view
    # We merge the scanner inventory with agent intelligence
    final_assets = []
    for item in manifest["file_inventory"]:
        # Find agent info for this file
        agent_node = next((n for n in nodes if n["id"] == item["path"]), None)
        
        final_assets.append({
            "id": item["path"],
            "name": item["name"],
            "type": agent_node["category"] if agent_node else "CORE", # Use Agent category if available
            "status": "analyzed" if agent_node else "unlinked",
            "tags": str(item["signatures"]),
            "dependencies": [] # edges are in the graph now
        })

    return {
        "assets": final_assets,
        "nodes": rf_nodes,
        "edges": rf_edges,
        "log": "\n".join(log_lines)
    }

@app.post("/transpile/optimize")
async def optimize_task_code(payload: Dict[str, Any]):
    """Re-runs Agent F with specific optimization flags."""
    code = payload.get("code")
    optimizations = payload.get("optimizations", [])
    
    agent_f = AgentFService()
    result = await agent_f.optimize_code(code, optimizations)
    
    # 3. Persistence (If context provided, we could save, but for refinement loop usually we wait for 'Approve')
    # For R2 demo, we just return the result.
    
    return result

@app.get("/solutions/{id}/export")
async def export_solution(id: str):
    """Zips the solution folder and returns it."""
    # ... (existing code) ...
    from fastapi.responses import FileResponse
    # ...
    return FileResponse(final_zip, media_type='application/zip', filename=f"{zip_filename}.zip")

@app.get("/projects")
async def list_projects():
    """Returns a list of all projects."""
    db = SupabasePersistence()
    return await db.list_projects()

@app.post("/projects/create")
async def create_project(
    name: str = Form(...),
    project_id: str = Form(...),
    source_type: str = Form(...),
    github_url: str = Form(None),
    overwrite: bool = Form(False),
    file: UploadFile = File(None)
):
    """Creates a new project and initializes it from source."""
    
    # 1. Register in Database (Supabase)
    db = SupabasePersistence()
    real_id = await db.get_or_create_project(name) # In a real app we might use project_id as ID or verify uniqueness
    # Note: get_or_create_project returns ID based on name. 
    # For this demo, we assume the user-generated 'project_id' matches or we just use the ID returned by DB for folder.
    
    # 2. Handle File Upload (Save temporarily)
    temp_zip_path = None
    if source_type == "zip" and file:
        temp_zip_path = os.path.join(PersistenceService.BASE_DIR, f"{project_id}_temp.zip")
        with open(temp_zip_path, "wb") as buffer:
            import shutil
            shutil.copyfileobj(file.file, buffer)
            
    # 3. Initialize Directory
    success = PersistenceService.initialize_project_from_source(
        project_id=project_id,
        source_type=source_type,
        file_path=temp_zip_path,
        github_url=github_url,
        overwrite=overwrite
    )
    
    if success:
        return {"success": True, "project_id": project_id}
    else:
        return {"success": False, "error": "Failed to initialize project"}

@app.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Deletes a project from both DB and Filesystem."""
    db = SupabasePersistence()
    
    # 1. Fetch Project Name for Folder Deletion
    project_name = await db.get_project_name_by_id(project_id)
    
    # 2. Delete from DB
    db_success = await db.delete_project(project_id)
    
    # 3. Delete from FS
    fs_success = False
    if project_name:
        fs_success = PersistenceService.delete_project_directory(project_name)
    else:
        # Fallback: maybe the ID passed IS the name (if simplified elsewhere)
        fs_success = PersistenceService.delete_project_directory(project_id)
    
    return {
        "success": True, 
        "details": {
            "db_deleted": db_success,
            "fs_deleted": fs_success
        }
    }

@app.post("/projects/{project_id}/reset")
async def reset_project(project_id: str):
    """Clears triage results for a project, resetting it to stage 1."""
    db = SupabasePersistence()
    success = await db.reset_project_data(project_id)
    return {"success": success}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
