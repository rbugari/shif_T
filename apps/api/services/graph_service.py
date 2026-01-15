from typing import List, Dict, Any

class GraphService:
    """Converts SSIS Parser results into React Flow graph format."""
    
    @staticmethod
    def build_mesh(executables: List[Dict[str, Any]], constraints: List[Dict[str, str]]) -> Dict[str, Any]:
        nodes = []
        edges = []
        
        # 1. Map DTS Executables to Nodes
        for ex in executables:
            nodes.append({
                "id": ex["id"],
                "type": "customNode",
                "data": {
                    "label": ex["name"],
                    "type": ex["type"],
                    "description": ex["description"]
                },
                "position": {"x": 0, "y": 0} # Frontend will handle layout or use simple stack
            })
            
        # 2. Map Precedence Constraints to Edges
        for pc in constraints:
            edges.append({
                "id": pc["id"],
                "source": pc["source"],
                "target": pc["target"],
                "animated": True,
                "style": {"stroke": "#00A9E0", "strokeWidth": 2} # Sopra Light Blue
            })
            
        return {"nodes": nodes, "edges": edges}
