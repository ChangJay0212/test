"""
Abstract base class for agents with cost monitoring
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import time
from core.logger import logger
from core.cost_monitor import cost_monitor
from llm_engines.base_engine import BaseLLMEngine
from tools.base_tool import BaseTool


class BaseAgent(ABC):
    """
    Abstract base class for agents
    Provides common interface and functionality for all agent types
    """
    
    def __init__(self, agent_uuid: str, agent_type: str, description: str, 
                 llm_engine: BaseLLMEngine, tools: List[BaseTool] = None):
        """
        Initialize base agent
        
        Args:
            agent_uuid: Unique identifier for the agent
            agent_type: Type/category of the agent
            description: Description of agent capabilities
            llm_engine: LLM engine instance
            tools: List of available tools
        """
        self.agent_uuid = agent_uuid
        self.agent_type = agent_type
        self.description = description
        self.llm_engine = llm_engine
        self.tools = tools or []
        self.tool_registry = {tool.name: tool for tool in self.tools}
        
        logger.info(f"Agent initialized: {self.agent_uuid} ({self.agent_type})")
    
    @abstractmethod
    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming message and generate response
        
        Args:
            message: Input message dictionary
            
        Returns:
            Response dictionary
        """
        pass
    
    def add_tool(self, tool: BaseTool):
        """
        Add a tool to the agent's toolkit
        
        Args:
            tool: Tool instance to add
        """
        if tool.name not in self.tool_registry:
            self.tools.append(tool)
            self.tool_registry[tool.name] = tool
            logger.info(f"Tool '{tool.name}' added to agent {self.agent_uuid}")
        else:
            logger.warning(f"Tool '{tool.name}' already exists in agent {self.agent_uuid}")
    
    def remove_tool(self, tool_name: str) -> bool:
        """
        Remove a tool from the agent's toolkit
        
        Args:
            tool_name: Name of tool to remove
            
        Returns:
            True if tool was removed, False if not found
        """
        if tool_name in self.tool_registry:
            # Remove from registry
            del self.tool_registry[tool_name]
            # Remove from list
            self.tools = [tool for tool in self.tools if tool.name != tool_name]
            logger.info(f"Tool '{tool_name}' removed from agent {self.agent_uuid}")
            return True
        else:
            logger.warning(f"Tool '{tool_name}' not found in agent {self.agent_uuid}")
            return False
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of available tools with their definitions
        
        Returns:
            List of tool definitions
        """
        return [tool.get_tool_definition() for tool in self.tools]
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific tool with given parameters
        
        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        try:
            if tool_name not in self.tool_registry:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' not found"
                }
            
            tool = self.tool_registry[tool_name]
            
            # Validate parameters
            if not tool.validate_parameters(parameters):
                return {
                    "success": False,
                    "error": f"Invalid parameters for tool '{tool_name}'"
                }
            
            # Execute tool
            result = tool.execute(**parameters)
            logger.info(f"Tool '{tool_name}' executed by agent {self.agent_uuid}")
            return result
            
        except Exception as e:
            logger.error(f"Tool execution error in agent {self.agent_uuid}: {e}")
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}"
            }
    
    def generate_response(self, prompt: str, use_tools: bool = True, **kwargs) -> str:
        """
        Generate response using the agent's LLM engine
        
        Args:
            prompt: Input prompt
            use_tools: Whether to include tools in generation
            **kwargs: Additional parameters for LLM
            
        Returns:
            Generated response
        """
        try:
            if use_tools and self.tools:
                tool_definitions = self.get_available_tools()
                return self.llm_engine.generate_with_tools(prompt, tool_definitions, **kwargs)
            else:
                return self.llm_engine.generate_response(prompt, **kwargs)
        except Exception as e:
            logger.error(f"Response generation error in agent {self.agent_uuid}: {e}")
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get agent information
        
        Returns:
            Dictionary containing agent metadata
        """
        return {
            "agent_uuid": self.agent_uuid,
            "agent_type": self.agent_type,
            "description": self.description,
            "llm_engine": self.llm_engine.get_model_info(),
            "available_tools": [tool.name for tool in self.tools],
            "tool_count": len(self.tools)
        }
    
    def create_system_prompt(self) -> str:
        """
        Create system prompt for the agent
        This method can be overridden by specific agent implementations
        
        Returns:
            System prompt string
        """
        tool_descriptions = ""
        if self.tools:
            tool_list = [f"- {tool.name}: {tool.description}" for tool in self.tools]
            tool_descriptions = "\n\nYou have access to the following tools:\n" + "\n".join(tool_list)
        
        return f"""You are a {self.agent_type} agent.
Description: {self.description}

Your role is to help users with tasks related to your specialization.
Provide helpful, accurate, and detailed responses.{tool_descriptions}

Always be professional, friendly, and educational in your responses."""
