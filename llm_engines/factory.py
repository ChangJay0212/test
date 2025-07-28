"""
LLM Engine Factory for creating different types of LLM engines
"""
import os
from typing import Dict, Any
from llm_engines.base_engine import BaseLLMEngine
from llm_engines.gemini_engine import GeminiEngine
from llm_engines.ollama_engine import OllamaEngine
from core.logger import logger
import config.settings as settings


class LLMEngineFactory:
    """
    LLMEngineFactory class for creating LLM engine instances.
    """
    
    # Available engine types
    SUPPORTED_ENGINES = {
        'gemini': GeminiEngine,
        'ollama': OllamaEngine
    }
    
    @classmethod
    def create_engine(cls, engine_type: str = None, **kwargs) -> BaseLLMEngine:
        """
        Create an LLM engine instance based on type.
        
        Args:
            engine_type (str, optional): Type of engine ('gemini', 'ollama'). Defaults to None.
            **kwargs: Additional parameters for engine initialization.
            
        Returns:
            BaseLLMEngine: Initialized LLM engine instance.

        Raises:
            Exception:
                An error occurred while creating the engine.
        """
        # Default engine selection
        if engine_type is None:
            engine_type = os.getenv('DEFAULT_LLM_ENGINE', 'gemini')
        
        engine_type = engine_type.lower()
        
        if engine_type not in cls.SUPPORTED_ENGINES:
            logger.error(f"Unsupported engine type: {engine_type}")
            logger.info(f"Supported engines: {list(cls.SUPPORTED_ENGINES.keys())}")
            logger.info("Falling back to Gemini engine")
            engine_type = 'gemini'
        
        try:
            # Create engine with appropriate configuration
            if engine_type == 'gemini':
                return cls._create_gemini_engine(**kwargs)
            elif engine_type == 'ollama':
                return cls._create_ollama_engine(**kwargs)
            
        except Exception as e:
            logger.error(f"Failed to create {engine_type} engine: {e}")
            
            # Fallback to another engine if possible
            if engine_type != 'gemini':
                logger.info("Attempting fallback to Gemini engine")
                try:
                    return cls._create_gemini_engine(**kwargs)
                except Exception as fallback_error:
                    logger.error(f"Fallback to Gemini also failed: {fallback_error}")
            
            raise Exception("Could not create any LLM engine")
    
    @classmethod
    def _create_gemini_engine(cls, **kwargs) -> GeminiEngine:
        """
        Create Gemini engine with configuration.
        
        Args:
            **kwargs: Override parameters.
            
        Returns:
            GeminiEngine: GeminiEngine instance.

        Raises:
            ValueError:
                If Gemini API key is required but not provided.
        """
        model_name = kwargs.get('model_name', getattr(settings, 'GEMINI_MODEL', 'gemini-pro'))
        api_key = kwargs.get('api_key', getattr(settings, 'GEMINI_API_KEY', None))
        
        if not api_key:
            raise ValueError("Gemini API key is required but not provided")
        
        engine = GeminiEngine(model_name=model_name, api_key=api_key)
        logger.info(f"Created Gemini engine with model: {model_name}")
        return engine
    
    @classmethod
    def _create_ollama_engine(cls, **kwargs) -> OllamaEngine:
        """
        Create Ollama engine with configuration.
        
        Args:
            **kwargs: Override parameters.
            
        Returns:
            OllamaEngine: OllamaEngine instance.

        Raises:
            Exception:
                An error occurred while creating the Ollama engine.
        """
        model_name = kwargs.get('model_name', getattr(settings, 'OLLAMA_MODEL', 'llama2'))
        base_url = kwargs.get('base_url', getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434'))
        
        engine = OllamaEngine(model_name=model_name, base_url=base_url)
        logger.info(f"Created Ollama engine with model: {model_name} at {base_url}")
        return engine
    
    @classmethod
    @classmethod
    def get_available_engines(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get information about available engines.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary with engine information.
        """
        engines_info = {}
        
        for engine_type, engine_class in cls.SUPPORTED_ENGINES.items():
            try:
                # Get basic info without initializing
                if engine_type == 'gemini':
                    info = {
                        "name": "Google Gemini",
                        "type": "cloud",
                        "requires_api_key": True,
                        "default_model": getattr(settings, 'GEMINI_MODEL', 'gemini-pro'),
                        "cost_model": "pay-per-token"
                    }
                elif engine_type == 'ollama':
                    info = {
                        "name": "Ollama Local",
                        "type": "local",
                        "requires_api_key": False,
                        "default_model": getattr(settings, 'OLLAMA_MODEL', 'llama2'),
                        "cost_model": "free"
                    }
                else:
                    info = {"name": "Unknown", "type": "unknown"}
                
                engines_info[engine_type] = info
                
            except Exception as e:
                logger.warning(f"Could not get info for engine {engine_type}: {e}")
                engines_info[engine_type] = {
                    "name": f"{engine_type.title()} Engine",
                    "type": "unknown",
                    "status": "unavailable",
                    "error": str(e)
                }
        
        return engines_info
    
    @classmethod
    @classmethod
    def validate_engine_config(cls, engine_type: str) -> Dict[str, Any]:
        """
        Validate configuration for a specific engine type.
        
        Args:
            engine_type (str): Type of engine to validate.
            
        Returns:
            Dict[str, Any]: Dictionary with validation results.

        Raises:
            Exception:
                An error occurred while validating engine configuration.
        """
        engine_type = engine_type.lower()
        
        if engine_type not in cls.SUPPORTED_ENGINES:
            return {
                "valid": False,
                "error": f"Unsupported engine type: {engine_type}",
                "supported_engines": list(cls.SUPPORTED_ENGINES.keys())
            }
        
        try:
            if engine_type == 'gemini':
                api_key = getattr(settings, 'GEMINI_API_KEY', None)
                if not api_key:
                    return {
                        "valid": False,
                        "error": "GEMINI_API_KEY not found in environment variables",
                        "suggestion": "Set GEMINI_API_KEY in your .env file"
                    }
                
                # Try to create a temporary engine to validate
                temp_engine = GeminiEngine(api_key=api_key)
                if not temp_engine.validate_api_key():
                    return {
                        "valid": False,
                        "error": "Invalid Gemini API key",
                        "suggestion": "Check your GEMINI_API_KEY value"
                    }
                
                return {
                    "valid": True,
                    "message": "Gemini engine configuration is valid"
                }
                
            elif engine_type == 'ollama':
                base_url = getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434')
                
                # Try to create a temporary engine to validate
                temp_engine = OllamaEngine(base_url=base_url)
                if not temp_engine.validate_api_key():  # This checks server connection
                    return {
                        "valid": False,
                        "error": f"Cannot connect to Ollama server at {base_url}",
                        "suggestion": "Make sure Ollama is running locally or update OLLAMA_BASE_URL"
                    }
                
                return {
                    "valid": True,
                    "message": "Ollama engine configuration is valid"
                }
                
        except Exception as e:
            return {
                "valid": False,
                "error": f"Configuration validation failed: {str(e)}",
                "suggestion": "Check your environment configuration"
            }
    
    @classmethod
    def create_for_agent(cls, agent_type: str = None, preferred_engine: str = None) -> BaseLLMEngine:
        """
        Create the most appropriate engine for a specific agent type
        
        Args:
            agent_type: Type of agent (e.g., 'english_teacher', 'chinese_teacher')
            preferred_engine: Preferred engine type if specified
            
        Returns:
            Initialized LLM engine instance
        """
        # Agent-specific engine preferences
        agent_engine_preferences = {
            'english_teacher': ['gemini', 'ollama'],  # Prefer Gemini for better English
            'chinese_teacher': ['gemini', 'ollama'],  # Prefer Gemini for multilingual
            'dynamic_assign': ['gemini', 'ollama']    # Prefer Gemini for decision making
        }
        
        # Use preferred engine if specified
        if preferred_engine:
            try:
                return cls.create_engine(preferred_engine)
            except Exception as e:
                logger.warning(f"Failed to create preferred engine {preferred_engine}: {e}")
        
        # Try agent-specific preferences
        if agent_type and agent_type in agent_engine_preferences:
            for engine_type in agent_engine_preferences[agent_type]:
                try:
                    logger.info(f"Trying to validate {engine_type} for {agent_type}")
                    validation = cls.validate_engine_config(engine_type)
                    logger.info(f"Validation result for {engine_type}: {validation}")
                    if validation.get('valid', False):
                        logger.info(f"Creating {engine_type} engine for {agent_type}")
                        return cls.create_engine(engine_type)
                    else:
                        logger.warning(f"{engine_type} validation failed: {validation.get('error', 'Unknown error')}")
                except Exception as e:
                    logger.warning(f"Failed to create {engine_type} for {agent_type}: {e}")
                    continue
        
        # Fallback to any available engine
        logger.info("Trying fallback engines")
        for engine_type in cls.SUPPORTED_ENGINES.keys():
            try:
                logger.info(f"Trying fallback validation for {engine_type}")
                validation = cls.validate_engine_config(engine_type)
                logger.info(f"Fallback validation result for {engine_type}: {validation}")
                if validation.get('valid', False):
                    logger.info(f"Creating fallback {engine_type} engine")
                    return cls.create_engine(engine_type)
                else:
                    logger.warning(f"Fallback {engine_type} validation failed: {validation.get('error', 'Unknown error')}")
            except Exception as e:
                logger.warning(f"Failed to create fallback engine {engine_type}: {e}")
                continue
        
        raise Exception("No available LLM engines could be created")
