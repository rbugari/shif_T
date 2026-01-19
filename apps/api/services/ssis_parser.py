from lxml import etree
import hashlib
import json
from typing import Dict, List, Any

class SSISParser:
    """Parses .dtsx (SSIS) XML files to extract semantic structure."""
    
    def __init__(self, content: str):
        self.content = content
        self.tree = etree.fromstring(content.encode('utf-8'))
        self.namespaces = {
            'DTS': 'www.microsoft.com/SqlServer/Dts',
            'SQLTask': 'www.microsoft.com/sqlserver/dts/tasks/sqltask'
        }

    def get_summary(self) -> Dict[str, Any]:
        """Returns a high-level summary of the package."""
        return {
            "creator_name": self.tree.xpath('//@DTS:CreatorName', namespaces=self.namespaces),
            "version_id": self.tree.xpath('//@DTS:VersionID', namespaces=self.namespaces),
            "executable_count": len(self.tree.xpath('//DTS:Executable', namespaces=self.namespaces)),
            "connection_managers": self.get_connection_managers()
        }

    def get_connection_managers(self) -> List[Dict[str, str]]:
        """Extracts connection manager details."""
        connections = []
        for conn in self.tree.xpath('//DTS:ConnectionManager', namespaces=self.namespaces):
            connections.append({
                "name": conn.get(f'{{{self.namespaces["DTS"]}}}ObjectName'),
                "id": conn.get(f'{{{self.namespaces["DTS"]}}}DTSID'),
                "connection_string": self.tree.xpath(f'.//DTS:Property[@DTS:Name="ConnectionString"]/text()', namespaces=self.namespaces)
            })
        return connections

    def extract_executables(self) -> List[Dict[str, Any]]:
        """Extracts control flow executables and their types."""
        execs = []
        for ex in self.tree.xpath('//DTS:Executable', namespaces=self.namespaces):
            execs.append({
                "id": ex.get(f'{{{self.namespaces["DTS"]}}}DTSID'),
                "name": ex.get(f'{{{self.namespaces["DTS"]}}}ObjectName'),
                "type": ex.get(f'{{{self.namespaces["DTS"]}}}ExecutableType'),
                "description": ex.get(f'{{{self.namespaces["DTS"]}}}Description')
            })
        return execs

    def extract_precedence_constraints(self) -> List[Dict[str, str]]:
        """Extracts relationships between executables."""
        constraints = []
        for pc in self.tree.xpath('//DTS:PrecedenceConstraint', namespaces=self.namespaces):
            constraints.append({
                "source": pc.get(f'{{{self.namespaces["DTS"]}}}From'),
                "target": pc.get(f'{{{self.namespaces["DTS"]}}}To'),
                "id": pc.get(f'{{{self.namespaces["DTS"]}}}DTSID')
            })
        return constraints

    @staticmethod
    def get_hash(content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()

    def get_logical_medulla(self) -> Dict[str, Any]:
        """
        Returns the 'spinal cord' of the ETL process, stripped of all XML/Layout noise.
        This is the primary input for the high-quality Architect Agent.
        """
        return {
            "summary": self.get_summary(),
            "data_flow_logic": self.get_data_flow_components(),
            "control_flow_topology": self.extract_executables(),
            "constraints": self.extract_precedence_constraints()
        }

    def get_data_flow_components(self) -> List[Dict[str, Any]]:
        """
        Surgically extracts components from Data Flow Tasks.
        Focuses on Intent (Source/Lookup/Dest) and Logic (SQL/Mappings).
        """
        components = []
        for comp in self.tree.xpath('//*[local-name()="component"]'):
            ref_id = comp.get('refId') 
            name = comp.get('name')
            contact_info = comp.get('contactInfo') or ""
            
            # Identify Component Intent
            comp_type = "UNKNOWN"
            if any(x in contact_info or x in name for x in ["Lookup", "Búsqueda"]):
                comp_type = "LOOKUP"
            elif any(x in contact_info or x in name for x in ["Source", "Origen"]):
                comp_type = "SOURCE"
            elif any(x in contact_info or x in name for x in ["Destination", "Destino"]):
                comp_type = "DESTINATION"
            elif "Derived column" in contact_info.lower():
                comp_type = "TRANSFORMATION_DERIVED"
            
            # Extract SQL / Table Logic (The 'Spine')
            logic = {}
            for prop in comp.xpath('.//*[local-name()="property"]'):
                p_name = prop.get('name')
                if p_name in ["SqlCommand", "OpenRowset", "TableOrViewName", "SqlStatementSource"]:
                    logic[p_name] = prop.text.strip() if prop.text else ""

            # Extract Column Mappings (The 'Nerves')
            mappings = []
            for input_col in comp.xpath('.//*[local-name()="inputColumn"]'):
                mappings.append({
                    "source": input_col.get("externalMetadataColumnId"),
                    "target": input_col.get("name"),
                    "usage": "INPUT"
                })
            for output_col in comp.xpath('.//*[local-name()="outputColumn"]'):
                 mappings.append({
                    "name": output_col.get("name"),
                    "usage": "OUTPUT"
                })

            components.append({
                "intent": comp_type,
                "name": name,
                "logic": logic,
                "mappings": mappings,
                "ref_id": ref_id
            })
            
        return components

