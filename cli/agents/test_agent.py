"""
Test generation specialist agent
"""
from .base import Agent, AgentTask, AgentResponse, AgentCapability
import logging

logger = logging.getLogger(__name__)

class TestGenerationAgent(Agent):
    """Specialized agent for generating unit tests"""
    
    def __init__(self, llm_interface):
        super().__init__("TestGenerationAgent", llm_interface)
        self.capabilities = [AgentCapability.TESTING]
        
        self.system_prompt = """You are a testing expert specializing in:

1. Unit test generation (pytest, unittest, jest, etc.)
2. Test-driven development (TDD)
3. Edge case identification
4. Mocking and fixtures
5. Test coverage and quality

Generate tests that:
- Cover normal cases and edge cases
- Are well-organized and readable
- Use appropriate assertions
- Include helpful test names
- Follow testing best practices
- Use proper mocking when needed

Provide complete, runnable tests with explanations."""
    
    def can_handle(self, task: AgentTask) -> float:
        """Determine if this is a test generation task"""
        keywords = ['test', 'unittest', 'pytest', 'jest', 'coverage', 'tdd', 'mock']
        
        if task.task_type == AgentCapability.TESTING:
            return 1.0
        
        content_lower = task.content.lower()
        matches = sum(1 for kw in keywords if kw in content_lower)
        
        has_code = 'code' in task.context or 'file_content' in task.context
        
        confidence = (matches / len(keywords)) * 0.7
        if has_code:
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def process(self, task: AgentTask) -> AgentResponse:
        """Process test generation task"""
        try:
            code = task.context.get('code', task.context.get('file_content', ''))
            language = task.context.get('language', 'python')
            
            prompt = f"""Generate comprehensive unit tests for the following {language} code:

```
{code}
```

User request: {task.content}

Provide complete, runnable tests with edge cases."""

            full_response = ""
            for token in self.llm.chat(prompt, self.system_prompt):
                full_response += token
            
            return AgentResponse(
                success=True,
                content=full_response,
                confidence=0.87,
                agent_name=self.name,
                metadata={"task_type": "testing", "language": language}
            )
            
        except Exception as e:
            logger.error(f"TestGenerationAgent error: {e}")
            return AgentResponse(
                success=False,
                content=f"Error generating tests: {str(e)}",
                confidence=0.0,
                agent_name=self.name
            )
