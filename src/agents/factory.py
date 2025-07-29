"""
Agent factory for creating agent instances
"""

import importlib
from typing import Any, Optional

from src.agents.registry import agent_registry
from src.utils.logger import logger


class AgentFactory:
    """
    Factory class for creating agent instances dynamically
    """

    @staticmethod
    def create_agent(agent_uuid: str) -> Optional[Any]:
        """
        Create agent instance dynamically using registry information

        Args:
            agent_uuid: UUID of the agent to create

        Returns:
            Agent instance or None if creation fails
        """
        try:
            # Get agent info from registry
            agent_info = agent_registry.get_agent_by_uuid(agent_uuid)
            if not agent_info:
                logger.error(f"Agent {agent_uuid} not found in registry")
                return None

            # Dynamic import
            module = importlib.import_module(agent_info.module_path)
            agent_class = getattr(module, agent_info.class_name)

            # Create instance
            agent_instance = agent_class()

            logger.info(f"Successfully created agent: {agent_info.agent_type}")
            return agent_instance

        except ImportError as e:
            logger.error(f"Failed to import module {agent_info.module_path}: {e}")
            return None
        except AttributeError as e:
            logger.error(
                f"Class {agent_info.class_name} not found in {agent_info.module_path}: {e}"
            )
            return None
        except Exception as e:
            logger.error(f"Failed to create agent {agent_uuid}: {e}")
            return None


# Global agent factory instance
agent_factory = AgentFactory()
