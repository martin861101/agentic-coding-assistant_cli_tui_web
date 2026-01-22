"""
LLM Interface with multi-provider support
Supports: Ollama, Gemini, OpenRouter, OpenAI, Anthropic
"""
import os
import re
import json
import logging
from abc import ABC, abstractmethod
from typing import Iterator, Optional, Dict, List, Any

from config import config, LLMProvider, PROVIDER_MODELS, DEFAULT_MODELS

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, model: Optional[str] = None):
        self.model = model or self.get_default_model()
        self.conversation_history: List[Dict[str, str]] = []
    
    @abstractmethod
    def get_default_model(self) -> str:
        """Return the default model for this provider"""
        pass
    
    @abstractmethod
    def chat(self, message: str, system_prompt: Optional[str] = None) -> Iterator[str]:
        """Send a message and stream the response"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available/configured"""
        pass
    
    def switch_model(self, model: str):
        """Switch to a different model"""
        self.model = model
        logger.info(f"Switched to model: {model}")
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_context_size(self) -> int:
        """Return current conversation history size"""
        return len(self.conversation_history)
    
    def _prune_history(self):
        """Remove old messages to stay within context limits"""
        max_messages = config.max_context_messages
        if len(self.conversation_history) > max_messages:
            self.conversation_history = self.conversation_history[-max_messages:]
    
    def _add_to_history(self, user_message: str, assistant_response: str):
        """Add a message exchange to history"""
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": assistant_response})
        self._prune_history()


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider"""
    
    def __init__(self, model: Optional[str] = None, host: Optional[str] = None):
        self.host = host or config.ollama_host
        self._ollama_available = False
        self.client = None
        
        try:
            import ollama
            self.client = ollama.Client(host=self.host)
            self._ollama_available = True
        except ImportError:
            logger.warning("ollama package not installed")
        except Exception as e:
            logger.warning(f"Could not connect to Ollama: {e}")
        
        super().__init__(model)
        
        # Validate model exists
        if self._ollama_available:
            self.model = self._ensure_valid_model(self.model)
    
    def get_default_model(self) -> str:
        return DEFAULT_MODELS.get("ollama", "mistral:latest")
    
    def is_available(self) -> bool:
        return self._ollama_available
    
    def _ensure_valid_model(self, requested_model: str) -> str:
        """Verify the model exists, otherwise find an available one"""
        try:
            available = self.get_available_models()
            if not available:
                return requested_model
            
            for model in available:
                if model == requested_model or model.startswith(requested_model.split(':')[0]):
                    return model
            
            # Use first available
            logger.warning(f"Model '{requested_model}' not found. Using '{available[0]}'")
            return available[0]
        except Exception:
            return requested_model
    
    def chat(self, message: str, system_prompt: Optional[str] = None) -> Iterator[str]:
        if not self._ollama_available:
            yield "Error: Ollama is not available. Make sure Ollama is running."
            return
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.extend(self.conversation_history)
            messages.append({"role": "user", "content": message})
            
            full_response = ""
            stream = self.client.chat(model=self.model, messages=messages, stream=True)
            
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    token = chunk['message']['content']
                    full_response += token
                    yield token
            
            self._add_to_history(message, full_response)
            
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            yield f"\nError: {str(e)}\n"
    
    def get_available_models(self) -> List[str]:
        if not self._ollama_available:
            return PROVIDER_MODELS.get("ollama", [])
        
        try:
            response = self.client.list()
            models = []
            
            if isinstance(response, dict) and 'models' in response:
                for model in response['models']:
                    name = model.get('name') or model.get('model', '')
                    if name:
                        models.append(name)
            elif hasattr(response, 'models'):
                for model in response.models:
                    if hasattr(model, 'model'):
                        models.append(model.model)
                    elif hasattr(model, 'name'):
                        models.append(model.name)
                    else:
                        model_str = str(model)
                        match = re.search(r"model='([^']+)'", model_str)
                        if match:
                            models.append(match.group(1))
            
            return models if models else PROVIDER_MODELS.get("ollama", [])
        except Exception as e:
            logger.error(f"Error listing Ollama models: {e}")
            return PROVIDER_MODELS.get("ollama", [])


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API provider"""
    
    def __init__(self, model: Optional[str] = None):
        # config.py already loads .env at import time
        self.api_key = config.gemini_api_key
        self._available = False
        self.genai = None
        
        if self.api_key and len(self.api_key.strip()) > 0:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.genai = genai
                self._available = True
                logger.info("Gemini API initialized successfully")
            except ImportError:
                logger.warning("google-generativeai package not installed. Run: pip install google-generativeai")
            except Exception as e:
                logger.warning(f"Could not initialize Gemini: {e}")
        else:
            logger.warning("GEMINI_API_KEY not found in environment")
        
        super().__init__(model)
    
    def get_default_model(self) -> str:
        return DEFAULT_MODELS.get("gemini", "gemini-1.5-flash")
    
    def is_available(self) -> bool:
        return self._available
    
    def chat(self, message: str, system_prompt: Optional[str] = None) -> Iterator[str]:
        if not self._available:
            yield "Error: Gemini is not configured. Set GEMINI_API_KEY in .env"
            return
        
        try:
            model = self.genai.GenerativeModel(
                model_name=self.model,
                system_instruction=system_prompt
            )
            
            # Build chat history
            history = []
            for msg in self.conversation_history:
                role = "user" if msg["role"] == "user" else "model"
                history.append({"role": role, "parts": [msg["content"]]})
            
            chat = model.start_chat(history=history)
            response = chat.send_message(message, stream=True)
            
            full_response = ""
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    yield chunk.text
            
            self._add_to_history(message, full_response)
            
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            yield f"\nError: {str(e)}\n"
    
    def get_available_models(self) -> List[str]:
        return PROVIDER_MODELS.get("gemini", [])


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter API provider (access to many models)"""
    
    def __init__(self, model: Optional[str] = None):
        # config.py already loads .env at import time
        self.api_key = config.openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self._available = self.api_key is not None and len(self.api_key.strip()) > 0
        
        super().__init__(model)
    
    def get_default_model(self) -> str:
        return DEFAULT_MODELS.get("openrouter", "meta-llama/llama-3.1-8b-instruct:free")
    
    def is_available(self) -> bool:
        return self._available
    
    def chat(self, message: str, system_prompt: Optional[str] = None) -> Iterator[str]:
        if not self._available:
            yield "Error: OpenRouter is not configured. Set OPENROUTER_API_KEY in .env"
            return
        
        try:
            import httpx
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.extend(self.conversation_history)
            messages.append({"role": "user", "content": message})
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/aria-assistant",
                "X-Title": "ARIA Assistant"
            }
            
            data = {
                "model": self.model,
                "messages": messages,
                "stream": True,
                "temperature": config.temperature
            }
            
            full_response = ""
            with httpx.Client(timeout=60.0) as client:
                with client.stream("POST", f"{self.base_url}/chat/completions", 
                                   headers=headers, json=data) as response:
                    for line in response.iter_lines():
                        if line.startswith("data: "):
                            line = line[6:]
                            if line.strip() == "[DONE]":
                                break
                            try:
                                chunk = json.loads(line)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        full_response += content
                                        yield content
                            except:
                                continue
            
            self._add_to_history(message, full_response)
            
        except ImportError:
            yield "Error: httpx package not installed. Run: pip install httpx"
        except Exception as e:
            logger.error(f"OpenRouter error: {e}")
            yield f"\nError: {str(e)}\n"
    
    def get_available_models(self) -> List[str]:
        return PROVIDER_MODELS.get("openrouter", [])


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider"""
    
    def __init__(self, model: Optional[str] = None):
        # config.py already loads .env at import time
        self.api_key = config.openai_api_key
        self._available = False
        self.client = None
        
        if self.api_key and len(self.api_key.strip()) > 0:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                self._available = True
            except ImportError:
                logger.warning("openai package not installed. Run: pip install openai")
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI: {e}")
        
        super().__init__(model)
    
    def get_default_model(self) -> str:
        return DEFAULT_MODELS.get("openai", "gpt-4o-mini")
    
    def is_available(self) -> bool:
        return self._available
    
    def chat(self, message: str, system_prompt: Optional[str] = None) -> Iterator[str]:
        if not self._available:
            yield "Error: OpenAI is not configured. Set OPENAI_API_KEY in .env"
            return
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.extend(self.conversation_history)
            messages.append({"role": "user", "content": message})
            
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=config.temperature
            )
            
            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
            
            self._add_to_history(message, full_response)
            
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            yield f"\nError: {str(e)}\n"
    
    def get_available_models(self) -> List[str]:
        return PROVIDER_MODELS.get("openai", [])


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude API provider"""
    
    def __init__(self, model: Optional[str] = None):
        # config.py already loads .env at import time
        self.api_key = config.anthropic_api_key
        self._available = False
        self.client = None
        
        if self.api_key and len(self.api_key.strip()) > 0:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
                self._available = True
            except ImportError:
                logger.warning("anthropic package not installed. Run: pip install anthropic")
            except Exception as e:
                logger.warning(f"Could not initialize Anthropic: {e}")
        
        super().__init__(model)
    
    def get_default_model(self) -> str:
        return DEFAULT_MODELS.get("anthropic", "claude-3-haiku-20240307")
    
    def is_available(self) -> bool:
        return self._available
    
    def chat(self, message: str, system_prompt: Optional[str] = None) -> Iterator[str]:
        if not self._available:
            yield "Error: Anthropic is not configured. Set ANTHROPIC_API_KEY in .env"
            return
        
        try:
            messages = []
            for msg in self.conversation_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": message})
            
            with self.client.messages.stream(
                model=self.model,
                max_tokens=4096,
                system=system_prompt or "",
                messages=messages
            ) as stream:
                full_response = ""
                for text in stream.text_stream:
                    full_response += text
                    yield text
                
                self._add_to_history(message, full_response)
            
        except Exception as e:
            logger.error(f"Anthropic error: {e}")
            yield f"\nError: {str(e)}\n"
    
    def get_available_models(self) -> List[str]:
        return PROVIDER_MODELS.get("anthropic", [])


class LLMInterface:
    """
    Unified LLM interface that can switch between providers.
    This is the main class that ARIA uses.
    
    Now with RAG memory support for intelligent context retrieval.
    """
    
    PROVIDERS = {
        "ollama": OllamaProvider,
        "gemini": GeminiProvider,
        "openrouter": OpenRouterProvider,
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
    }
    
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self.provider_name = provider or config.llm_provider.value
        self._provider: BaseLLMProvider = self._create_provider(self.provider_name, model)
        
        # Memory system (lazy loaded)
        self._memory_manager = None
        self._memory_enabled = True
    
    def _create_provider(self, provider_name: str, model: Optional[str] = None) -> BaseLLMProvider:
        """Create a provider instance"""
        provider_class = self.PROVIDERS.get(provider_name, OllamaProvider)
        return provider_class(model)
    
    @property
    def model(self) -> str:
        return self._provider.model
    
    @property
    def conversation_history(self) -> List[Dict[str, str]]:
        return self._provider.conversation_history
    
    def chat(self, message: str, system_prompt: Optional[str] = None) -> Iterator[str]:
        """Send a message and stream the response"""
        return self._provider.chat(message, system_prompt)
    
    def switch_model(self, model: str):
        """Switch to a different model"""
        self._provider.switch_model(model)
    
    def switch_provider(self, provider_name: str, model: Optional[str] = None):
        """Switch to a different provider"""
        if provider_name not in self.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider_name}. Available: {list(self.PROVIDERS.keys())}")
        
        # Preserve conversation history if possible
        old_history = self._provider.conversation_history
        
        self.provider_name = provider_name
        self._provider = self._create_provider(provider_name, model)
        self._provider.conversation_history = old_history
        
        logger.info(f"Switched to provider: {provider_name}, model: {self._provider.model}")
    
    def clear_history(self):
        """Clear conversation history"""
        self._provider.clear_history()
    
    def get_context_size(self) -> int:
        """Return current conversation history size"""
        return self._provider.get_context_size()
    
    def get_available_models(self) -> List[str]:
        """Get available models for current provider"""
        return self._provider.get_available_models()
    
    def is_provider_available(self) -> bool:
        """Check if current provider is available"""
        return self._provider.is_available()
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of all providers and their availability"""
        providers = []
        for name in self.PROVIDERS.keys():
            try:
                # Check if API key is configured for this provider
                if name == "ollama":
                    available = True  # Ollama is always potentially available
                else:
                    available = config.has_api_key(name)
                
                providers.append({
                    "name": name,
                    "available": available,
                    "current": name == self.provider_name,
                    "default_model": DEFAULT_MODELS.get(name, "unknown")
                })
            except:
                providers.append({
                    "name": name,
                    "available": False,
                    "current": name == self.provider_name,
                    "default_model": DEFAULT_MODELS.get(name, "unknown")
                })
        
        return providers
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings - only works with Ollama"""
        if isinstance(self._provider, OllamaProvider) and self._provider.client:
            try:
                response = self._provider.client.embeddings(
                    model=config.embedding_model,
                    prompt=text
                )
                return response['embedding']
            except Exception as e:
                logger.error(f"Error generating embedding: {e}")
        return []
    
    # ========== Memory System Integration ==========
    
    @property
    def memory(self):
        """Get the memory manager (lazy loaded)"""
        if self._memory_manager is None and self._memory_enabled:
            try:
                from memory import MemoryManager
                self._memory_manager = MemoryManager(
                    data_dir=config.data_dir,
                    embedding_model=config.embedding_model,
                    ollama_host=config.ollama_host,
                )
                logger.info("Memory system initialized")
            except Exception as e:
                logger.warning(f"Could not initialize memory system: {e}")
                self._memory_enabled = False
        return self._memory_manager
    
    def enable_memory(self, enabled: bool = True):
        """Enable or disable memory system"""
        self._memory_enabled = enabled
        if not enabled:
            self._memory_manager = None
    
    def index_project(self, project_path, force: bool = False) -> Dict[str, Any]:
        """
        Index a project for RAG retrieval.
        
        Args:
            project_path: Path to project directory
            force: Force re-indexing
            
        Returns:
            Indexing statistics
        """
        if not self.memory:
            return {"status": "skipped", "reason": "memory_disabled"}
        
        from pathlib import Path
        return self.memory.index_project(Path(project_path), force=force)
    
    def chat_with_context(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        project_path = None,
        use_memory: bool = True,
    ) -> Iterator[str]:
        """
        Send a message with automatic context retrieval from memory.
        
        This is the RAG-enhanced version of chat(). It:
        1. Retrieves relevant code snippets from the indexed codebase
        2. Retrieves relevant past conversations
        3. Injects this context into the prompt
        4. Calls the LLM
        5. Stores the conversation for future retrieval
        
        Args:
            message: User's message
            system_prompt: Optional system prompt
            project_path: Current project path for context
            use_memory: Whether to use memory retrieval
            
        Returns:
            Iterator of response tokens
        """
        enhanced_prompt = system_prompt or ""
        
        # Retrieve and inject context
        if use_memory and self.memory and self._memory_enabled:
            try:
                from pathlib import Path
                project = Path(project_path) if project_path else None
                
                # Retrieve relevant context
                context = self.memory.retrieve_context(
                    query=message,
                    project_path=project,
                    max_code_results=5,
                    max_conversation_results=3,
                )
                
                # Add context to prompt
                context_section = context.to_prompt_section(max_tokens=3000)
                if context_section:
                    enhanced_prompt = enhanced_prompt + "\n" + context_section
                    logger.debug(f"Added {context.total_tokens_estimate} tokens of context")
                
            except Exception as e:
                logger.warning(f"Context retrieval failed: {e}")
        
        # Stream response and collect it
        full_response = ""
        for token in self._provider.chat(message, enhanced_prompt):
            full_response += token
            yield token
        
        # Store conversation for future retrieval
        if use_memory and self.memory and self._memory_enabled:
            try:
                self.memory.store_conversation(
                    user_query=message,
                    assistant_response=full_response,
                    metadata={
                        "provider": self.provider_name,
                        "model": self.model,
                    }
                )
            except Exception as e:
                logger.warning(f"Could not store conversation: {e}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        if not self.memory:
            return {"enabled": False}
        
        stats = self.memory.get_stats()
        stats["enabled"] = True
        return stats
    
    def clear_memory(self, what: str = "all"):
        """
        Clear memory stores.
        
        Args:
            what: "all", "codebase", "conversations"
        """
        if self.memory:
            self.memory.clear_memory(what)
