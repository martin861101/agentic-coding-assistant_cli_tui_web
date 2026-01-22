"""
Auto-Claude Bridge Module
=========================

Integration layer that brings the Auto-Claude autonomous coding framework
into the ARIA CLI. This module provides:

- Agent types and tool permissions from Auto-Claude
- Implementation plan system (subtasks, phases, verification)
- Graphiti memory integration
- QA validation loops
- MCP tool server integration
- Runners for spec generation, roadmap, ideation

Architecture:
    ARIA CLI <-> Auto-Claude Bridge <-> Auto-Claude Backend

The bridge provides a clean Python API that wraps the Auto-Claude backend,
adapting it for use with ARIA's existing LLM interface and tool system.
"""

import sys
from pathlib import Path

# Add Auto-Claude backend to path
BACKEND_PATH = Path(__file__).parent.parent / "Auto-Claude" / "apps" / "backend"
if BACKEND_PATH.exists() and str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

__version__ = "1.0.0"

# Lazy imports to avoid circular dependencies
__all__ = [
    # Agent System
    "AutoClaudeAgentCoordinator",
    "AgentType",
    "get_agent_config",
    "get_available_agent_types",
    # Implementation Plan
    "ImplementationPlanManager",
    "WorkflowType",
    "PhaseType",
    "SubtaskStatus",
    "create_implementation_plan",
    # Memory
    "GraphitiMemoryManager",
    "is_graphiti_available",
    # QA System
    "QAValidator",
    "run_qa_validation",
    # MCP Tools
    "MCPToolServer",
    "create_mcp_server",
    # Runners
    "run_spec",
    "run_roadmap",
    "run_ideation",
    "run_autonomous_build",
    # Configuration
    "AutoClaudeConfig",
    "setup_auto_claude",
]


def __getattr__(name):
    """Lazy imports to avoid circular dependencies and speed up import."""
    
    # Agent System
    if name == "AutoClaudeAgentCoordinator":
        from .agents import AutoClaudeAgentCoordinator
        return AutoClaudeAgentCoordinator
    elif name == "AgentType":
        from .agents import AgentType
        return AgentType
    elif name == "get_agent_config":
        from .agents import get_agent_config
        return get_agent_config
    elif name == "get_available_agent_types":
        from .agents import get_available_agent_types
        return get_available_agent_types
    
    # Implementation Plan
    elif name == "ImplementationPlanManager":
        from .implementation import ImplementationPlanManager
        return ImplementationPlanManager
    elif name in ("WorkflowType", "PhaseType", "SubtaskStatus"):
        from .implementation import WorkflowType, PhaseType, SubtaskStatus
        return locals()[name]
    elif name == "create_implementation_plan":
        from .implementation import create_implementation_plan
        return create_implementation_plan
    
    # Memory
    elif name == "GraphitiMemoryManager":
        from .memory import GraphitiMemoryManager
        return GraphitiMemoryManager
    elif name == "is_graphiti_available":
        from .memory import is_graphiti_available
        return is_graphiti_available
    
    # QA System
    elif name == "QAValidator":
        from .qa_system import QAValidator
        return QAValidator
    elif name == "run_qa_validation":
        from .qa_system import run_qa_validation
        return run_qa_validation
    
    # MCP Tools
    elif name == "MCPToolServer":
        from .mcp_tools import MCPToolServer
        return MCPToolServer
    elif name == "create_mcp_server":
        from .mcp_tools import create_mcp_server
        return create_mcp_server
    
    # Runners
    elif name in ("run_spec", "run_roadmap", "run_ideation", "run_autonomous_build"):
        from .runners import run_spec, run_roadmap, run_ideation, run_autonomous_build
        return locals()[name]
    
    # Configuration
    elif name == "AutoClaudeConfig":
        from .config import AutoClaudeConfig
        return AutoClaudeConfig
    elif name == "setup_auto_claude":
        from .config import setup_auto_claude
        return setup_auto_claude
    
    raise AttributeError(f"module 'auto_claude_bridge' has no attribute '{name}'")
