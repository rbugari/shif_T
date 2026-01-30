from .base_driver import IBaseDriver
from typing import Dict, Any, List
import re

class SQLDriver(IBaseDriver):
    """
    Driver for SQL Scripts (Stored Procedures, Scripts, DDL).
    """

    def can_handle(self, file_extension: str) -> bool:
        return file_extension.lower() == 'sql'

    def analyze_content(self, file_path: str, content: str) -> Dict[str, Any]:
        signatures = []
        invocations = []
        metadata = {}
        
        try:
            content_upper = content.upper()
            if 'CREATE PROCEDURE' in content_upper: signatures.append("Stored Procedure")
            if 'MERGE INTO' in content_upper: signatures.append("Merge Logic")
            
            # --- CODE INSIGHT ---
            metadata["logic_snippet"] = content[:1000] # Capture first 1000 chars

            # --- IO DETECTION ---
            # Sources (FROM/JOIN)
            sources = re.findall(r'FROM\s+([\w\."\[\]]+)|JOIN\s+([\w\."\[\]]+)', content_upper)
            source_tables = [s[0] or s[1] for s in sources]
            metadata["sources"] = list(set(source_tables))
            
            # Targets (INSERT/UPDATE/DELETE)
            targets = re.findall(r'INSERT\s+INTO\s+([\w\."\[\]]+)|UPDATE\s+([\w\."\[\]]+)|DELETE\s+FROM\s+([\w\."\[\]]+)', content_upper)
            target_tables = [t[0] or t[1] or t[2] for t in targets]
            metadata["targets"] = list(set(target_tables))

            # --- DIALECT DETECTION ---
            # Oracle Keywords
            if any(k in content_upper for k in ['DBMS_OUTPUT', 'NOCACHE', 'EXCEPTION WHEN', 'VARCHAR2']):
                signatures.append("Oracle (PL/SQL)")
            
            # MySQL Keywords
            if 'AUTO_INCREMENT' in content_upper or 'LIMIT ' in content_upper or '`' in content:
                signatures.append("MySQL")
            
            # SQL Server Keywords
            if any(k in content_upper for k in ['USE [', 'IDENTITY(', 'PRINT ', 'GO\n']):
                signatures.append("SQL Server (T-SQL)")
                
            # Grep for EXEC (T-SQL Style)
            exec_matches = re.findall(r'EXEC\s+\[?([\w\.]+)\]?', content, re.IGNORECASE)
            invocations.extend([f"Calls SP: {m}" for m in exec_matches])

            # Grep for CALL (MySQL/Oracle Style)
            call_matches = re.findall(r'CALL\s+([\w\.]+)', content, re.IGNORECASE)
            invocations.extend([f"Calls Procedure: {m}" for m in call_matches])
            
        except Exception as e:
            signatures.append(f"SQL Parse Error: {str(e)}")



        return {
            "signatures": signatures,
            "invocations": invocations,
            "metadata": metadata
        }

    @property
    def agent_knowledge(self) -> str:
        return """
        ### TECHNOLOGY CONTEXT: SQL (T-SQL / PL-SQL)
        - **Nature**: Set-based declarative logic + Procedural extensions.
        - **Core Components**: Stored Procedures, Views, Functions, Triggers.
        - **Migration Strategy**:
          - **Select/Transform** -> PySpark SQL / DataFrames.
          - **DDL** -> Delta Table Creation via Spark Catalog.
          - **Cursors/Loops** -> MUST be refactored to vectorised operations (Pandas/UDFs) or mapWithState.
          - **Temp Tables** -> Spark Temporary Views or Cached DataFrames.
        """
