"""
Debugging specialist agent
"""
from .base import Agent, AgentTask, AgentResponse, AgentCapability
import logging

logger = logging.getLogger(__name__)

class DebugAgent(Agent):
    """Specialized agent for debugging and error analysis"""
    
    def __init__(self, llm_interface):
        super().__init__("DebugAgent", llm_interface)
        self.capabilities = [AgentCapability.DEBUGGING]
        
        self.system_prompt = """You are an expert debugger with deep knowledge of:

1. Stack trace analysis and error interpretation
2. Common programming pitfalls and bugs
3. Debugging strategies and techniques
4. Root cause analysis
5. Providing actionable fixes

Your role:
- Analyze errors and stack traces
- Identify the root cause of issues
- Suggest specific fixes with code examples
- Explain why the error occurred
- Provide debugging tips to prevent similar issues

Be precise and practical. Focus on solutions."""
    
    def can_handle(self, task: AgentTask) -> float:
        """Determine if this is a debugging task"""
        keywords = ['debug', 'error', 'exception', 'bug', 'crash', 'fix', 'stack trace', 'traceback']
        
        if task.task_type == AgentCapability.DEBUGGING:
            return 1.0
        
        content_lower = task.content.lower()
        matches = sum(1 for kw in keywords if kw in content_lower)
        
        # Check for error indicators in context
        has_error = any(key in task.context for key in ['error', 'exception', 'traceback', 'stderr'])
        
        confidence = (matches / len(keywords)) * 0.6
        if has_error:
            confidence += 0.4
        
        return min(confidence, 1.0)
    
    def process(self, task: AgentTask) -> AgentResponse:
        """Process debugging task"""
        try:
            error_info = task.context.get('error', '')
            code = task.context.get('code', '')
            traceback = task.context.get('traceback', '')
            
            prompt = f"""Help debug this issue:

User request: {task.content}
"""
            
            if error_info:
                prompt += f"\nError: {error_info}"
            
            if traceback:
                prompt += f"\n\nStack trace:\n```\n{traceback}\n```"
            
            if code:
                prompt += f"\n\nRelevant code:\n```\n{code}\n```"
            
            prompt += "\n\nPlease analyze the issue and provide a solution."
            
            full_response = ""
            for token in self.llm.chat(prompt, self.system_prompt):
                full_response += token
            
            return AgentResponse(
                success=True,
                content=full_response,
                confidence=0.88,
                agent_name=self.name,
                metadata={"task_type": "debugging"}
            )
            
        except Exception as e:
            logger.error(f"DebugAgent error: {e}")
            return AgentResponse(
                success=False,
                content=f"Error during debugging: {str(e)}",
                confidence=0.0,
                agent_name=self.name
            )
