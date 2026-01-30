import os
import json
from typing import Dict, Any, List
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
try:
    from apps.api.utils.logger import logger
except ImportError:
    try:
        from utils.logger import logger
    except ImportError:
        from ..utils.logger import logger


class AgentCService:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_ID", "gpt-4"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY")
        )
        self.prompt_path = os.path.join(os.path.dirname(__file__), "../prompts/agent_c_interpreter.md")
        self.standards_path = os.path.join(os.path.dirname(__file__), "../prompts/coding_standards.md")

    def _load_prompt(self, path: str = None) -> str:
        target_path = path or self.prompt_path
        with open(target_path, "r", encoding="utf-8") as f:
            return f.read()

    def _get_migration_rules(self, source_type: str, target_lang: str = None) -> str:
        """
        Determines and loads the correct migration rules based on Source Type and Target Lang.
        Example: source=sql, target=snowpark -> Loads knowledge/sql_snowpark.md
        """
        import os
        if not target_lang:
            target_lang = os.getenv("TARGET_LANG", "pyspark").lower()
        else:
            target_lang = target_lang.lower()
        
        # Map source types to file prefixes
        # e.g. SQL_SCRIPT -> sql, SSIS_PACKAGE -> ssis
        source_prefix = "sql" # default
        if "SSIS" in source_type.upper():
            source_prefix = "ssis"
        elif "SQL" in source_type.upper():
            source_prefix = "sql"
            
        rule_filename = f"{source_prefix}_{target_lang}.md"
        
        # Construct path: apps/api/prompts/knowledge/filename
        base_dir = os.path.dirname(self.prompt_path) # apps/api/prompts
        knowledge_path = os.path.join(base_dir, "knowledge", rule_filename)
        
        try:
            if os.path.exists(knowledge_path):
                with open(knowledge_path, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                return f"WARN: No migration rules found for {source_prefix} -> {target_lang} at {knowledge_path}"
        except Exception as e:
            return f"WARN: Error loading rules: {str(e)}"

    async def transpile_task(self, node_data: Dict[str, Any], context: Dict[str, Any] = None, target_lang: str = None) -> Dict[str, Any]:
        """Transpiles a single SSIS task into PySpark/Snowpark code following defined standards."""
        system_prompt = self._load_prompt(self.prompt_path)
        standards = self._load_prompt(self.standards_path)
        
        # Dynamic Knowledge Injection
        effective_target = (target_lang or os.getenv("TARGET_LANG", "pyspark")).lower()
        source_type = node_data.get('type', 'UNKNOWN')
        migration_rules = self._get_migration_rules(source_type, effective_target)
        
        human_content = f"""
        CODING STANDARDS TO FOLLOW:
        {standards}

        MIGRATION KNOWLEDGE ({effective_target.upper()}):
        {migration_rules}

        TRANSPILE THE FOLLOWING TASK:
        Task Name: {node_data.get('name')}
        Task Type: {node_data.get('type')}
        Task Description: {node_data.get('description')}
        
        CONTEXT:
        {json.dumps(context or {}, indent=2)}
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_content)
        ]

        response = await self.llm.ainvoke(messages)
        content = response.content.strip()

        # Clean JSON if LLM added markdown blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse LLM response as JSON",
                "raw_response": content
            }
