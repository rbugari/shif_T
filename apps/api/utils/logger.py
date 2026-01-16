import os
import sys
import json
from datetime import datetime
from typing import Any, Dict

class ShiftLogger:
    def __init__(self):
        # Read from environment, default to False
        self.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"

    def log(self, message: str, level: str = "INFO", component: str = "System"):
        """Standard log format: [TIMESTAMP] [LEVEL] [COMPONENT] Message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] [{component}] {message}")
        sys.stdout.flush()

    def info(self, message: str, component: str = "System"):
        self.log(message, "INFO", component)

    def warning(self, message: str, component: str = "System"):
        self.log(message, "WARNING", component)

    def error(self, message: str, component: str = "System"):
        self.log(message, "ERROR", component)

    def debug(self, message: str, component: str = "System", data: Any = None):
        """
        Logs verbose debug info ONLY if DEBUG_MODE is True.
        Handles JSON formatting for complex data structures.
        """
        if not self.debug_mode:
            return

        self.log(message, "DEBUG", component)
        
        if data:
            try:
                if isinstance(data, (dict, list)):
                    formatted_data = json.dumps(data, indent=2, default=str)
                    print(f"--- DEBUG DATA ({component}) ---\n{formatted_data}\n-------------------------")
                else:
                    print(f"--- DEBUG DATA ({component}) ---\n{str(data)}\n-------------------------")
            except Exception as e:
                print(f"--- DEBUG DATA ({component}) [Serialization Error] ---\n{str(data)}\n-------------------------")
            
            sys.stdout.flush()

# Singleton instance for easy import
logger = ShiftLogger()
