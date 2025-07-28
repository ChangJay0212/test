"""
Agent registry for managing agent metadata and topic assignments
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from core.logger import logger
import config.settings as settings


@dataclass
class AgentInfo:
    """
    AgentInfo class for agent information in registry.
    """
    agent_uuid: str
    agent_type: str
    description: str
    topic: str
    status: str = "active"


class AgentRegistry:
    """
    AgentRegistry class for managing agent metadata and topic mappings.
    """
    
    def __init__(self):
        self.agents: Dict[str, AgentInfo] = {}
        self.topic_to_agent: Dict[str, str] = {}
        self._initialize_default_agents()
    
    def _initialize_default_agents(self):
        """
        Initialize default agents in the registry.

        """
        default_agents = [
            {
                "agent_uuid": "english_teacher_001",
                "agent_type": "english_teacher",
                "description": "English language teacher specialized in grammar, vocabulary, writing, and literature analysis",
                "topic": settings.TOPIC_ENGLISH_TEACHER
            },
            {
                "agent_uuid": "chinese_teacher_001", 
                "agent_type": "chinese_teacher",
                "description": "Chinese language teacher specialized in literature, writing, poetry, and cultural context",
                "topic": settings.TOPIC_CHINESE_TEACHER
            }
        ]
        
        for agent_data in default_agents:
            agent_info = AgentInfo(**agent_data)
            self.register_agent(agent_info)
    
    def register_agent(self, agent_info: AgentInfo) -> bool:
        """
        Register a new agent in the registry.
        
        Args:
            agent_info (AgentInfo): Agent information to register.
            
        Returns:
            bool: True if registration successful, False otherwise.

        Raises:
            Exception:
                An error occurred while registering the agent.
        """
        try:
            self.agents[agent_info.agent_uuid] = agent_info
            self.topic_to_agent[agent_info.topic] = agent_info.agent_uuid
            logger.info(f"Agent registered: {agent_info.agent_uuid} -> {agent_info.topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to register agent {agent_info.agent_uuid}: {e}")
            return False
    
    def unregister_agent(self, agent_uuid: str) -> bool:
        """
        Unregister an agent from the registry.
        
        Args:
            agent_uuid (str): UUID of agent to unregister.
            
        Returns:
            bool: True if unregistration successful, False otherwise.

        Raises:
            Exception:
                An error occurred while unregistering the agent.
        """
        try:
            if agent_uuid in self.agents:
                agent_info = self.agents[agent_uuid]
                del self.agents[agent_uuid]
                if agent_info.topic in self.topic_to_agent:
                    del self.topic_to_agent[agent_info.topic]
                logger.info(f"Agent unregistered: {agent_uuid}")
                return True
            else:
                logger.warning(f"Agent not found for unregistration: {agent_uuid}")
                return False
        except Exception as e:
            logger.error(f"Failed to unregister agent {agent_uuid}: {e}")
            return False
    
    def get_agent_by_uuid(self, agent_uuid: str) -> Optional[AgentInfo]:
        """
        Get agent information by UUID.
        
        Args:
            agent_uuid (str): Agent UUID.
            
        Returns:
            Optional[AgentInfo]: AgentInfo if found, None otherwise.
        """
        return self.agents.get(agent_uuid)
    
    def get_agent_by_topic(self, topic: str) -> Optional[AgentInfo]:
        """
        Get agent information by topic.
        
        Args:
            topic (str): Topic name.
            
        Returns:
            Optional[AgentInfo]: AgentInfo if found, None otherwise.
        """
        agent_uuid = self.topic_to_agent.get(topic)
        if agent_uuid:
            return self.agents.get(agent_uuid)
        return None
    
    def list_agents(self) -> List[AgentInfo]:
        """
        List all registered agents.
        
        Returns:
            List[AgentInfo]: List of all registered agent information.
        """
        return list(self.agents.values())
    
    def list_topics(self) -> List[str]:
        """
        List all registered topics.
        
        Returns:
            List[str]: List of all registered topic names.
        """
        return list(self.topic_to_agent.keys())
    
    def get_agent_descriptions(self) -> Dict[str, str]:
        """
        Get mapping of agent types to descriptions for dynamic assignment.
        
        Returns:
            Dict[str, str]: Dictionary mapping agent types to descriptions.
        """
        return {
            agent.agent_type: agent.description 
            for agent in self.agents.values()
        }
    
    def update_agent_status(self, agent_uuid: str, status: str) -> bool:
        """
        Update agent status.
        
        Args:
            agent_uuid (str): Agent UUID.
            status (str): New status (active, inactive, error).
            
        Returns:
            bool: True if update successful, False otherwise.

        Raises:
            Exception:
                An error occurred while updating agent status.
        """
        try:
            if agent_uuid in self.agents:
                self.agents[agent_uuid].status = status
                logger.info(f"Agent status updated: {agent_uuid} -> {status}")
                return True
            else:
                logger.warning(f"Agent not found for status update: {agent_uuid}")
                return False
        except Exception as e:
            logger.error(f"Failed to update agent status {agent_uuid}: {e}")
            return False


# Global agent registry instance
agent_registry = AgentRegistry()
