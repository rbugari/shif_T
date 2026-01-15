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
