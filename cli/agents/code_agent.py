"""
Code-focused agents for review and refactoring
"""
from .base import Agent, AgentTask, AgentResponse, AgentCapability
import logging

logger = logging.getLogger(__name__)

class CodeReviewAgent(Agent):
    """Specialized agent for code review"""
    
    def __init__(self, llm_interface):
        super().__init__("CodeReviewAgent", llm_interface)
        self.capabilities = [
            AgentCapability.CODE_REVIEW,
            AgentCapability.SECURITY,
            AgentCapability.PERFORMANCE
        ]
        
        self.system_prompt = """You are a senior code reviewer with expertise in software architecture, 
security, and performance optimization. Your role is to:

1. Analyze code for bugs, security vulnerabilities, and performance issues
2. Check for code style and best practices
3. Suggest improvements and optimizations
4. Identify architectural concerns
5. Rate code quality and provide constructive feedback

Be thorough but concise. Focus on meaningful issues, not nitpicks.
Format your response with clear sections: Issues, Suggestions, and Overall Assessment."""
    
    def can_handle(self, task: AgentTask) -> float:
        """Determine if this is a code review task"""
        keywords = ['review', 'check', 'analyze', 'bug', 'security', 'performance', 'quality']
        
        if task.task_type == AgentCapability.CODE_REVIEW:
            return 1.0
        
        # Check for keywords in content
        content_lower = task.content.lower()
        matches = sum(1 for kw in keywords if kw in content_lower)
        
        # Check if there's code in the context
        has_code = 'code' in task.context or 'file_content' in task.context
        
        confidence = (matches / len(keywords)) * 0.7
        if has_code:
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def process(self, task: AgentTask) -> AgentResponse:
        """Process code review task"""
        try:
            # Build prompt
            code = task.context.get('code', task.context.get('file_content', ''))
            
            prompt = f"""Please review the following code:

```
{code}
```

User request: {task.content}

Provide a comprehensive code review."""

            # Get LLM response
            full_response = ""
            for token in self.llm.chat(prompt, self.system_prompt):
                full_response += token
            
            return AgentResponse(
                success=True,
                content=full_response,
                confidence=0.9,
                agent_name=self.name,
                metadata={"task_type": "code_review"}
            )
            
        except Exception as e:
            logger.error(f"CodeReviewAgent error: {e}")
            return AgentResponse(
                success=False,
                content=f"Error during code review: {str(e)}",
                confidence=0.0,
                agent_name=self.name
            )

class RefactoringAgent(Agent):
    """Specialized agent for code refactoring"""
    
    def __init__(self, llm_interface):
        super().__init__("RefactoringAgent", llm_interface)
        self.capabilities = [AgentCapability.REFACTORING]
        
        self.system_prompt = """You are an expert in code refactoring and software design patterns.
Your role is to:

1. Identify code smells and anti-patterns
2. Suggest refactoring strategies
3. Apply SOLID principles and design patterns
4. Improve code readability and maintainability
5. Provide refactored code with explanations

Always explain WHY you're making each change and what benefit it provides.
Maintain the original functionality while improving structure."""
    
    def can_handle(self, task: AgentTask) -> float:
        """Determine if this is a refactoring task"""
        keywords = ['refactor', 'improve', 'clean', 'restructure', 'design pattern', 'solid']
        
        if task.task_type == AgentCapability.REFACTORING:
            return 1.0
        
        content_lower = task.content.lower()
        matches = sum(1 for kw in keywords if kw in content_lower)
        
        has_code = 'code' in task.context or 'file_content' in task.context
        
        confidence = (matches / len(keywords)) * 0.7
        if has_code:
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def process(self, task: AgentTask) -> AgentResponse:
        """Process refactoring task"""
        try:
            code = task.context.get('code', task.context.get('file_content', ''))
            
            prompt = f"""Please refactor the following code:

```
{code}
```

User request: {task.content}

Provide the refactored code with detailed explanations."""

            full_response = ""
            for token in self.llm.chat(prompt, self.system_prompt):
                full_response += token
            
            return AgentResponse(
                success=True,
                content=full_response,
                confidence=0.85,
                agent_name=self.name,
                metadata={"task_type": "refactoring"}
            )
            
        except Exception as e:
            logger.error(f"RefactoringAgent error: {e}")
            return AgentResponse(
                success=False,
                content=f"Error during refactoring: {str(e)}",
                confidence=0.0,
                agent_name=self.name
            )
