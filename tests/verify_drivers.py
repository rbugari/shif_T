import sys
import os
import shutil

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from apps.api.services.discovery_service import DiscoveryService
from apps.api.services.persistence_service import PersistenceService

# Setup Dummy Project
PROJECT_ID = "verify_drivers_test"
PROJECT_PATH = f"c:/proyectos_dev/ShifT/solutions/{PROJECT_ID}"
TRIAGE_PATH = os.path.join(PROJECT_PATH, "Triage")

def setup():
    if os.path.exists(PROJECT_PATH):
        shutil.rmtree(PROJECT_PATH)
    os.makedirs(TRIAGE_PATH)
    
    # Create Dummy SSIS File
    with open(os.path.join(TRIAGE_PATH, "Package.dtsx"), "w", encoding="utf-8") as f:
        f.write("""<?xml version="1.0"?>
<DTS:Executable xmlns:DTS="www.microsoft.com/SqlServer/Dts"
  DTS:refId="Package"
  DTS:CreationDate="1/29/2026 5:00:00 PM"
  DTS:CreationName="SSIS.Package.3"
  DTS:CreatorComputerName="PC"
  DTS:CreatorName="User"
  DTS:DTSID="{DUMMY-GUID}"
  DTS:ExecutableType="SSIS.Package.3"
  DTS:LastModifiedProductVersion="11.0.2100.60"
  DTS:LocaleID="1033"
  DTS:ObjectName="Package"
  DTS:PackageType="5"
  DTS:VersionBuild="1"
  DTS:VersionGUID="{DUMMY-VERSION-GUID}">
  <DTS:Property DTS:Name="PackageFormatVersion">6</DTS:Property>
  <DTS:Executable
    DTS:refId="Package\\Data Flow Task"
    DTS:CreationName="SSIS.Pipeline.3"
    DTS:DTSID="{DUMMY-TASK-GUID}"
    DTS:ExecutableType="SSIS.Pipeline.3"
    DTS:LocaleID="-1"
    DTS:ObjectName="Data Flow Task"
    DTS:TaskContact="Performs high-performance data extraction, transformation and loading;Microsoft Corporation; Microsoft SQL Server; (C) 2007 Microsoft Corporation; All Rights Reserved;http://www.microsoft.com/sql/support/default.asp;1">
      <DTS:ObjectData>
        <pipeline
          version="1">
          <components>
            <component
              refId="Package\\Data Flow Task\\OLE DB Source"
              componentClassID="{165A5430-D5DA-48E8-9F7C-123456789012}"
              contactInfo="OLE DB Source;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved; http://www.microsoft.com/sql/support;7"
              description="OLE DB Source"
              name="OLE DB Source"
              usesDispositions="true"
              version="7">
            </component>
          </components>
        </pipeline>
      </DTS:ObjectData>
  </DTS:Executable>
</DTS:Executable>""")

    # Create Dummy SQL File (Oracle Style)
    with open(os.path.join(TRIAGE_PATH, "Procedure.sql"), "w", encoding="utf-8") as f:
        f.write("""
        CREATE PROCEDURE SP_TEST AS
        BEGIN
            MERGE INTO TargetTable T
            USING SourceTable S ON (T.ID = S.ID)
            WHEN MATCHED THEN UPDATE SET T.Val = S.Val;
        END;
        """)

def verify():
    print("Running DiscoveryService...")
    manifest = DiscoveryService.generate_manifest(PROJECT_ID)
    
    # 1. Check SSIS Detection
    ssis_file = next((f for f in manifest["file_inventory"] if f["name"] == "Package.dtsx"), None)
    if ssis_file and "SSIS Package (Optimized Scan)" in ssis_file["signatures"]:
        print("[PASS] SSIS Driver active and detected package.")
    else:
        print(f"[FAIL] SSIS Detection failed. Found: {ssis_file}")

    # 2. Check SQL/Oracle Detection
    sql_file = next((f for f in manifest["file_inventory"] if f["name"] == "Procedure.sql"), None)
    if sql_file and "Merge Logic" in sql_file["signatures"]:
        print("[PASS] SQL Driver active and detected MERGE logic.")
    else:
        print(f"[FAIL] SQL Detection failed. Found: {sql_file}")

    # 3. Check Context Injection
    context = manifest.get("knowledge_context", "")
    if "TECHNOLOGY CONTEXT: SSIS" in context and "TECHNOLOGY CONTEXT: SQL" in context:
        print("[PASS] Knowledge Context contains both SSIS and SQL/Oracle context.")
    else:
        print(f"[FAIL] Context missing or incomplete. Length: {len(context)}")
        print(f"Context snippet: {context[:200]}...")

if __name__ == "__main__":
    try:
        setup()
        verify()
    except Exception as e:
        print(f"Verification Failed with Error: {e}")
        import traceback
        traceback.print_exc()
