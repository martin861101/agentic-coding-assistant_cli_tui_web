"""
Documentation specialist agent
"""
from .base import Agent, AgentTask, AgentResponse, AgentCapability
import logging

logger = logging.getLogger(__name__)

class DocumentationAgent(Agent):
    """Specialized agent for generating documentation"""
    
    def __init__(self, llm_interface):
        super().__init__("DocumentationAgent", llm_interface)
        self.capabilities = [AgentCapability.DOCUMENTATION]
        
        self.system_prompt = """You are a technical documentation expert specializing in:

1. Clear, comprehensive docstrings
2. README files and user guides
3. API documentation
4. Code comments that add value
5. Architecture documentation

Your documentation should:
- Be clear and concise
- Include examples where helpful
- Follow language-specific conventions
- Explain the "why" not just the "what"
- Be properly formatted (Markdown, reStructuredText, etc.)

Focus on making code accessible to other developers."""
    
    def can_handle(self, task: AgentTask) -> float:
        """Determine if this is a documentation task"""
        keywords = ['document', 'docstring', 'readme', 'comment', 'explain', 'api doc', 'guide']
        
        if task.task_type == AgentCapability.DOCUMENTATION:
            return 1.0
        
        content_lower = task.content.lower()
        matches = sum(1 for kw in keywords if kw in content_lower)
        
        has_code = 'code' in task.context or 'file_content' in task.context
        
        confidence = (matches / len(keywords)) * 0.7
        if has_code:
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def process(self, task: AgentTask) -> AgentResponse:
        """Process documentation task"""
        try:
            code = task.context.get('code', task.context.get('file_content', ''))
            file_type = task.context.get('file_type', 'code')
            
            prompt = f"""Generate documentation for:

{code if code else task.content}

User request: {task.content}

Provide comprehensive documentation."""

            full_response = ""
            for token in self.llm.chat(prompt, self.system_prompt):
                full_response += token
            
            return AgentResponse(
                success=True,
                content=full_response,
                confidence=0.9,
                agent_name=self.name,
                metadata={"task_type": "documentation"}
            )
            
        except Exception as e:
            logger.error(f"DocumentationAgent error: {e}")
            return AgentResponse(
                success=False,
                content=f"Error generating documentation: {str(e)}",
                confidence=0.0,
                agent_name=self.name
            )
