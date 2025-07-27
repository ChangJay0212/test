"""
English teacher agent implementation with cost monitoring
"""
import time
from typing import Dict, Any
from agents.base_agent import BaseAgent
from llm_engines.factory import LLMEngineFactory
from tools.web_search import WebSearchTool
from tools.calculator import Calculator
from tools.weather_check import WeatherCheck
from core.logger import logger
from core.cost_monitor import cost_monitor


class EnglishTeacherAgent(BaseAgent):
    """
    English teacher agent specialized in English language instruction
    """
    
    def __init__(self, agent_uuid: str = "english_teacher_001", engine_type: str = None):
        # Initialize LLM engine using factory
        llm_engine = LLMEngineFactory.create_for_agent(
            agent_type="english_teacher", 
            preferred_engine=engine_type
        )
        
        # Initialize tools
        tools = [
            WebSearchTool(),
            Calculator(),
            WeatherCheck()
        ]
        
        # Initialize base agent
        super().__init__(
            agent_uuid=agent_uuid,
            agent_type="english_teacher",
            description="English language teacher specialized in grammar, vocabulary, writing, and literature analysis",
            llm_engine=llm_engine,
            tools=tools
        )
    
    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process message from student and provide English language assistance with cost tracking
        
        Args:
            message: Input message containing student query
            
        Returns:
            Response dictionary with teaching assistance
        """
        start_time = time.time()
        
        try:
            # Extract message content
            user_message = message.get('message', '')
            producer_uuid = message.get('producer_uuid', '')
            request_id = message.get('request_id', '')
            
            if not user_message:
                return {
                    "success": False,
                    "error": "Empty message received",
                    "producer_uuid": producer_uuid
                }
            
            logger.info(f"English teacher processing message: {user_message[:50]}...")
            
            # Create specialized prompt for English teaching
            system_prompt = self.create_english_teacher_prompt()
            full_prompt = f"{system_prompt}\n\nStudent Question: {user_message}\n\nResponse:"
            
            # Generate response
            response = self.generate_response(full_prompt, use_tools=True)
            
            # Get cost information from LLM engine
            cost_stats = self.llm_engine.get_cost_statistics()
            
            # Check if web search might be helpful for complex topics
            tools_used = []
            if self._should_use_web_search(user_message):
                search_result = self.execute_tool("web_search", {"query": user_message})
                if search_result.get("success"):
                    search_info = self._format_search_results(search_result)
                    response += f"\n\nAdditional Information:\n{search_info}"
                    tools_used.append("web_search")
            
            # Calculate response time
            end_time = time.time()
            response_time = end_time - start_time
            
            # Log cost information
            cost_monitor.log_request(
                agent_uuid=self.agent_uuid,
                agent_type=self.agent_type,
                request_id=request_id,
                producer_uuid=producer_uuid,
                cost_info={
                    "input_tokens": 0,  # Will be updated by LLM engine
                    "output_tokens": 0,
                    "total_cost": 0.0
                },
                response_time=response_time,
                model_name=self.llm_engine.model_name,
                success=True
            )
            
            return {
                "success": True,
                "response": response,
                "agent_type": self.agent_type,
                "agent_uuid": self.agent_uuid,
                "producer_uuid": producer_uuid,
                "request_id": request_id,
                "tools_used": tools_used,
                "response_time": response_time,
                "cost_info": {
                    "total_cost": cost_stats.get("total_cost", 0.0),
                    "total_tokens": cost_stats.get("total_tokens", 0)
                }
            }
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            logger.error(f"Error processing message in English teacher: {e}")
            
            # Log failed request
            cost_monitor.log_request(
                agent_uuid=self.agent_uuid,
                agent_type=self.agent_type,
                request_id=message.get('request_id', ''),
                producer_uuid=message.get('producer_uuid', ''),
                cost_info={"input_tokens": 0, "output_tokens": 0, "total_cost": 0.0},
                response_time=response_time,
                model_name=self.llm_engine.model_name,
                success=False,
                error_message=str(e)
            )
            
            return {
                "success": False,
                "error": f"Processing failed: {str(e)}",
                "agent_type": self.agent_type,
                "agent_uuid": self.agent_uuid,
                "producer_uuid": message.get('producer_uuid', ''),
                "request_id": message.get('request_id', ''),
                "response_time": response_time
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
    
    def _should_use_web_search(self, message: str) -> bool:
        """
        Determine if web search would be helpful for the query
        
        Args:
            message: Student message
            
        Returns:
            True if web search should be used
        """
        # Use web search for complex topics, current events, or specific literary works
        search_keywords = [
            "current events", "news", "recent", "latest", "modern literature",
            "contemporary", "famous author", "book analysis", "poem analysis",
            "historical context", "cultural significance", "etymology"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in search_keywords)
    
    def _format_search_results(self, search_result: Dict[str, Any]) -> str:
        """
        Format search results for educational presentation
        
        Args:
            search_result: Search results from web search tool
            
        Returns:
            Formatted search information
        """
        if not search_result.get("success") or not search_result.get("results"):
            return "I searched for additional information but couldn't find relevant results at the moment."
        
        results = search_result["results"][:3]  # Limit to top 3 results
        formatted_results = []
        
        for i, result in enumerate(results, 1):
            title = result.get("title", "Unknown Title")
            snippet = result.get("snippet", "No description available")
            formatted_results.append(f"{i}. {title}\n   {snippet}")
        
        return "\n\n".join(formatted_results)
