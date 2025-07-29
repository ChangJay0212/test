"""
English teacher agent implementation with cost monitoring
"""

import time
from typing import Any, Dict

from src.agents.base_agent import BaseAgent
from src.llm_engines.factory import LLMEngineFactory
from src.monitoring.cost_monitor import cost_monitor
from src.tools.calculator import Calculator
from src.tools.weather_check import WeatherCheck
from src.tools.web_search import WebSearchTool
from src.utils.logger import logger


class EnglishTeacherAgent(BaseAgent):
    """
    EnglishTeacherAgent class specialized in English language instruction.
    """

    def __init__(
        self, agent_uuid: str = "english_teacher_001", engine_type: str = None
    ):
        # Initialize LLM engine using factory
        llm_engine = LLMEngineFactory.create_for_agent(
            agent_type="english_teacher", preferred_engine=engine_type
        )

        # Initialize tools
        tools = [WebSearchTool(), Calculator(), WeatherCheck()]

        # Initialize base agent
        super().__init__(
            agent_uuid=agent_uuid,
            agent_type="english_teacher",
            description="English language teacher specialized in grammar, vocabulary, writing, and literature analysis",
            llm_engine=llm_engine,
            tools=tools,
        )

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process message from student and provide English language assistance with cost tracking.

        Args:
            message (Dict[str, Any]): Input message containing student query.

        Returns:
            Dict[str, Any]: Response with English teaching assistance.

        Raises:
            Exception:
                An error occurred while processing the message.
        """
        start_time = time.time()

        try:
            # Extract message content
            user_message = message.get("message", "")
            producer_uuid = message.get("producer_uuid", "")
            request_id = message.get("request_id", "")
            user_id = message.get("user_id", producer_uuid or "anonymous")  # Use producer_uuid as user_id fallback

            if not user_message:
                return {
                    "success": False,
                    "error": "Empty message received",
                    "producer_uuid": producer_uuid,
                }

            logger.info(f"English teacher processing message: {user_message[:50]}...")

            # Create specialized prompt for English teaching
            system_prompt = self.create_english_teacher_prompt()
            full_prompt = (
                f"{system_prompt}\n\nStudent Question: {user_message}\n\nResponse:"
            )

            # Generate response with intelligent tool usage
            response_data = self.generate_response(
                full_prompt, 
                use_tools=True, 
                user_id=user_id,
                request_id=request_id,
                agent_uuid=self.agent_uuid,
                agent_type=self.agent_type
            )

            # Get cost information from LLM engine
            cost_stats = self.llm_engine.get_cost_statistics()

            # Calculate response time
            end_time = time.time()
            response_time = end_time - start_time

            # Log cost information with actual data from LLM engine
            try:
                logger.info(
                    f"Logging cost for request {request_id}: tokens={cost_stats.get('last_request_input_tokens', 0)}+{cost_stats.get('last_request_output_tokens', 0)}"
                )
                cost_monitor.log_request(
                    agent_uuid=self.agent_uuid,
                    agent_type=self.agent_type,
                    request_id=request_id,
                    producer_uuid=producer_uuid,
                    cost_info={
                        "input_tokens": cost_stats.get("last_request_input_tokens", 0),
                        "output_tokens": cost_stats.get(
                            "last_request_output_tokens", 0
                        ),
                        "input_cost": cost_stats.get("last_request_input_cost", 0.0),
                        "output_cost": cost_stats.get("last_request_output_cost", 0.0),
                        "total_cost": cost_stats.get("last_request_total_cost", 0.0),
                    },
                    response_time=response_time,
                    model_name=self.llm_engine.model_name,
                    success=True,
                )
                logger.info(f"Cost logged successfully for request {request_id}")
            except Exception as cost_log_error:
                logger.error(
                    f"Failed to log cost for request {request_id}: {cost_log_error}"
                )
                # Continue with response even if cost logging fails

            return {
                "success": True,
                "response": response_data["content"],
                "agent_type": self.agent_type,
                "agent_uuid": self.agent_uuid,
                "producer_uuid": producer_uuid,
                "request_id": request_id,
                "tools_used": response_data["tools_used"],
                "tool_results": response_data["tool_results"],
                "response_time": response_time,
                "cost_info": {
                    "input_tokens": cost_stats.get("last_request_input_tokens", 0),
                    "output_tokens": cost_stats.get("last_request_output_tokens", 0),
                    "total_tokens": cost_stats.get("last_request_input_tokens", 0)
                    + cost_stats.get("last_request_output_tokens", 0),
                    "input_cost": cost_stats.get("last_request_input_cost", 0.0),
                    "output_cost": cost_stats.get("last_request_output_cost", 0.0),
                    "total_cost": cost_stats.get("last_request_total_cost", 0.0),
                    "model_name": self.llm_engine.model_name,
                },
                "performance_metrics": {
                    "response_time": response_time,
                    "tokens_per_second": (
                        cost_stats.get("last_request_input_tokens", 0)
                        + cost_stats.get("last_request_output_tokens", 0)
                    )
                    / response_time
                    if response_time > 0
                    else 0,
                    "tools_count": len(response_data["tools_used"]),
                },
            }

        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time

            logger.error(f"Error processing message in English teacher: {e}")

            # Log failed request
            cost_monitor.log_request(
                agent_uuid=self.agent_uuid,
                agent_type=self.agent_type,
                request_id=message.get("request_id", ""),
                producer_uuid=message.get("producer_uuid", ""),
                cost_info={"input_tokens": 0, "output_tokens": 0, "total_cost": 0.0},
                response_time=response_time,
                model_name=self.llm_engine.model_name,
                success=False,
                error_message=str(e),
            )

            return {
                "success": False,
                "error": f"Processing failed: {str(e)}",
                "agent_type": self.agent_type,
                "agent_uuid": self.agent_uuid,
                "producer_uuid": message.get("producer_uuid", ""),
                "request_id": message.get("request_id", ""),
                "response_time": response_time,
            }

    def create_english_teacher_prompt(self) -> str:
        """
        Create specialized system prompt for English teaching

        Returns:
            English teacher system prompt
        """
        return """You are an experienced English language teacher. Your specialties include:

- Grammar and syntax analysis
- Vocabulary building and word usage
- Writing improvement and style suggestions
- Literature analysis and interpretation
- Pronunciation and phonetics guidance
- English as a Second Language (ESL) support

Teaching Approach:
- Provide clear, educational explanations
- Use examples to illustrate concepts
- Offer practical exercises when appropriate
- Encourage learning through positive reinforcement
- Break down complex topics into manageable parts
- Adapt your language level to the student's needs

When helping students:
1. First understand what they're asking
2. Provide a clear, helpful explanation
3. Give practical examples
4. Suggest ways to practice or improve
5. Be encouraging and supportive

Remember to be patient, encouraging, and thorough in your explanations."""
