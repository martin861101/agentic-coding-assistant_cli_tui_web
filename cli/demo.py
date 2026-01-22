"""
ARIA Demo Script
Showcases all advanced features
"""

DEMO_WELCOME = """
╔═══════════════════════════════════════════════════════════╗
║                    ARIA FEATURE DEMO                      ║
║        Adaptive Real-time Intelligence Assistant          ║
╚═══════════════════════════════════════════════════════════╝

This demo showcases ARIA's advanced capabilities:
  🔌 Plugin System
  🤖 Multi-Agent System  
  🧠 Learning System
"""

DEMO_STEPS = [
    {
        "title": "1️⃣  Basic Commands",
        "commands": [
            "/help",
            "@read aria.py",
            "@ls .",
        ],
        "description": "Basic file operations and navigation"
    },
    {
        "title": "2️⃣  Code Execution",
        "commands": [
            '@exec print("Hello from ARIA!")',
            '@exec import sys; print(f"Python {sys.version}")',
        ],
        "description": "Execute code in multiple languages"
    },
    {
        "title": "3️⃣  Plugin System",
        "commands": [
            "/plugins",
            "plugin demo",  # Triggers example plugin
        ],
        "description": "View and interact with plugins"
    },
    {
        "title": "4️⃣  Multi-Agent System",
        "commands": [
            "/agents",
            "@review",  # Then paste sample code
        ],
        "description": "Specialized agents for different tasks"
    },
    {
        "title": "5️⃣  Agent Examples",
        "sample_interactions": [
            {
                "agent": "@review",
                "sample_code": """
def process_data(data):
    result = []
    for item in data:
        if item:
            result.append(item * 2)
    return result
""",
                "description": "CodeReviewAgent will analyze this code"
            },
            {
                "agent": "@refactor",
                "sample_code": """
class DataManager:
    def __init__(self):
        self.db_host = "localhost"
        self.db_port = 5432
        self.db_name = "mydb"
    
    def connect(self):
        # hardcoded connection
        pass
""",
                "description": "RefactoringAgent suggests dependency injection"
            },
            {
                "agent": "@debug",
                "sample_error": """
Traceback (most recent call last):
  File "app.py", line 42, in process
    result = data['key']
KeyError: 'key'
""",
                "description": "DebugAgent analyzes errors"
            },
            {
                "agent": "@test",
                "sample_code": """
def calculate_discount(price, discount_percent):
    if discount_percent > 100:
        return 0
    return price * (1 - discount_percent / 100)
""",
                "description": "TestGenerationAgent creates unit tests"
            },
            {
                "agent": "@document",
                "sample_code": """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
""",
                "description": "DocumentationAgent adds docstrings"
            }
        ]
    },
    {
        "title": "6️⃣  Learning System",
        "commands": [
            "# Ask a question first",
            "How do I read a JSON file in Python?",
            "# Then provide feedback",
            "/rate 5",
            "/correct Always include error handling in file operations",
            "/learn",
        ],
        "description": "ARIA learns from your feedback"
    },
    {
        "title": "7️⃣  Memory & Context",
        "commands": [
            "/memory",
            "@model llama3",
            "/clear",
        ],
        "description": "Manage conversation context and settings"
    }
]

CREATE_PLUGIN_DEMO = '''
🔧 Creating a Custom Plugin:

Create a file in plugins/weather_plugin.py:

```python
from plugin_system import Plugin, PluginMetadata
from tools.base import Tool, ToolResult
import random

class WeatherTool(Tool):
    """Get weather information"""
    
    def execute(self, city: str = "New York") -> ToolResult:
        # Simulated weather data
        temps = ["☀️ Sunny, 72°F", "⛅ Partly Cloudy, 68°F", "🌧️ Rainy, 55°F"]
        weather = random.choice(temps)
        return ToolResult(
            success=True,
            output=f"Weather in {city}: {weather}"
        )

class WeatherPlugin(Plugin):
    metadata = PluginMetadata(
        name="Weather Plugin",
        version="1.0.0",
        author="ARIA User",
        description="Provides weather information"
    )
    
    def on_load(self):
        print("🌤️  Weather plugin loaded!")
    
    def get_tools(self):
        return [WeatherTool()]
    
    def on_message(self, message: str):
        if "weather" in message.lower():
            return "Use: weather <city> to get weather info"
        return None

def load_plugin():
    return WeatherPlugin()
```

Then reload ARIA or use: /plugin reload weather_plugin
'''

CREATE_AGENT_DEMO = '''
🤖 Creating a Custom Agent:

Add to agents/security_agent.py:

```python
from agents.base import Agent, AgentTask, AgentResponse, AgentCapability

class SecurityAgent(Agent):
    """Specialized security analysis agent"""
    
    def __init__(self, llm_interface):
        super().__init__("SecurityAgent", llm_interface)
        self.capabilities = [AgentCapability.SECURITY]
        
        self.system_prompt = """You are a cybersecurity expert.
        Analyze code for:
        - SQL injection vulnerabilities
        - XSS vulnerabilities
        - Authentication issues
        - Data validation problems
        - Cryptography misuse
        
        Provide specific fixes with secure code examples."""
    
    def can_handle(self, task: AgentTask) -> float:
        keywords = ['security', 'vulnerability', 'exploit', 'attack']
        score = sum(1 for kw in keywords if kw in task.content.lower())
        return min(score / len(keywords), 1.0)
    
    def process(self, task: AgentTask) -> AgentResponse:
        code = task.context.get('code', '')
        prompt = f"Analyze for security issues:\\n\\n{code}\\n\\nUser: {task.content}"
        
        response = ""
        for token in self.llm.chat(prompt, self.system_prompt):
            response += token
        
        return AgentResponse(
            success=True,
            content=response,
            confidence=0.92,
            agent_name=self.name
        )
```

Register in aria.py:
```python
from agents.security_agent import SecurityAgent
# In _register_agents():
self.agent_coordinator.register_agent(SecurityAgent(LLMInterface()))
```
'''

LEARNING_TIPS = """
💡 Learning System Tips:

1. **Provide Specific Corrections:**
   ❌ Bad: "This is wrong"
   ✅ Good: "Always include type hints in Python function signatures"

2. **Rate Consistently:**
   - Use ratings to help ARIA understand quality
   - Rate 1-2 for poor responses
   - Rate 4-5 for helpful responses

3. **Set Preferences:**
   Use corrections to teach preferences:
   - Code style (PEP 8, Google, etc.)
   - Preferred frameworks
   - Documentation style
   - Testing approach

4. **Monitor Learning:**
   Check /learn regularly to see patterns ARIA has learned

5. **Pattern Examples:**
   After 2-3 similar corrections, ARIA will:
   - Recognize the pattern
   - Adjust future responses
   - Show learned preferences in /learn
"""

WORKFLOW_EXAMPLES = """
🎯 Common Workflows:

**1. Code Review Workflow:**
   @read myfile.py
   @review for security and performance
   /rate 5
   /correct Always suggest specific performance metrics

**2. Refactoring Workflow:**
   @read legacy_code.py
   @refactor to use modern Python features
   @write refactored.py [paste suggested code]
   
**3. Debug Workflow:**
   [Copy error trace]
   @debug [paste error]
   @read problematic_file.py
   [Get fix suggestion]
   
**4. Documentation Workflow:**
   @read mymodule.py
   @document with Google-style docstrings
   /rate 5
   
**5. Test Generation:**
   @read functions.py
   @test with pytest and edge cases
   @write test_functions.py [paste tests]
   @exec pytest test_functions.py
"""

if __name__ == "__main__":
    print(DEMO_WELCOME)
    print("\n" + "="*60 + "\n")
    
    for step in DEMO_STEPS:
        print(f"\n{step['title']}")
        print(f"{'─' * 60}")
        print(f"📝 {step['description']}\n")
        
        if 'commands' in step:
            print("Commands to try:")
            for cmd in step['commands']:
                print(f"  → {cmd}")
        
        if 'sample_interactions' in step:
            print("\nAgent Examples:")
            for interaction in step['sample_interactions']:
                print(f"\n  {interaction['agent']}")
                print(f"  {interaction['description']}")
                if 'sample_code' in interaction:
                    print(f"  Code:\n{interaction['sample_code']}")
                if 'sample_error' in interaction:
                    print(f"  Error:\n{interaction['sample_error']}")
        
        print()
    
    print("\n" + "="*60)
    print("\n📚 Advanced Customization:\n")
    print(CREATE_PLUGIN_DEMO)
    print("\n" + CREATE_AGENT_DEMO)
    print("\n" + LEARNING_TIPS)
    print("\n" + WORKFLOW_EXAMPLES)
    
    print("\n" + "="*60)
    print("\n✨ Ready to start! Run: python aria.py")
    print("\nFor more details, see:")
    print("  - QUICKSTART.md - Basic usage")
    print("  - ADVANCED_FEATURES.md - Feature deep-dive")
    print("  - PROJECT_STRUCTURE.md - Architecture overview")
    print("\n" + "="*60 + "\n")
