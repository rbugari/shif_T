from .base_driver import IBaseDriver
from typing import Dict, Any, List
# Import SSISParser from parent directory - relative import might be tricky depending on how this module is loaded.
# Assuming apps.api.services structure.
from ..ssis_parser import SSISParser
import traceback

class SSISDriver(IBaseDriver):
    """
    Driver for Microsoft SQL Server Integration Services (SSIS).
    Handles .dtsx packages.
    """

    def can_handle(self, file_extension: str) -> bool:
        return file_extension.lower() == 'dtsx'

    def analyze_content(self, file_path: str, content: str) -> Dict[str, Any]:
        signatures = []
        invocations = []
        metadata = {}
        
        try:
            parser = SSISParser(content)
            summary = parser.get_summary()
            medulla = parser.get_logical_medulla()
            
            signatures.append("SSIS Package (Optimized Scan)")
            if summary.get("executable_count", 0) > 0:
                signatures.append(f"Contains {summary['executable_count']} Executables")
            
            # High-Quality Metadata for Architect Agents
            metadata["logical_medulla"] = medulla
            metadata["connections"] = summary.get("connection_managers", [])
            
            # Invocations (semantic detection)
            for comp in medulla.get("data_flow_logic", []):
                if comp.get("intent") == "SOURCE":
                    invocations.append(f"Reads from: {comp.get('name')}")
                if comp.get("intent") == "DESTINATION":
                    invocations.append(f"Writes to: {comp.get('name')}")

        except Exception as ssis_err:
            signatures.append(f"SSIS Parse Error: {str(ssis_err)}")
            # We might want to log this properly
            print(f"SSIS Driver Error: {traceback.format_exc()}")

        return {
            "signatures": signatures,
            "invocations": invocations,
            "metadata": metadata
        }

    @property
    def agent_knowledge(self) -> str:
        return """
        ### TECHNOLOGY CONTEXT: SSIS (SQL Server Integration Services)
        - **Format**: XML-based (.dtsx).
        - **Core Components**:
          - **Control Flow**: Executables (Tasks, Containers) that define workflow orchestration.
          - **Data Flow**: Pipelines (Components) that move data buffers (Sources -> Transforms -> Destinations).
        - **Key Constraints**:
          - Lookups are memory-intensive.
          - Scripts (VB/C#) are black boxes requiring special attention.
          - Execute Package Tasks imply dependencies.
        - **Migration Strategy**:
          - **Control Flow** -> Airflow DAGs / Databricks Notebook Workflows.
          - **Data Flow** -> PySpark DataFrames.
          - **Expressions** -> Python f-strings or Column Expressions.
        """
