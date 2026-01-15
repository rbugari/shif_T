import os
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any
import json

class AgentAService:
    """Service for Agent A (Detective) using Azure OpenAI."""
    
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_ID", "gpt-4"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            temperature=0
        )
        
        self.prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "agent_a_discovery.md")
        
    def _load_prompt(self) -> str:
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    async def analyze_manifest(self, manifest: Dict[str, Any], system_prompt_override: str = None) -> Dict[str, Any]:
        """Analyzes the full project manifest to build the Mesh Graph."""
        
        system_prompt = system_prompt_override or self._load_prompt()
        
        # Prepare content for LLM (might need truncation if too large)
        # We send the structure and snippets.
        
        user_message = f"""
        PROJECT MANIFEST:
        -----------------
        Project ID: {manifest.get('project_id')}
        Tech Stack Stats: {json.dumps(manifest.get('tech_stats'), indent=2)}
        
        FILE INVENTORY:
        {json.dumps(manifest.get('file_inventory'), indent=2)}
        
        INSTRUCTIONS:
        1. Process the FILE INVENTORY. Pay special attention to 'metadata' fields for .dtsx files (contain executables) and 'signatures' for .sql files.
        2. Assign a FUNCTIONAL CATEGORY (CORE, SUPPORT, IGNORED) to all relevant files.
        3. Discover dependencies (Edges) based on 'invocations', 'metadata.executables', or naming conventions. Focus the mesh on CORE components.
        4. Synthesize the Mesh Graph. Return ONLY the JSON requested in the System Prompt.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        # Using a larger context model might be needed if inventory is huge. 
        # Assuming gpt-4 or 4-turbo window is sufficient for this demo.
        response = await self.llm.ainvoke(messages)
        content = response.content
        
        # Clean potential markdown formatting
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback for partial JSON or comments
            return {
                "error": "Failed to parse LLM response", 
                "raw_response": content,
                "mesh_graph": {"nodes": [], "edges": []}
            }
    async def analyze_package(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes a single SSIS package summary (legacy/individual ingest)."""
        system_prompt = self._load_prompt()
        
        user_message = f"""
        ANALYZE THIS SSIS PACKAGE:
        -------------------------
        Summary: {json.dumps(summary, indent=2)}
        
        INSTRUCTIONS:
        Identify the primary purpose of this package and any critical tasks.
        Return a summary and classification.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        response = await self.llm.ainvoke(messages)
        content = response.content
        
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        try:
            return json.loads(content)
        except:
            return {"raw_analysis": content}
