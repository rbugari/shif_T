import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apps.api.services.agent_c_service import AgentCService

def test_rules():
    service = AgentCService()
    
    scenarios = [
        ("pyspark", "SQL_SCRIPT", "sql_pyspark"),
        ("snowpark", "SQL_SCRIPT", "sql_snowpark"),
        ("pyspark", "SSIS_PACKAGE", "ssis_pyspark"),
        ("snowpark", "SSIS_PACKAGE", "ssis_snowpark"),
    ]

    print("--- Verifying Agent C Rule Loading ---")
    
    for target_lang, source_type, expected_file_part in scenarios:
        os.environ["TARGET_LANG"] = target_lang
        rules = service._get_migration_rules(source_type)
        
        print(f"\n[TARGET_LANG={target_lang}, SOURCE={source_type}]")
        if "WARN" in rules:
            print(f"❌ FAILED: {rules}")
        elif "TECHNOLOGY CONTEXT" in rules:
             # Basic check if content looks right
             if target_lang.upper() in rules.upper() or (target_lang == "pyspark" and "DATAFRAMES" in rules.upper()):
                 print(f"✅ SUCCESS: Loaded rules correctly.")
                 print(f"   Snippet: {rules.splitlines()[0]}")
             else:
                 print(f"⚠️  CONTENT MISMATCH? Loaded:\n{rules[:100]}")
        else:
             print(f"❌ FAILED: Unexpected content.\n{rules[:50]}")

if __name__ == "__main__":
    test_rules()
