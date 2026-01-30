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

class DeveloperService:
    """
    The Code Developer: Context-Aware Transpiler.
    Generates PySpark code using Platform Rules and Schema Context.
    """

    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_ID", "gpt-4"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            temperature=0  # Deterministic code gen
        )
        self.prompt_path = os.path.join(os.path.dirname(__file__), "../prompts/developer_transpiler.md")

    def _load_prompt(self) -> str:
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def _get_migration_rules(self, source_type: str, target_lang: str = None) -> str:
        """
        Determines and loads the correct migration rules based on Source Type and Target Lang.
        """
        import os
        if not target_lang:
            target_lang = os.getenv("TARGET_LANG", "pyspark").lower()
        else:
            target_lang = target_lang.lower()
        
        # Map source types to file prefixes
        source_prefix = "sql" # default
        if "SSIS" in source_type.upper():
            source_prefix = "ssis"
        elif "SQL" in source_type.upper():
            source_prefix = "sql"
            
        rule_filename = f"{source_prefix}_{target_lang}.md"
        
        # Construct path: apps/api/prompts/knowledge/filename
        # self.prompt_path is .../prompts/developer_transpiler.md
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

    def compile_prompt(self, platform_spec: Dict[str, Any], knowledge_context: str = "") -> str:
        """Returns the system prompt merged with standards and knowledge context."""
        prompt = self._load_prompt()
        prompt += f"\n\n## PLATFORM RULES (Target Technology)\n{json.dumps(platform_spec, indent=2)}"
        if knowledge_context:
            prompt += f"\n\n## DRIVER KNOWLEDGE CONTEXT (Source Technology)\n{knowledge_context}"
        return prompt

    @logger.llm_debug("Developer-Transpiler")
    async def generate_code(self, 
                            task_def: Dict[str, Any], 
                            platform_spec: Dict[str, Any], 
                            schema_ref: Dict[str, Any],
                            knowledge_context: str = "",
                            target_lang: str = None) -> Dict[str, Any]:
        """
        Generates code for a specific task/package.
        """
        logger.info(f"Generating code for task: {task_def.get('package_name')}", "Developer")
        system_prompt = self._load_prompt()
        
        # Dynamic Knowledge Injection if not provided
        if not knowledge_context or knowledge_context.startswith("<!--"):
            # Determine source type from task/package or assume default based on flow
            # For now, SSIS Packages usually end in .dtsx, SQL in .sql
            # task_def 'package_name' gives a hint.
            pkg_name = task_def.get('package_name', '')
            source_type = "SSIS" if ".dtsx" in pkg_name or "Package" in pkg_name else "SQL"
            
            knowledge_context = self._get_migration_rules(source_type, target_lang)

        # Prepare Context
        # Filter schema ref to only relevant tables if possible, 
        # but for now passing full context (or a summarized version is better for token limits).
        # We'll rely on the LLM to pick what it needs from the provided JSONs.
        
        user_message = f"""
        PLATFORM RULES (Use these patterns):
        {json.dumps(platform_spec, indent=2)}
        
        DRIVER KNOWLEDGE (Source Technology Context):
        {knowledge_context or "No specific driver context provided."}

        
        TARGET SCHEMA (Use these types):
        {json.dumps(schema_ref, indent=2)}
        
        TASK TO TRANSPILE:
        Name: {task_def.get('package_name')}
        Inputs: {task_def.get('inputs')}
        Lookups: {task_def.get('lookups')}
        Outputs: {task_def.get('outputs')}
        Description: Auto-generated task from SSIS package {task_def.get('package_name')}.
        """

        # DEBUG: Log the full constructed prompt
        logger.debug("Constructed LLM Prompt (System)", "Developer", system_prompt)
        logger.debug("Constructed LLM Prompt (User)", "Developer", user_message)

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]

        try:
            response = await self.llm.ainvoke(messages)
            content = response.content.strip()

            logger.debug("Raw LLM Response", "Developer", content)

            # Clean JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            return json.loads(content)
        except Exception as e:
            logger.error(f"Error generating code: {e}", "Developer")
            return {
                "error": str(e),
                "notebook_content": f"# Error generating code: {e}"
            }
