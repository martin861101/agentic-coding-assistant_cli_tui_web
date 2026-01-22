"""
Base classes for ARIA tools
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class ToolResult(BaseModel):
    """Result from a tool execution"""
    success: bool
    output: Any
    error: Optional[str] = None
    
class Tool(ABC):
    """Base class for all tools"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.description = self.__doc__ or "No description available"
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters"""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """Return the tool's parameter schema"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {}
        }

class ToolRegistry:
    """Registry for all available tools"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool):
        """Register a new tool"""
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self.tools.keys())
    
    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """Get schemas for all tools"""
        return [tool.get_schema() for tool in self.tools.values()]
