"""
Chinese teacher agent implementation
"""
from typing import Dict, Any
from agents.base_agent import BaseAgent
from llm_engines.factory import LLMEngineFactory
from tools.web_search import WebSearchTool
from tools.calculator import Calculator
from tools.weather_check import WeatherCheck
from core.logger import logger


class ChineseTeacherAgent(BaseAgent):
    """
    Chinese teacher agent specialized in Chinese language and literature
    """
    
    def __init__(self, agent_uuid: str = "chinese_teacher_001", engine_type: str = None):
        # Initialize LLM engine using factory
        llm_engine = LLMEngineFactory.create_for_agent(
            agent_type="chinese_teacher", 
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
            agent_type="chinese_teacher",
            description="Chinese language teacher specialized in literature, writing, poetry, and cultural context",
            llm_engine=llm_engine,
            tools=tools
        )
    
    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process message from student and provide Chinese language assistance
        
        Args:
            message: Input message containing student query
            
        Returns:
            Response dictionary with teaching assistance
        """
        try:
            # Extract message content
            user_message = message.get('message', '')
            producer_uuid = message.get('producer_uuid', '')
            
            if not user_message:
                return {
                    "success": False,
                    "error": "Empty message received",
                    "producer_uuid": producer_uuid
                }
            
            logger.info(f"Chinese teacher processing message: {user_message[:50]}...")
            
            # Create specialized prompt for Chinese teaching
            system_prompt = self.create_chinese_teacher_prompt()
            full_prompt = f"{system_prompt}\n\nStudent Question: {user_message}\n\nResponse:"
            
            # Generate response
            response = self.generate_response(full_prompt, use_tools=True)
            
            # Check if web search might be helpful for cultural or historical topics
            if self._should_use_web_search(user_message):
                search_result = self.execute_tool("web_search", {"query": user_message})
                if search_result.get("success"):
                    search_info = self._format_search_results(search_result)
                    response += f"\n\n補充資料 (Additional Information):\n{search_info}"
            
            return {
                "success": True,
                "response": response,
                "agent_type": self.agent_type,
                "agent_uuid": self.agent_uuid,
                "producer_uuid": producer_uuid,
                "tools_used": ["web_search"] if self._should_use_web_search(user_message) else []
            }
            
        except Exception as e:
            logger.error(f"Error processing message in Chinese teacher: {e}")
            return {
                "success": False,
                "error": f"Processing failed: {str(e)}",
                "agent_type": self.agent_type,
                "agent_uuid": self.agent_uuid,
                "producer_uuid": message.get('producer_uuid', '')
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
    
    def _should_use_web_search(self, message: str) -> bool:
        """
        Determine if web search would be helpful for the query
        
        Args:
            message: Student message
            
        Returns:
            True if web search should be used
        """
        # Use web search for historical context, cultural topics, or specific literary works
        search_keywords = [
            "歷史", "文化", "背景", "作者", "詩人", "朝代", "典故", "成語來源",
            "history", "culture", "author", "poet", "dynasty", "classical", 
            "contemporary chinese", "taiwan literature", "cultural significance"
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
            return "我查找了相關資料，但目前未能找到合適的補充資訊。(I searched for additional information but couldn't find relevant results at the moment.)"
        
        results = search_result["results"][:3]  # Limit to top 3 results
        formatted_results = []
        
        for i, result in enumerate(results, 1):
            title = result.get("title", "Unknown Title")
            snippet = result.get("snippet", "No description available")
            formatted_results.append(f"{i}. {title}\n   {snippet}")
        
        return "\n\n".join(formatted_results)
