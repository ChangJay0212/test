"""
Dynamic assignment module for routing messages to appropriate agents
"""

from typing import Dict, Optional

from src.agents.registry import agent_registry
from src.llm_engines.factory import LLMEngineFactory
from src.utils.logger import logger


class DynamicAssigner:
    """
    DynamicAssigner class for routing messages to appropriate agents
    when no specific agent is requested.
    """

    def __init__(self, engine_type: str = None):
        self.llm_engine = LLMEngineFactory.create_for_agent(
            agent_type="dynamic_assign", preferred_engine=engine_type
        )

    def assign_agent(self, message: str) -> Optional[str]:
        """
        Dynamically assign an agent based on message content.

        Args:
            message (str): User message to analyze.

        Returns:
            Optional[str]: Topic name for the assigned agent, or None if assignment fails.

        Raises:
            Exception:
                An error occurred while assigning agent.
        """
        try:
            # Get available agents and their descriptions
            agent_descriptions = agent_registry.get_agent_descriptions()

            if not agent_descriptions:
                logger.warning("No agents available for dynamic assignment")
                return None

            # Create prompt for LLM to decide agent assignment
            prompt = self._create_assignment_prompt(message, agent_descriptions)

            # Get LLM response
            response = self.llm_engine.generate_response(prompt)

            # Parse response to get agent type
            assigned_agent_type = self._parse_assignment_response(
                response, agent_descriptions
            )

            if assigned_agent_type:
                # Find topic for the assigned agent type
                for agent_info in agent_registry.list_agents():
                    if agent_info.agent_type == assigned_agent_type:
                        logger.info(
                            f"Dynamic assignment: '{message[:50]}...' -> {assigned_agent_type}"
                        )
                        return agent_info.topic

            logger.warning(f"Failed to assign agent for message: {message[:50]}...")
            return None

        except Exception as e:
            logger.error(f"Error in dynamic assignment: {e}")
            return None

    def _create_assignment_prompt(
        self, message: str, agent_descriptions: Dict[str, str]
    ) -> str:
        """
        Create prompt for LLM to decide agent assignment

        Args:
            message: User message
            agent_descriptions: Available agents and their descriptions

        Returns:
            Formatted prompt string
        """
        agents_info = "\n".join(
            [
                f"- {agent_type}: {description}"
                for agent_type, description in agent_descriptions.items()
            ]
        )

        prompt = f"""You are an intelligent routing system. Based on the user's message, determine which specialist teacher would be most appropriate to help.

Available Teachers:
{agents_info}

User Message: "{message}"

Instructions:
1. Analyze the content and intent of the user's message
2. Choose the most appropriate teacher based on their specialization
3. Respond with ONLY the teacher type (e.g., "english_teacher" or "chinese_teacher")
4. If the message is unclear or could apply to multiple teachers, choose the most likely one
5. Do not provide explanations, just the teacher type

Teacher Type:"""

        return prompt

    def _parse_assignment_response(
        self, response: str, agent_descriptions: Dict[str, str]
    ) -> Optional[str]:
        """
        Parse LLM response to extract assigned agent type

        Args:
            response: LLM response
            agent_descriptions: Available agent types

        Returns:
            Agent type if valid, None otherwise
        """
        try:
            # Clean and normalize response
            response = response.strip().lower()

            # Check if response matches any available agent type
            for agent_type in agent_descriptions.keys():
                if agent_type.lower() in response:
                    return agent_type

            # If no direct match, try to find partial matches
            for agent_type in agent_descriptions.keys():
                agent_parts = agent_type.lower().split("_")
                if any(part in response for part in agent_parts):
                    return agent_type

            logger.warning(f"Could not parse assignment response: {response}")
            return None

        except Exception as e:
            logger.error(f"Error parsing assignment response: {e}")
            return None


# Global dynamic assigner instance
dynamic_assigner = DynamicAssigner()
