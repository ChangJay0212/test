"""
Chinese teacher agent implementation
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


class ChineseTeacherAgent(BaseAgent):
    """
    ChineseTeacherAgent class specialized in Chinese language and literature.
    """

    def __init__(
        self, agent_uuid: str = "chinese_teacher_001", engine_type: str = None
    ):
        # Initialize LLM engine using factory
        llm_engine = LLMEngineFactory.create_for_agent(
            agent_type="chinese_teacher", preferred_engine=engine_type
        )

        # Initialize tools
        tools = [WebSearchTool(), Calculator(), WeatherCheck()]

        # Initialize base agent
        super().__init__(
            agent_uuid=agent_uuid,
            agent_type="chinese_teacher",
            description="Chinese language teacher specialized in literature, writing, poetry, and cultural context",
            llm_engine=llm_engine,
            tools=tools,
        )

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process message from student and provide Chinese language assistance.

        Args:
            message (Dict[str, Any]): Input message containing student query.

        Returns:
            Dict[str, Any]: Response dictionary with teaching assistance.

        Raises:
            Exception: An error occurred while processing the message.
        """
        try:
            # Extract message content
            user_message = message.get("message", "")
            producer_uuid = message.get("producer_uuid", "")
            request_id = message.get("request_id", f"req_{int(time.time())}")
            user_id = message.get("user_id", producer_uuid or "anonymous")  # Use producer_uuid as user_id fallback

            if not user_message:
                return {
                    "success": False,
                    "error": "Empty message received",
                    "producer_uuid": producer_uuid,
                }

            logger.info(f"Chinese teacher processing message: {user_message[:50]}...")

            # Create specialized prompt for Chinese teaching
            system_prompt = self.create_chinese_teacher_prompt()
            full_prompt = (
                f"{system_prompt}\n\nStudent Question: {user_message}\n\nResponse:"
            )

            # Generate response with intelligent tool usage
            start_time = time.time()
            response_data = self.generate_response(
                full_prompt, 
                use_tools=True, 
                user_id=user_id,
                request_id=request_id,
                agent_uuid=self.agent_uuid,
                agent_type=self.agent_type
            )
            response_time = time.time() - start_time

            # Get cost information from LLM engine
            cost_stats = self.llm_engine.get_cost_statistics()

            # Log cost information
            try:
                request_id = message.get("request_id", f"req_{int(time.time())}")

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
                            "input_tokens": cost_stats.get(
                                "last_request_input_tokens", 0
                            ),
                            "output_tokens": cost_stats.get(
                                "last_request_output_tokens", 0
                            ),
                            "input_cost": cost_stats.get(
                                "last_request_input_cost", 0.0
                            ),
                            "output_cost": cost_stats.get(
                                "last_request_output_cost", 0.0
                            ),
                            "total_cost": cost_stats.get(
                                "last_request_total_cost", 0.0
                            ),
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
            except Exception as e:
                logger.error(f"Error logging cost for Chinese teacher: {e}")

            return {
                "success": True,
                "response": response_data["content"],
                "agent_type": self.agent_type,
                "agent_uuid": self.agent_uuid,
                "producer_uuid": producer_uuid,
                "request_id": message.get("request_id", ""),
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
            logger.error(f"Error processing message in Chinese teacher: {e}")

            # Log failed request cost
            try:
                request_id = message.get("request_id", f"req_{int(time.time())}")
                producer_uuid = message.get("producer_uuid", "")

                logger.info(f"Logging failed request cost for {request_id}")
                cost_monitor.log_request(
                    agent_uuid=self.agent_uuid,
                    agent_type=self.agent_type,
                    request_id=request_id,
                    producer_uuid=producer_uuid,
                    cost_info={},
                    response_time=0.0,
                    model_name="gemini-1.5-flash",
                    success=False,
                    error_message=str(e),
                )
                logger.info(f"Failed request cost logged for {request_id}")
            except Exception as cost_error:
                logger.error(f"Error logging failed request cost: {cost_error}")

            return {
                "success": False,
                "error": f"Processing failed: {str(e)}",
                "agent_type": self.agent_type,
                "agent_uuid": self.agent_uuid,
                "producer_uuid": message.get("producer_uuid", ""),
            }

    def create_chinese_teacher_prompt(self) -> str:
        """
        Create specialized system prompt for Chinese teaching

        Returns:
            Chinese teacher system prompt
        """
        return """You are an experienced Chinese language and literature teacher (國文老師). Your specialties include:

- Classical Chinese literature (古典文學)
- Modern Chinese literature (現代文學) 
- Poetry analysis and appreciation (詩詞鑒賞)
- Writing skills and composition (寫作技巧)
- Character analysis and etymology (文字學)
- Cultural and historical context (文化歷史背景)
- Reading comprehension strategies (閱讀理解)

Teaching Approach:
- Provide clear explanations in both Chinese and English when helpful
- Use traditional teaching methods combined with modern approaches
- Emphasize cultural significance and historical context
- Encourage deep thinking and critical analysis
- Connect literature to contemporary life
- Foster appreciation for Chinese cultural heritage

When helping students:
1. Understand their specific question or learning need
2. Provide comprehensive explanations with examples
3. Include cultural and historical context when relevant
4. Suggest further reading or practice materials
5. Encourage continued exploration of Chinese culture and literature

Be patient, thorough, and inspiring in your teaching approach. Help students develop both language skills and cultural understanding."""
