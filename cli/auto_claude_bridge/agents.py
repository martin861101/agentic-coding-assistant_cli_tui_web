"""
Agent System Integration
========================

Bridges Auto-Claude's agent types and tool configurations with ARIA.
Provides a unified interface to the 21+ agent types from the backend.
"""

import sys
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from dataclasses import dataclass

# Try to import from backend
try:
    BACKEND_PATH = Path(__file__).parent.parent / "Auto-Claude" / "apps" / "backend"
    if BACKEND_PATH.exists() and str(BACKEND_PATH) not in sys.path:
        sys.path.insert(0, str(BACKEND_PATH))
    
    from agents.tools_pkg.models import (
        AGENT_CONFIGS,
        BASE_READ_TOOLS,
        BASE_WRITE_TOOLS,
        WEB_TOOLS,
        CONTEXT7_TOOLS,
        LINEAR_TOOLS,
        GRAPHITI_MCP_TOOLS,
        ELECTRON_TOOLS,
        PUPPETEER_TOOLS,
        TOOL_UPDATE_SUBTASK_STATUS,
        TOOL_GET_BUILD_PROGRESS,
        TOOL_RECORD_DISCOVERY,
        TOOL_RECORD_GOTCHA,
        TOOL_GET_SESSION_CONTEXT,
        TOOL_UPDATE_QA_STATUS,
        get_agent_config as _get_agent_config,
        get_required_mcp_servers,
        get_default_thinking_level,
    )
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False
    AGENT_CONFIGS = {}
    BASE_READ_TOOLS = ["Read", "Glob", "Grep"]
    BASE_WRITE_TOOLS = ["Write", "Edit", "Bash"]
    WEB_TOOLS = ["WebFetch", "WebSearch"]


class AgentType(str, Enum):
    """All available Auto-Claude agent types."""
    
    # Spec creation
    SPEC_GATHERER = "spec_gatherer"
    SPEC_RESEARCHER = "spec_researcher"
    SPEC_WRITER = "spec_writer"
    SPEC_CRITIC = "spec_critic"
    SPEC_DISCOVERY = "spec_discovery"
    SPEC_CONTEXT = "spec_context"
    SPEC_VALIDATION = "spec_validation"
    SPEC_COMPACTION = "spec_compaction"
    
    # Build phases
    PLANNER = "planner"
    CODER = "coder"
    
    # QA phases
    QA_REVIEWER = "qa_reviewer"
    QA_FIXER = "qa_fixer"
    
    # Utility phases
    INSIGHTS = "insights"
    MERGE_RESOLVER = "merge_resolver"
    COMMIT_MESSAGE = "commit_message"
    PR_REVIEWER = "pr_reviewer"
    PR_ORCHESTRATOR = "pr_orchestrator_parallel"
    PR_FOLLOWUP = "pr_followup_parallel"
    
    # Analysis
    ANALYSIS = "analysis"
    BATCH_ANALYSIS = "batch_analysis"
    BATCH_VALIDATION = "batch_validation"
    
    # Roadmap & Ideation
    ROADMAP_DISCOVERY = "roadmap_discovery"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    IDEATION = "ideation"


@dataclass
class AgentConfig:
    """Configuration for a specific agent type."""
    
    agent_type: AgentType
    tools: List[str]
    mcp_servers: List[str]
    mcp_servers_optional: List[str]
    auto_claude_tools: List[str]
    thinking_level: str
    
    @property
    def all_tools(self) -> List[str]:
        """Get all tools including Auto-Claude custom tools."""
        return self.tools + self.auto_claude_tools
    
    @property
    def has_write_access(self) -> bool:
        """Check if this agent can write files."""
        write_tools = {"Write", "Edit"}
        return bool(write_tools.intersection(self.tools))
    
    @property
    def has_code_execution(self) -> bool:
        """Check if this agent can execute code."""
        return "Bash" in self.tools
    
    @property
    def has_web_access(self) -> bool:
        """Check if this agent can access the web."""
        return bool({"WebFetch", "WebSearch"}.intersection(self.tools))


def get_available_agent_types() -> List[AgentType]:
    """Get all available agent types."""
    return list(AgentType)


def get_agent_config(agent_type: AgentType | str) -> AgentConfig:
    """
    Get the configuration for a specific agent type.
    
    Args:
        agent_type: The agent type to get config for
        
    Returns:
        AgentConfig with tools, MCP servers, and thinking level
    """
    if isinstance(agent_type, AgentType):
        agent_type_str = agent_type.value
    else:
        agent_type_str = agent_type
    
    if BACKEND_AVAILABLE and agent_type_str in AGENT_CONFIGS:
        config = AGENT_CONFIGS[agent_type_str]
        return AgentConfig(
            agent_type=AgentType(agent_type_str),
            tools=config.get("tools", []),
            mcp_servers=config.get("mcp_servers", []),
            mcp_servers_optional=config.get("mcp_servers_optional", []),
            auto_claude_tools=config.get("auto_claude_tools", []),
            thinking_level=config.get("thinking_default", "medium"),
        )
    
    # Default fallback config
    return AgentConfig(
        agent_type=AgentType(agent_type_str) if agent_type_str in [e.value for e in AgentType] else AgentType.CODER,
        tools=BASE_READ_TOOLS + BASE_WRITE_TOOLS + WEB_TOOLS,
        mcp_servers=["context7"],
        mcp_servers_optional=[],
        auto_claude_tools=[],
        thinking_level="medium",
    )


class AutoClaudeAgentCoordinator:
    """
    Coordinator for Auto-Claude agents.
    
    Manages agent selection and tool configuration based on task type.
    Integrates with ARIA's existing agent system.
    """
    
    def __init__(self, llm_interface=None):
        """
        Initialize the coordinator.
        
        Args:
            llm_interface: ARIA's LLM interface for agent sessions
        """
        self.llm = llm_interface
        self.active_agents: Dict[str, AgentConfig] = {}
        self._load_agents()
    
    def _load_agents(self):
        """Load all available agent configurations."""
        for agent_type in AgentType:
            try:
                config = get_agent_config(agent_type)
                self.active_agents[agent_type.value] = config
            except Exception:
                pass
    
    def get_agent_for_task(self, task_description: str) -> AgentConfig:
        """
        Select the most appropriate agent for a task.
        
        Args:
            task_description: Description of the task to perform
            
        Returns:
            AgentConfig for the best matching agent
        """
        task_lower = task_description.lower()
        
        # Task-to-agent mapping
        if any(word in task_lower for word in ["plan", "design", "architecture"]):
            return get_agent_config(AgentType.PLANNER)
        elif any(word in task_lower for word in ["test", "verify", "qa", "quality"]):
            return get_agent_config(AgentType.QA_REVIEWER)
        elif any(word in task_lower for word in ["fix", "bug", "error", "issue"]):
            return get_agent_config(AgentType.QA_FIXER)
        elif any(word in task_lower for word in ["spec", "requirement", "gather"]):
            return get_agent_config(AgentType.SPEC_GATHERER)
        elif any(word in task_lower for word in ["review", "pr", "pull request"]):
            return get_agent_config(AgentType.PR_REVIEWER)
        elif any(word in task_lower for word in ["roadmap", "strategy"]):
            return get_agent_config(AgentType.ROADMAP_DISCOVERY)
        elif any(word in task_lower for word in ["idea", "brainstorm", "feature"]):
            return get_agent_config(AgentType.IDEATION)
        elif any(word in task_lower for word in ["analyze", "analysis"]):
            return get_agent_config(AgentType.ANALYSIS)
        elif any(word in task_lower for word in ["doc", "document", "readme"]):
            return get_agent_config(AgentType.SPEC_WRITER)
        elif any(word in task_lower for word in ["merge", "conflict"]):
            return get_agent_config(AgentType.MERGE_RESOLVER)
        elif any(word in task_lower for word in ["commit", "message"]):
            return get_agent_config(AgentType.COMMIT_MESSAGE)
        else:
            # Default to coder for implementation tasks
            return get_agent_config(AgentType.CODER)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all available agents with their capabilities."""
        result = []
        for agent_type in AgentType:
            config = get_agent_config(agent_type)
            result.append({
                "name": agent_type.value,
                "thinking_level": config.thinking_level,
                "has_write_access": config.has_write_access,
                "has_code_execution": config.has_code_execution,
                "has_web_access": config.has_web_access,
                "tools": config.tools,
                "mcp_servers": config.mcp_servers,
            })
        return result
    
    def get_tools_for_phase(self, phase: str) -> List[str]:
        """
        Get the appropriate tools for a build phase.
        
        Args:
            phase: Build phase (planning, coding, qa, etc.)
            
        Returns:
            List of tool names to enable
        """
        phase_mapping = {
            "planning": AgentType.PLANNER,
            "coding": AgentType.CODER,
            "qa": AgentType.QA_REVIEWER,
            "review": AgentType.PR_REVIEWER,
        }
        
        agent_type = phase_mapping.get(phase.lower(), AgentType.CODER)
        config = get_agent_config(agent_type)
        return config.all_tools


# Convenience exports
def get_coder_tools() -> List[str]:
    """Get tools available to the coder agent."""
    return get_agent_config(AgentType.CODER).all_tools


def get_planner_tools() -> List[str]:
    """Get tools available to the planner agent."""
    return get_agent_config(AgentType.PLANNER).all_tools


def get_qa_tools() -> List[str]:
    """Get tools available to the QA reviewer agent."""
    return get_agent_config(AgentType.QA_REVIEWER).all_tools
