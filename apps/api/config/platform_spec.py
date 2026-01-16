import os
import json
from typing import Dict, Any

class PlatformSpec:
    """Helper to load the normative platform specification."""
    
    def __init__(self):
        # Default path relative to this file
        # this file is in apps/api/config/
        # json is in apps/api/config/
        self.config_path = os.path.join(os.path.dirname(__file__), "platform_spec.json")

    def load_platform_spec(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            # Fallback to absolute path search if __file__ is unreliable in some contexts
            self.config_path = os.path.join(os.getcwd(), "apps", "api", "config", "platform_spec.json")
            
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Platform Spec not found at {self.config_path}")
            
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)
