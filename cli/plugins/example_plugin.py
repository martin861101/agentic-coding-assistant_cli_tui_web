"""
Example ARIA Plugin
This demonstrates how to create custom plugins for ARIA
"""
from plugin_system import Plugin, PluginMetadata
from tools.base import Tool, ToolResult

class GreetingTool(Tool):
    """A simple greeting tool"""
    
    def execute(self, name: str = "friend") -> ToolResult:
        """Greet someone by name"""
        greeting = f"Hello, {name}! This is a custom plugin tool."
        return ToolResult(success=True, output=greeting)

class ExamplePlugin(Plugin):
    """Example plugin showing how to extend ARIA"""
    
    metadata = PluginMetadata(
        name="Example Plugin",
        version="1.0.0",
        author="ARIA Team",
        description="Demonstrates plugin capabilities"
    )
    
    def on_load(self):
        """Called when plugin loads"""
        print("✅ Example plugin loaded!")
    
    def get_tools(self) -> list:
        """Provide custom tools"""
        return [GreetingTool()]
    
    def on_message(self, message: str):
        """Hook into message processing"""
        # Example: respond to a specific trigger
        if message.lower() == "plugin demo":
            return "🔌 This is a plugin-generated response!"
        return None

# This is required - each plugin must define 'load_plugin()'
def load_plugin():
    return ExamplePlugin()
