from abc import ABC, abstractmethod
from typing import Dict, Any, List

class IBaseDriver(ABC):
    """
    Abstract Base Class for Knowledge Drivers.
    Each driver encapsulates the logic to detect, parse, and provide LLM context 
    for a specific technology (e.g., SSIS, Oracle, Informatica).
    """

    @abstractmethod
    def can_handle(self, file_extension: str) -> bool:
        """Returns True if this driver can handle the given file extension."""
        pass

    @abstractmethod
    def analyze_content(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Analyzes the file content and returns a dictionary with:
        - signatures: List[str]
        - invocations: List[str]
        - metadata: Dict[str, Any]
        - snippet: str (optional custom snippet logic)
        """
        pass


