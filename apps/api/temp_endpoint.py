
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
        "profile": null
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
