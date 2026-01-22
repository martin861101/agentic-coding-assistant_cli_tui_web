"""
Plugin System for ARIA
Allows dynamic loading of custom tools and extensions
"""
import importlib
import importlib.util
import inspect
import sys
from pathlib import Path
from typing import List, Dict, Type, Optional
from tools.base import Tool
import logging

logger = logging.getLogger(__name__)

class PluginMetadata:
    """Metadata for a plugin"""
    def __init__(self, name: str, version: str, author: str, description: str):
        self.name = name
        self.version = version
        self.author = author
        self.description = description

class Plugin:
    """Base class for ARIA plugins"""
    
    # Plugin metadata - override in subclasses
    metadata = PluginMetadata(
        name="BasePlugin",
        version="1.0.0",
        author="Unknown",
        description="Base plugin class"
    )
    
    def __init__(self):
        self.enabled = True
    
    def on_load(self):
        """Called when plugin is loaded"""
        pass
    
    def on_unload(self):
        """Called when plugin is unloaded"""
        pass
    
    def get_tools(self) -> List[Tool]:
        """Return list of tools provided by this plugin"""
        return []
    
    def on_message(self, message: str) -> Optional[str]:
        """
        Hook called for every user message
        Can return a response to intercept the message
        """
        return None

class PluginManager:
    """Manages plugin loading, unloading, and lifecycle"""
    
    def __init__(self, plugins_dir: Path):
        self.plugins_dir = plugins_dir
        self.plugins: Dict[str, Plugin] = {}
        self.loaded_modules: Dict[str, any] = {}
        
        # Create plugins directory if it doesn't exist
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        
        # Create example plugin if directory is empty
        self._create_example_plugin()
    
    def _create_example_plugin(self):
        """Create an example plugin to demonstrate the system"""
        example_file = self.plugins_dir / "example_plugin.py"
        if not example_file.exists():
            example_code = '''"""
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
'''
            with open(example_file, 'w', encoding='utf-8') as f:
                f.write(example_code)
            logger.info(f"Created example plugin at {example_file}")
    
    def discover_plugins(self) -> List[Path]:
        """Discover all Python files in plugins directory"""
        return list(self.plugins_dir.glob("*.py"))
    
    def load_plugin(self, plugin_path: Path) -> bool:
        """
        Load a plugin from a file
        
        Args:
            plugin_path: Path to the plugin file
            
        Returns:
            True if loaded successfully
        """
        try:
            plugin_name = plugin_path.stem
            
            # Load the module
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if spec is None or spec.loader is None:
                logger.error(f"Could not load spec for {plugin_path}")
                return False
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)
            
            # Get the plugin instance
            if not hasattr(module, 'load_plugin'):
                logger.error(f"Plugin {plugin_name} missing load_plugin() function")
                return False
            
            plugin_instance = module.load_plugin()
            
            if not isinstance(plugin_instance, Plugin):
                logger.error(f"load_plugin() must return a Plugin instance")
                return False
            
            # Store plugin
            self.plugins[plugin_name] = plugin_instance
            self.loaded_modules[plugin_name] = module
            
            # Call lifecycle hook
            plugin_instance.on_load()
            
            logger.info(f"Loaded plugin: {plugin_instance.metadata.name} v{plugin_instance.metadata.version}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_path}: {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin"""
        if plugin_name not in self.plugins:
            return False
        
        try:
            plugin = self.plugins[plugin_name]
            plugin.on_unload()
            
            # Remove from registry
            del self.plugins[plugin_name]
            if plugin_name in self.loaded_modules:
                del sys.modules[plugin_name]
                del self.loaded_modules[plugin_name]
            
            logger.info(f"Unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_name}: {e}")
            return False
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin"""
        if plugin_name not in self.loaded_modules:
            return False
        
        plugin_path = self.plugins_dir / f"{plugin_name}.py"
        self.unload_plugin(plugin_name)
        return self.load_plugin(plugin_path)
    
    def load_all_plugins(self):
        """Load all discovered plugins"""
        plugins = self.discover_plugins()
        loaded_count = 0
        
        for plugin_path in plugins:
            if self.load_plugin(plugin_path):
                loaded_count += 1
        
        logger.info(f"Loaded {loaded_count}/{len(plugins)} plugins")
        return loaded_count
    
    def get_all_tools(self) -> List[Tool]:
        """Get all tools from all loaded plugins"""
        tools = []
        for plugin in self.plugins.values():
            if plugin.enabled:
                tools.extend(plugin.get_tools())
        return tools
    
    def process_message_hooks(self, message: str) -> Optional[str]:
        """
        Run message through all plugin hooks
        Returns first non-None response
        """
        for plugin in self.plugins.values():
            if plugin.enabled:
                response = plugin.on_message(message)
                if response is not None:
                    return response
        return None
    
    def list_plugins(self) -> List[Dict[str, any]]:
        """List all loaded plugins with metadata"""
        return [
            {
                "name": plugin.metadata.name,
                "version": plugin.metadata.version,
                "author": plugin.metadata.author,
                "description": plugin.metadata.description,
                "enabled": plugin.enabled,
                "internal_name": name
            }
            for name, plugin in self.plugins.items()
        ]
    
    def enable_plugin(self, plugin_name: str):
        """Enable a plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True
    
    def disable_plugin(self, plugin_name: str):
        """Disable a plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False
