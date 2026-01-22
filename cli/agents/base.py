"""
Base classes for ARIA's multi-agent system
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AgentCapability(Enum):
    """Capabilities that agents can have"""
    CODE_REVIEW = "code_review"
    REFACTORING = "refactoring"
    DEBUGGING = "debugging"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    PERFORMANCE = "performance"
    GENERAL = "general"

@dataclass
class AgentTask:
    """A task for an agent to process"""
    task_type: AgentCapability
    content: str
    context: Dict[str, Any]
    priority: int = 1
    
@dataclass
class AgentResponse:
    """Response from an agent"""
    success: bool
    content: str
    confidence: float  # 0.0 to 1.0
    agent_name: str
    metadata: Optional[Dict[str, Any]] = None

class Agent(ABC):
    """Base class for specialized agents"""
    
    def __init__(self, name: str, llm_interface):
        self.name = name
        self.llm = llm_interface
        self.capabilities: List[AgentCapability] = []
        self.system_prompt = ""
    
    @abstractmethod
    def can_handle(self, task: AgentTask) -> float:
        """
        Determine if this agent can handle the task
        
        Returns:
            Confidence score 0.0 to 1.0
        """
        pass
    
    @abstractmethod
    def process(self, task: AgentTask) -> AgentResponse:
        """
        Process a task and return a response
        """
        pass
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Return list of this agent's capabilities"""
        return self.capabilities

class AgentCoordinator:
    """
    Coordinates multiple agents, routing tasks to the most appropriate agent
    """
    
    def __init__(self):
        self.agents: List[Agent] = []
        self.task_queue: List[AgentTask] = []
    
    def register_agent(self, agent: Agent):
        """Register a new agent"""
        self.agents.append(agent)
        logger.info(f"Registered agent: {agent.name} with capabilities: {[c.value for c in agent.capabilities]}")
    
    def route_task(self, task: AgentTask) -> Optional[Agent]:
        """
        Route a task to the most capable agent
        
        Returns:
            The selected agent or None
        """
        best_agent = None
        best_confidence = 0.0
        
        for agent in self.agents:
            confidence = agent.can_handle(task)
            if confidence > best_confidence:
                best_confidence = confidence
                best_agent = agent
        
        if best_confidence > 0.3:  # Minimum confidence threshold
            logger.info(f"Routing task to {best_agent.name} (confidence: {best_confidence:.2f})")
            return best_agent
        
        logger.warning(f"No suitable agent found for task type: {task.task_type}")
        return None
    
    def process_task(self, task: AgentTask) -> Optional[AgentResponse]:
        """
        Process a task by routing it to the appropriate agent
        """
        agent = self.route_task(task)
        
        if agent is None:
            return None
        
        try:
            response = agent.process(task)
            logger.info(f"Agent {agent.name} completed task with confidence {response.confidence:.2f}")
            return response
        except Exception as e:
            logger.error(f"Agent {agent.name} failed to process task: {e}")
            return AgentResponse(
                success=False,
                content=f"Error: {str(e)}",
                confidence=0.0,
                agent_name=agent.name
            )
    
    def get_agent_by_capability(self, capability: AgentCapability) -> List[Agent]:
        """Get all agents with a specific capability"""
        return [agent for agent in self.agents if capability in agent.capabilities]
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents"""
        return [
            {
                "name": agent.name,
                "capabilities": [c.value for c in agent.capabilities]
            }
            for agent in self.agents
        ]
