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

class ComplianceService:
    """
    The Compliance Officer: Code Auditor Agent.
    Validates generated code against the normative Platform Spec.
    """

    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_ID", "gpt-4"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            temperature=0
        )
        self.prompt_path = os.path.join(os.path.dirname(__file__), "../prompts/compliance_auditor.md")

    def _load_prompt(self) -> str:
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    @logger.llm_debug("Compliance-Auditor")
    async def audit_code(self, notebook_content: str, platform_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audits the provided PySpark code.
        """
        logger.info("Auditing generated code...", "Compliance")
        system_prompt = self._load_prompt()
        
        user_message = f"""
        PLATFORM RULES (Evaluation Criteria):
        {json.dumps(platform_spec.get('qa_rules'), indent=2)}
        
        CODE TO AUDIT:
        --------------------------------------------------
        {notebook_content}
        --------------------------------------------------
        """
        
        # DEBUG: Log context
        logger.debug("Audit Prompt (System)", "Compliance", system_prompt)
        logger.debug("Audit Prompt (User)", "Compliance", user_message)

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]

        try:
            response = await self.llm.ainvoke(messages)
            content = response.content.strip()

            logger.debug("Raw Audit Response", "Compliance", content)

            # Clean JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            return json.loads(content)
        except Exception as e:
            logger.error(f"Audit Error: {e}", "Compliance")
            return {
                "status": "ERROR",
                "score": 0,
                "violations": [{"severity": "CRITICAL", "description": f"Audit failed due to system error: {str(e)}"}]
            }
