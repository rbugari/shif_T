from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import shutil
from typing import Dict, Any, List, Optional
from services.ssis_parser import SSISParser
from services.agent_a_service import AgentAService
from services.graph_service import GraphService
from services.agent_c_service import AgentCService
from services.agent_f_service import AgentFService
from services.agent_g_service import AgentGService
from services.developer_service import DeveloperService
from config.platform_spec import PlatformSpec
from services.persistence_service import PersistenceService, SupabasePersistence
from services.discovery_service import DiscoveryService
from services.refinement.governance_service import GovernanceService
from services.report_service import ReportService
from supabase import create_client, Client
import io
import datetime
import uuid

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
async def get_agent_a_prompt(project_id: Optional[str] = None, compiled: bool = False):
    """Returns the current default system prompt for Agent A."""
    agent_a = AgentAService()
    if compiled and project_id:
        knowledge_context = DiscoveryService.get_global_knowledge_context()
        return {"prompt": agent_a.compile_prompt(knowledge_context)}
    return {"prompt": agent_a._load_prompt()}

@app.get("/prompts/agent-c")
async def get_agent_c_prompt(project_id: Optional[str] = None, compiled: bool = False):
    if compiled and project_id:
        dev_service = DeveloperService()
        platform_spec = PlatformSpec().load_platform_spec()
        knowledge_context = DiscoveryService.get_global_knowledge_context()
        return {"prompt": dev_service.compile_prompt(platform_spec, knowledge_context)}
    agent_c = AgentCService()
    return {"prompt": agent_c._load_prompt()}

@app.get("/prompts/agent-f")
async def get_agent_f_prompt(project_id: Optional[str] = None, compiled: bool = False):
    agent_f = AgentFService()
    if compiled and project_id:
        platform_spec = PlatformSpec().load_platform_spec()
        return {"prompt": agent_f.compile_prompt(platform_spec)}
    return {"prompt": agent_f._load_prompt()}

@app.get("/prompts/agent-g")
async def get_agent_g_prompt(project_id: Optional[str] = None, compiled: bool = False):
    agent_g = AgentGService()
    if compiled and project_id:
        db = SupabasePersistence()
        resolved_uuid = await db.resolve_project_id(project_id)
        project_name = await db.get_project_name_by_id(resolved_uuid) if resolved_uuid else project_id
        return {"prompt": agent_g.compile_prompt(project_name)}
    return {"prompt": agent_g._load_prompt()}

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

@app.patch("/assets/{asset_id}")
async def patch_asset(asset_id: str, updates: Dict[str, Any]):
    """Updates asset metadata (type, selected status)."""
    db = SupabasePersistence()
    success = await db.update_asset_metadata(asset_id, updates)
    return {"success": success}

@app.get("/projects/{project_id}/logs")
async def get_project_logs(project_id: str, type: str = "migration"):
    """Returns the content of a log file. type='migration' or 'triage'."""
    db = SupabasePersistence()
    
    # Standardized Resolution
    resolved_uuid = await db.resolve_project_id(project_id)
    if not resolved_uuid:
        return {"logs": "[Error] Project not found"}
        
    project_name = project_id
    resolved_name = await db.get_project_name_by_id(resolved_uuid)
    if resolved_name:
        project_name = resolved_name
    
    filename = "migration.log"
    if type == "triage":
        filename = "triage.log"

    try:
        full_path = os.path.join(PersistenceService.ensure_solution_dir(project_name), filename)
        content = PersistenceService.read_file_content(project_name, full_path)
        return {"logs": content}
    except (FileNotFoundError, ValueError):
        return {"logs": ""} # File likely doesn't exist yet
    except Exception as e:
        return {"logs": f"Error reading logs: {e}"}


@app.get("/projects/{project_id}/assets")
async def get_project_assets(project_id: str):
    """Returns a scanned inventory of project assets."""
    db = SupabasePersistence()
    # We return the PERSISTED assets from the DB.
    resolved_uuid = await db.resolve_project_id(project_id)
    if not resolved_uuid:
        return {"assets": [], "error": "Project not found"}

            
    assets = await db.get_project_assets(resolved_uuid)
    return {"assets": assets}

class TriageParams(BaseModel):
    system_prompt: Optional[str] = None
    user_context: Optional[str] = None

@app.post("/projects/{project_id}/triage")
async def run_triage(project_id: str, params: TriageParams):
    """Re-runs the triage (discovery) process using agentic reasoning."""
    db = SupabasePersistence()
    
    # Resolve UUID and Name correctly
    project_uuid = await db.resolve_project_id(project_id)
    if not project_uuid:
        return {"error": f"Project '{project_id}' not found"}
        
    project_folder = project_id
    # Always try to get the real name for the folder to ensure FS consistency
    resolved_name = await db.get_project_name_by_id(project_uuid)
    if resolved_name:
        project_folder = resolved_name


    # GOVERNANCE CHECK: TRIAGE is only allowed in TRIAGE mode.
    current_status = await db.get_project_status(project_uuid)
    if current_status == "DRAFTING":
        return {
            "assets": [],
            "log": "[ERROR] Project is in DRAFTING mode. Triage is locked. Unlock project to modify scope.",
            "error": "Project is in DRAFTING mode"
        }

    # Setup Real-time Logging
    log_file_path = os.path.join(PersistenceService.ensure_solution_dir(project_folder), "triage.log")
    # Clear existing log
    with open(log_file_path, "w", encoding="utf-8") as f:
        f.write("")

    log_lines = []
    
    def log_step(msg: str):
        log_lines.append(msg)
        # Real-time append to file
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(msg + "\n")

    log_step(f"[Start] Initializing Shift-T Triage Agent for Project: {project_id} (Folder: {project_folder})")
    
    # 1. Deep Scan (The Scanner / Pre-processing)
    log_step("[Step 1] Running Deep Scanner (Python Engine)...")
    from fastapi.concurrency import run_in_threadpool
    manifest = await run_in_threadpool(DiscoveryService.generate_manifest, project_folder)
    
    file_count = len(manifest["file_inventory"])
    tech_stats = manifest["tech_stats"]
    
    # 1.1 Primary Technology Detection & Suggestions
    detected_source = None
    print(f"DEBUG: Triage Tech Stats: {tech_stats}")

    if tech_stats.get('dtsx'):
        detected_source = "SSIS"
    elif tech_stats.get('sql'):
        # Check signatures of .sql files to refine the guess
        sql_signatures = []
        for item in manifest["file_inventory"]:
             if item['type'] == 'SQL_SCRIPT':
                 sql_signatures.extend(item['signatures'])
        
        print(f"DEBUG: SQL Signatures found: {sql_signatures}")

        if any("Oracle" in s for s in sql_signatures): detected_source = "ORACLE"
        elif any("MySQL" in s for s in sql_signatures): detected_source = "MYSQL"
        elif any("SQL Server" in s for s in sql_signatures): detected_source = "SQL_SERVER"
        else: detected_source = "SQL_SERVER" # Default for .sql
    
    print(f"DEBUG: Final Detected Source: {detected_source}")

    # Suggest & Auto-Update
    metadata = await db.get_project_metadata(project_uuid)
    current_config = metadata.get("config") or {}
    current_source = current_config.get("source_tech")
    
    print(f"DEBUG: Current Config Source: {current_source}")

    suggested_source_tech = None

    if detected_source:
        # Always suggest if mismatch, do not auto-update even if empty
        if current_source != detected_source:
            log_step(f"   > [INFO] Technology Detected: {detected_source}. Configured: {current_source}. Suggesting update.")
            suggested_source_tech = detected_source

    # Format tech stats for log
    tech_summary = ", ".join([f"{count} {ext.upper()}" for ext, count in tech_stats.items()])
    log_step(f"   > Scanned {file_count} files.")
    log_step(f"   > Tech Stack Detected: {tech_summary or 'No specific technology detected'}")

    # 2. Agent A Analysis (The Detective)
    log_step("[Step 2] Invoking Agent A (Mesh Architect)...")
    if params.system_prompt:
        log_step("   > Applying custom System Prompt override.")
    
    agent_a = AgentAService()
    try:
        # Pass user_context as part of the system prompt or prepend to user message? 
        # Ideally we prepend it to the prompt.
        prompt = params.system_prompt
        if params.user_context:
            prompt = (prompt or "") + f"\n\n[USER CONTEXT CONSTRAINTS]:\n{params.user_context}"
            
        result = await agent_a.analyze_manifest(manifest, system_prompt_override=prompt)
        
        if "error" in result:
            log_step(f"   [WARNING] Agent A returned an error: {result['error']}")
            if "raw_response" in result:
                 log_step(f"   [DEBUG] Raw Response Snippet: {result['raw_response'][:200]}...")

        mesh_graph = result.get("mesh_graph", {})
        nodes = mesh_graph.get("nodes", [])
        edges = mesh_graph.get("edges", [])
        
        log_step(f"   > Agent Analysis Complete.")
        log_step(f"   > Identified {len(nodes)} Functional Nodes and {len(edges)} Dependencies.")
        
        if len(nodes) == 0:
            log_step("   [CRITICAL] No functional nodes identified. Check manifest size or LLM constraints.")

        # Log Observations
        obs = result.get("triage_observations", [])
        for o in obs:
            log_step(f"   [OBSERVATION] {o}")

        # --- PERSIST AI INSIGHTS TO PROJECT CONFIG ---
        ai_insights = {
            "solution_summary": result.get("solution_summary", ""),
            "triage_observations": result.get("triage_observations", []),
            "critical_questions": result.get("critical_questions", []),
            "gaps": result.get("gaps", []),
            "triage_metadata": {
                "detected_paradigm": result.get("detected_paradigm", "ETL"),
                "total_assets_scanned": len(manifest.get("file_inventory", [])),
                "core_targets": len([n for n in nodes if n.get("category") == "CORE"])
            }
        }
        await db.update_project_config(project_uuid, ai_insights)

            
    except Exception as e:

        log_step(f"[ERROR] Agent A Failed: {str(e)}")
        return {
            "assets": [],
            "log": "\n".join(log_lines),
            "error": str(e)
        }

    # 3. Persistence (Supabase)
    log_step("[Step 3] Persisting Mesh Graph and Discovered Assets...")
    
    # NEW: Persist the scanner inventory to DB
    db_assets = []
    for item in manifest["file_inventory"]:
        # Find agent info for this file
        agent_node = next((n for n in nodes if n["id"] == item["path"]), None)
        
        # Determine category (type in DB)
        category = agent_node["category"] if agent_node else "IGNORED" 
        if not agent_node:
            # Fallback for files not analyzed by Agent A
            category = DiscoveryService._map_extension_to_type(item["name"].split('.')[-1].lower() if '.' in item["name"] else 'none')

        # Prepare Metadata (Drivers + Agent Intelligence)
        asset_metadata = item.get("metadata", {})
        if agent_node and "technical_summary" in agent_node:
            asset_metadata["technical_summary"] = agent_node["technical_summary"]

        db_assets.append({
            "filename": item["name"],
            "type": category,
            "source_path": item["path"],
            "metadata": asset_metadata,  # Store the rich technical info
            "selected": True if category != "IGNORED" else False
        })

    
    # Clean up old assets before saving new ones to prevent accumulation/duplicates
    # Inlining the delete to avoid AttributeError if server didn't reload PersistenceService
    try:
        db.client.table("assets").delete().eq("project_id", project_uuid).execute()
    except Exception as e:
        print(f"Warning: Failed to clean assets: {e}")

    saved_assets = await db.batch_save_assets(project_uuid, db_assets)
    # Create lookup map for UUIDs: source_path -> id
    # Create lookup map for UUIDs: source_path -> id AND source_path -> filename
    asset_map = { a["source_path"]: a["id"] for a in saved_assets }
    pname_map = { a["source_path"]: a["filename"] for a in saved_assets }

    
    # Transform Agent Nodes to ReactFlow Nodes (basic)
    rf_nodes = []
    # Filter for graph: Only show CORE and SUPPORT nodes. IGNORED are for the inventory only.
    graph_eligible = [n for n in nodes if n.get("category") != "IGNORED"]
    
    for i, n in enumerate(graph_eligible):
        # Find UUID for this node
        n_uuid = asset_map.get(n["id"], n["id"]) # Fallback to path if not found (shouldn't happen)
        
        # FIX: Use Filename if available, fallback to Agent Label
        display_label = pname_map.get(n["id"], n["label"])

        rf_nodes.append({
            "id": n_uuid, # Use UUID for Graph Nodes too!
            "type": "custom", 
            "position": {"x": 200 + (i % 5 * 250), "y": 100 + (i // 5 * 150)}, # Better grid-like layout
            "data": { 
                "label": display_label, 
                "category": n.get("category", "CORE"),
                "complexity": n.get("complexity", "LOW"),
                "status": "pending"
            }
        })
        
    rf_edges = []
    for e in edges:
        # Resolve edge source/target to UUIDs if they mirror paths
        src_uid = asset_map.get(e['from'], e['from'])
        tgt_uid = asset_map.get(e['to'], e['to'])
        
        rf_edges.append({
            "id": f"e{src_uid}-{tgt_uid}",
            "source": src_uid,
            "target": tgt_uid,
            "label": e.get('type', 'SEQUENTIAL')
        })
        
    await db.save_project_layout(project_uuid, {"nodes": rf_nodes, "edges": rf_edges})
    log_step("[Success] Graph and Assets saved to database.")
    
    # Map back to assets list for the grid view
    # We merge the scanner inventory with agent intelligence
    final_assets = []
    for item in manifest["file_inventory"]:
        # Find agent info for this file
        agent_node = next((n for n in nodes if n["id"] == item["path"]), None)
        # Find UUID
        item_uuid = asset_map.get(item["path"])
        
        if item_uuid:
            final_assets.append({
                "id": item_uuid, # THIS IS THE FIX: Return UUID
                "name": item["name"],
                "type": agent_node["category"] if agent_node else "CORE", # Use Agent category if available
                "status": "analyzed" if agent_node else "unlinked",
                "tags": str(item["signatures"]),
                "selected": True if (agent_node and agent_node["category"] != "IGNORED") else False,
                "dependencies": [] # edges are in the graph now
            })

    return {
        "assets": final_assets,
        "nodes": rf_nodes,
        "edges": rf_edges,
        "log": "\n".join(log_lines),
        "suggested_source_tech": suggested_source_tech
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
    res = db.client.table("projects").select("*, assets_count:assets(count)").execute()
    # Post-process count if needed, or rely on Supabase alias
    return res.data if res.data else []

@app.get("/projects/{project_id}")
async def get_project_details(project_id: str):
    """Returns project details (name, repo_url, etc.) by ID."""
    db = SupabasePersistence()
    
    # Resolve to UUID
    resolved_uuid = await db.resolve_project_id(project_id)
    if not resolved_uuid:
        return {"error": "Project not found"}
        
    metadata = await db.get_project_metadata(resolved_uuid)
    if metadata:
        return {"id": resolved_uuid, **metadata}
        
    return {"error": "Project data not found"}


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
    real_id = await db.get_or_create_project(name, github_url) # Pass github_url
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

@app.get("/projects/{project_id}/files")
async def list_project_files(project_id: str):
    """Returns the file tree for the project's output directory."""
    db = SupabasePersistence()
    resolved_uuid = await db.resolve_project_id(project_id)
    if not resolved_uuid:
        return {"files": []}
        
    project_name = project_id
    resolved_name = await db.get_project_name_by_id(resolved_uuid)
    if resolved_name:
        project_name = resolved_name
        
    tree = PersistenceService.get_project_files(project_name)
    return tree


@app.get("/projects/{project_id}/files/content")
async def get_file_content(project_id: str, path: str):
    """Returns the content of a specific file."""
    db = SupabasePersistence()
    resolved_uuid = await db.resolve_project_id(project_id)
    if not resolved_uuid:
        return {"error": "Project not found"}
        
    project_name = project_id
    resolved_name = await db.get_project_name_by_id(resolved_uuid)
    if resolved_name:
        project_name = resolved_name
        
    try:
        content = PersistenceService.read_file_content(project_name, path)
        return {"content": content}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Failed to read file: {e}"}


from services.migration_orchestrator import MigrationOrchestrator

@app.post("/transpile/orchestrate")
async def trigger_orchestration(payload: Dict[str, Any]):
    """Triggers the full Migration Orchestrator (Agents C -> F -> G)."""
    print(f"DEBUG: Entering trigger_orchestration with payload: {payload}")
    project_id = payload.get("project_id")
    limit = payload.get("limit", 0)
    
    if not project_id:
        return {"error": "project_id is required"}
        
    # 1. Resolve Project UUID
    db = SupabasePersistence()
    resolved_uuid = await db.resolve_project_id(project_id)
    if not resolved_uuid:
        return {"error": "Project not found"}
        
    project_name = project_id
    resolved_name = await db.get_project_name_by_id(resolved_uuid)
    if resolved_name:
        project_name = resolved_name


    print(f"DEBUG: Instantiating MigrationOrchestrator for {project_name}")
    orchestrator = MigrationOrchestrator(project_name)
    print("DEBUG: Running full migration...")
    result = await orchestrator.run_full_migration(limit=limit)
    print("DEBUG: Migration complete.")
    return result

@app.post("/projects/{project_id}/reset")
async def reset_project(project_id: str):
    """Clears triage results for a project, resetting it to stage 1."""
    db = SupabasePersistence()
    resolved_uuid = await db.resolve_project_id(project_id)
    if not resolved_uuid:
        return {"success": False, "error": "Project not found"}
    success = await db.reset_project_data(resolved_uuid)

    return {"success": success}

@app.post("/projects/{project_id}/approve")
async def approve_triage(project_id: str):
    """Locks the project scope and transitions to DRAFTING state."""
    db = SupabasePersistence()
    
    project_uuid = await db.resolve_project_id(project_id)
    if not project_uuid:
        return {"success": False, "error": "Project not found"}


    # Check validation rules? (e.g. must have assets selected)
    # For now, just transition.
    success_status = await db.update_project_status(project_uuid, "DRAFTING")
    success_stage = await db.update_project_stage(project_uuid, "2")
    return {"success": success_status and success_stage, "status": "DRAFTING"}

@app.post("/projects/{project_id}/unlock")
async def unlock_triage(project_id: str):
    """Unlocks the project scope and transitions back to TRIAGE state."""
    db = SupabasePersistence()
    
    project_uuid = await db.resolve_project_id(project_id)
    if not project_uuid:
        return {"success": False, "error": "Project not found"}


    success = await db.update_project_status(project_uuid, "TRIAGE")
    return {"success": success, "status": "TRIAGE"}

@app.post("/projects/{project_id}/config")
async def update_project_config(project_id: str, config: Dict[str, Any]):
    """Updates the project configuration (source/destination tech)."""
    db = SupabasePersistence()
    success = await db.update_project_config(project_id, config)
    return {"success": success}

# Duplicate get_project_logs removed.


# --- Phase 3: Refinement Endpoints ---
from services.refinement.refinement_orchestrator import RefinementOrchestrator

@app.post("/refine/start")
async def start_refinement(payload: dict):
    """Triggers the Refinement Phase (Profiler -> Architect -> Refactor -> Ops)."""
    project_id = payload.get("project_id")
    if not project_id:
        return {"error": "Project ID required"}
    
    # Resolve Project Name for File System Access
    db = SupabasePersistence()
    project_name = project_id
    if "-" in project_id:
        n = await db.get_project_name_by_id(project_id)
        if n: project_name = n

    # In a real async system, this would be a background task. 
    # For MVP, we run synchronously to show immediate results.
    orchestrator = RefinementOrchestrator()
    result = orchestrator.start_pipeline(project_name)
    return result


@app.get("/projects/{project_id}/refinement/state")
async def get_refinement_state(project_id: str):
    """Returns the persisted state of Phase 3 (logs and profile)."""
    db = SupabasePersistence()
    project_name = project_id
    if "-" in project_id:
        n = await db.get_project_name_by_id(project_id)
        if n: project_name = n

    state = {
        "log": [],
        "profile": None
    }

    try:
        # 1. Fetch Logs
        log_content = PersistenceService.read_file_content(project_name, "refinement.log")
        if log_content:
            state["log"] = log_content.split("\n")
    except:
        pass

    try:
        # 2. Fetch Profile Metadata
        profile_content = PersistenceService.read_file_content(project_name, "Refined/profile_metadata.json")
        if profile_content:
            import json
            state["profile"] = json.loads(profile_content)
    except:
        pass

    return state


@app.get("/projects/{project_id}/status")
async def get_project_status(project_id: str):
    """Returns the current governance status."""
    db = SupabasePersistence()
    
    # Resolve to UUID
    resolved_uuid = await db.resolve_project_id(project_id)
    if not resolved_uuid:
        return {"error": "Project not found"}
        
    res = db.client.table("projects").select("*").eq("id", resolved_uuid).execute()
    status = res.data[0].get("status") if res.data else None
    return {"status": status}


@app.get("/projects/{project_id}/governance")
async def get_governance(project_id: str):
    """Returns the certification report and lineage for the project."""
    db = SupabasePersistence()
    project_name = project_id
    if "-" in project_id:
        n = await db.get_project_name_by_id(project_id)
        if n: project_name = n

    service = GovernanceService()
    try:
        report = service.get_certification_report(project_name)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/projects/{project_id}/export")
async def export_project(project_id: str):
    """Streams the project solution as a ZIP bundle."""
    db = SupabasePersistence()
    project_name = project_id
    if "-" in project_id:
        n = await db.get_project_name_by_id(project_id)
        if n: project_name = n

    service = GovernanceService()
    try:
        zip_buffer = service.create_export_bundle(project_name)
        filename = f"ShiftT_Solution_{project_name}.zip"
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/x-zip-compressed",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False

@app.get("/projects/{project_id}/triage/report")
async def download_triage_report(project_id: str):
    """Generates and downloads a PDF report for the Triage stage."""
    db = SupabasePersistence()
    project_uuid = await db.resolve_project_id(project_id)
    if not project_uuid:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")


    # Get Metadata
    meta = await db.get_project_metadata(project_uuid)
    
    # Get Assets
    assets = await db.get_project_assets(project_uuid)
    
    # Get Layout (Dependencies)
    layout = await db.get_project_layout(project_uuid)
    
    report_data = {
        "name": meta.get("name", "Unknown") if meta else project_id,
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "assets": assets,
        "layout": layout,
        "config": meta.get("config", {}) if meta else {},
        "summary": {} 
    }


    
    pdf_bytes = ReportService.generate_triage_pdf(report_data)
    project_name = meta.get("name", project_id) if meta else project_id
    safe_name = "".join([c for c in project_name if c.isalnum() or c in (' ', '-', '_')]).strip()
    filename = f"Triaje_{safe_name}.pdf"
    
    # [NEW] Persist the report to the solution directory
    try:
        saved_path = PersistenceService.save_report_pdf(project_name, filename, pdf_bytes)
        print(f"Report saved to: {saved_path}")
    except Exception as e:
        print(f"Error saving report to disk: {e}")
    
    import urllib.parse
    encoded_filename = urllib.parse.quote(filename)
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes), 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}; filename=\"{filename}\""}
    )


@app.get("/projects/{project_id}/governance/report")
async def download_governance_report(project_id: str):
    """Generates and downloads the Final Governance PDF Report."""
    db = SupabasePersistence()
    project_uuid = await db.resolve_project_id(project_id)
    if not project_uuid:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
    
    # 1. Get Project Metadata
    meta = await db.get_project_metadata(project_uuid)
    project_name = meta.get("name", project_id) if meta else project_id

    # 2. Get Governance Data (Score, Lineage, Stats)
    gov_service = GovernanceService()
    try:
        # Reuse standard project name resolution
        gov_data = gov_service.get_certification_report(project_name)
    except Exception as e:
        gov_data = {"error": str(e)}

    # 3. Get Manual Content (from file)
    manual_content = "Operating Manual not generated."
    try:
        content = PersistenceService.read_file_content(project_name, "GOVERNANCE/manual.md")
        if content: manual_content = content
    except:
        pass
    
    # 4. Prepare Data Packet
    report_data = {
        "name": project_name,
        "governance": gov_data,
        "manual_content": manual_content
    }

    # 5. Generate PDF
    pdf_bytes = ReportService.generate_final_report_pdf(report_data)
    
    safe_name = "".join([c for c in project_name if c.isalnum() or c in (' ', '-', '_')]).strip()
    filename = f"Certificate_{safe_name}.pdf"
    
    # Persist copy
    try:
        PersistenceService.save_report_pdf(project_name, filename, pdf_bytes)
    except:
        pass

    import urllib.parse
    encoded_filename = urllib.parse.quote(filename)
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}; filename=\"{filename}\""}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
