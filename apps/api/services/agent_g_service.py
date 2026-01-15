import os
import json
from typing import Dict, Any, List
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

class AgentGService:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_ID", "gpt-4"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY")
        )
        self.prompt_path = os.path.join(os.path.dirname(__file__), "../prompts/agent_g_governance.md")

    def _load_prompt(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    async def generate_documentation(self, project_name: str, mesh: Dict[str, Any], transformations: List[Dict[str, Any]]) -> str:
        """Generates technical documentation and lineage for a project."""
        system_prompt = self._load_prompt(self.prompt_path)
        
        human_content = f"""
        PROJECT NAME: {project_name}
        
        EXECUTION MESH (Logic Relationships):
        {json.dumps(mesh, indent=2)}
        
        TRANSFORMED CODE (PySpark Logic):
        {json.dumps(transformations, indent=2)}
        
        Please generate the Governance Documentation following the structure defined in your system prompt.
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_content)
        ]

        response = await self.llm.ainvoke(messages)
        return response.content.strip()
