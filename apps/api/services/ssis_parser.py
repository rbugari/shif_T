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

    def get_data_flow_components(self) -> List[Dict[str, Any]]:
        """
        Extracts components from Data Flow Tasks (Pipeline).
        Crucial for identifying Lookups and Sources vs Destinations.
        """
        components = []
        # Data Flow namespace usually differs or is inline types, but 'component' tag is standard in pipeline
        # Note: namespace parsing in pipeline XML can be tricky as it's often CDATA or nested.
        # We'll look for the 'component' tag regardless of namespace for robustness in this pass.
        
        # Searching deeply for components
        # In a real .dtsx, Pipeline XML is often inside a wrapper. 
        # For this logic, we search for 'component' elements locally or via generic xpath.
        
        # NOTE: SSIS 2012+ uses 'component' tags with 'contactInfo' that reveals type.
        for comp in self.tree.xpath('//*[local-name()="component"]'):
            ref_id = comp.get('refId') 
            name = comp.get('name')
            contact_info = comp.get('contactInfo') or ""
            
            comp_type = "UNKNOWN"
            if "Lookup" in contact_info or "Lookup" in name:
                comp_type = "LOOKUP"
            elif "Source" in contact_info or "Source" in name:
                comp_type = "SOURCE"
            elif "Destination" in contact_info or "Destination" in name:
                comp_type = "DESTINATION"
            
            # Extract connections (which table/file is it touching?)
            connections = []
            for conn in comp.xpath('.//*[local-name()="connection"]'):
                 connections.append({
                     "connection_manager_id": conn.get('connectionManagerID'),
                     "name": conn.get('name')
                 })
                 
            # Extract properties (like SqlCommand or TableName)
            properties = {}
            for prop in comp.xpath('.//*[local-name()="property"]'):
                prop_name = prop.get('name')
                prop_val = prop.text
                if prop_name in ["OpenRowset", "SqlCommand", "TableOrViewName"]:
                    properties[prop_name] = prop_val

            components.append({
                "ref_id": ref_id,
                "name": name,
                "type": comp_type,
                "connections": connections,
                "properties": properties
            })
            
        return components
