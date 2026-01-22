"""
MCP Tool Server Integration
============================

Bridges Auto-Claude's MCP tool system with ARIA.
Provides the custom Auto-Claude tools for build management.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

# Try to import from backend
try:
    BACKEND_PATH = Path(__file__).parent.parent / "Auto-Claude" / "apps" / "backend"
    if BACKEND_PATH.exists() and str(BACKEND_PATH) not in sys.path:
        sys.path.insert(0, str(BACKEND_PATH))
    
    from agents.tools_pkg import (
        create_auto_claude_mcp_server as _create_mcp_server,
        TOOL_UPDATE_SUBTASK_STATUS,
        TOOL_GET_BUILD_PROGRESS,
        TOOL_RECORD_DISCOVERY,
        TOOL_RECORD_GOTCHA,
        TOOL_GET_SESSION_CONTEXT,
        TOOL_UPDATE_QA_STATUS,
    )
    MCP_BACKEND_AVAILABLE = True
except ImportError:
    MCP_BACKEND_AVAILABLE = False
    TOOL_UPDATE_SUBTASK_STATUS = "mcp__auto-claude__update_subtask_status"
    TOOL_GET_BUILD_PROGRESS = "mcp__auto-claude__get_build_progress"
    TOOL_RECORD_DISCOVERY = "mcp__auto-claude__record_discovery"
    TOOL_RECORD_GOTCHA = "mcp__auto-claude__record_gotcha"
    TOOL_GET_SESSION_CONTEXT = "mcp__auto-claude__get_session_context"
    TOOL_UPDATE_QA_STATUS = "mcp__auto-claude__update_qa_status"


class MCPTool:
    """A single MCP tool definition."""
    
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable,
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.handler = handler
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters."""
        try:
            result = self.handler(**kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP tool definition format."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }


class MCPToolServer:
    """
    MCP Tool Server for Auto-Claude.
    
    Provides custom tools for build management:
    - update_subtask_status: Mark subtasks as completed/failed
    - get_build_progress: Get current build progress
    - record_discovery: Record insights for memory
    - record_gotcha: Record common pitfalls
    - get_session_context: Get context for current session
    - update_qa_status: Update QA validation status
    """
    
    def __init__(self, spec_dir: Path, project_dir: Optional[Path] = None):
        """
        Initialize the MCP server.
        
        Args:
            spec_dir: Directory containing the spec
            project_dir: Root project directory
        """
        self.spec_dir = Path(spec_dir)
        self.project_dir = Path(project_dir) if project_dir else self.spec_dir.parent.parent.parent
        self.tools: Dict[str, MCPTool] = {}
        self._register_tools()
    
    def _register_tools(self):
        """Register all Auto-Claude MCP tools."""
        
        # update_subtask_status
        self.tools[TOOL_UPDATE_SUBTASK_STATUS] = MCPTool(
            name=TOOL_UPDATE_SUBTASK_STATUS,
            description="Update the status of a subtask in the implementation plan",
            input_schema={
                "type": "object",
                "properties": {
                    "subtask_id": {"type": "string", "description": "ID of the subtask"},
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed", "failed"],
                        "description": "New status"
                    },
                    "notes": {"type": "string", "description": "Optional notes"},
                },
                "required": ["subtask_id", "status"],
            },
            handler=self._handle_update_subtask_status,
        )
        
        # get_build_progress
        self.tools[TOOL_GET_BUILD_PROGRESS] = MCPTool(
            name=TOOL_GET_BUILD_PROGRESS,
            description="Get the current build progress including completed/pending subtasks",
            input_schema={
                "type": "object",
                "properties": {},
            },
            handler=self._handle_get_build_progress,
        )
        
        # record_discovery
        self.tools[TOOL_RECORD_DISCOVERY] = MCPTool(
            name=TOOL_RECORD_DISCOVERY,
            description="Record a discovery or insight for future reference",
            input_schema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The discovery content"},
                    "category": {
                        "type": "string",
                        "description": "Category (pattern, architecture, api, etc.)"
                    },
                },
                "required": ["content"],
            },
            handler=self._handle_record_discovery,
        )
        
        # record_gotcha
        self.tools[TOOL_RECORD_GOTCHA] = MCPTool(
            name=TOOL_RECORD_GOTCHA,
            description="Record a gotcha or common pitfall encountered",
            input_schema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The gotcha description"},
                },
                "required": ["content"],
            },
            handler=self._handle_record_gotcha,
        )
        
        # get_session_context
        self.tools[TOOL_GET_SESSION_CONTEXT] = MCPTool(
            name=TOOL_GET_SESSION_CONTEXT,
            description="Get context for the current session including previous discoveries",
            input_schema={
                "type": "object",
                "properties": {},
            },
            handler=self._handle_get_session_context,
        )
        
        # update_qa_status
        self.tools[TOOL_UPDATE_QA_STATUS] = MCPTool(
            name=TOOL_UPDATE_QA_STATUS,
            description="Update the QA validation status",
            input_schema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "approved", "rejected", "needs_fixes"],
                        "description": "QA status"
                    },
                    "issues": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of issues found"
                    },
                },
                "required": ["status"],
            },
            handler=self._handle_update_qa_status,
        )
    
    def _handle_update_subtask_status(
        self,
        subtask_id: str,
        status: str,
        notes: str = "",
    ) -> Dict[str, Any]:
        """Handle update_subtask_status tool call."""
        from .implementation import ImplementationPlanManager, SubtaskStatus
        
        manager = ImplementationPlanManager(self.spec_dir)
        success = manager.update_subtask_status(
            subtask_id=subtask_id,
            status=SubtaskStatus(status),
            notes=notes,
        )
        
        return {
            "success": success,
            "subtask_id": subtask_id,
            "new_status": status,
        }
    
    def _handle_get_build_progress(self) -> Dict[str, Any]:
        """Handle get_build_progress tool call."""
        from .implementation import ImplementationPlanManager
        
        manager = ImplementationPlanManager(self.spec_dir)
        return manager.get_progress()
    
    def _handle_record_discovery(
        self,
        content: str,
        category: str = "general",
    ) -> Dict[str, Any]:
        """Handle record_discovery tool call."""
        from .memory import GraphitiMemoryManager
        
        memory = GraphitiMemoryManager(self.spec_dir, self.project_dir)
        success = memory.record_discovery(content, category)
        
        return {
            "success": success,
            "content": content[:100] + "..." if len(content) > 100 else content,
        }
    
    def _handle_record_gotcha(self, content: str) -> Dict[str, Any]:
        """Handle record_gotcha tool call."""
        from .memory import GraphitiMemoryManager
        
        memory = GraphitiMemoryManager(self.spec_dir, self.project_dir)
        success = memory.record_gotcha(content)
        
        return {
            "success": success,
            "content": content[:100] + "..." if len(content) > 100 else content,
        }
    
    def _handle_get_session_context(self) -> Dict[str, Any]:
        """Handle get_session_context tool call."""
        from .memory import GraphitiMemoryManager
        from .implementation import ImplementationPlanManager
        
        # Get memory context
        memory = GraphitiMemoryManager(self.spec_dir, self.project_dir)
        memory_stats = memory.get_stats()
        
        # Get build progress
        plan_manager = ImplementationPlanManager(self.spec_dir)
        progress = plan_manager.get_progress()
        
        # Get next subtask
        next_subtask = plan_manager.get_next_subtask()
        
        return {
            "progress": progress,
            "next_subtask": next_subtask,
            "memory_stats": memory_stats,
        }
    
    def _handle_update_qa_status(
        self,
        status: str,
        issues: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Handle update_qa_status tool call."""
        # Update implementation plan
        plan_file = self.spec_dir / "implementation_plan.json"
        if plan_file.exists():
            try:
                plan = json.loads(plan_file.read_text())
                plan["qa_status"] = status
                if issues:
                    plan["qa_issues"] = issues
                plan_file.write_text(json.dumps(plan, indent=2))
                return {"success": True, "status": status}
            except (json.JSONDecodeError, IOError) as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Implementation plan not found"}
    
    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools."""
        return [tool.to_dict() for tool in self.tools.values()]
    
    def execute_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name."""
        tool = self.get_tool(name)
        if not tool:
            return {"success": False, "error": f"Tool not found: {name}"}
        return tool.execute(**kwargs)


def create_mcp_server(
    spec_dir: Path,
    project_dir: Optional[Path] = None,
) -> MCPToolServer:
    """
    Create an MCP tool server for a spec.
    
    Args:
        spec_dir: Directory containing the spec
        project_dir: Root project directory
        
    Returns:
        Configured MCPToolServer instance
    """
    return MCPToolServer(spec_dir, project_dir)
