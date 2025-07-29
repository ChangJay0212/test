"""
Abstract base class for agents with cost monitoring
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from src.llm_engines.base_engine import BaseLLMEngine
from src.tools.base_tool import BaseTool
from src.utils.logger import logger


class BaseAgent(ABC):
    """
    BaseAgent class as abstract base class for agents.
    Provides common interface and functionality for all agent types.
    """

    def __init__(
        self,
        agent_uuid: str,
        agent_type: str,
        description: str,
        llm_engine: BaseLLMEngine,
        tools: List[BaseTool] = None,
    ):
        """
        Initialize base agent.

        Args:
            agent_uuid (str): Unique identifier for the agent.
            agent_type (str): Type/category of the agent.
            description (str): Description of agent capabilities.
            llm_engine (BaseLLMEngine): LLM engine instance.
            tools (List[BaseTool], optional): List of available tools. Defaults to None.
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
        Add a tool to the agent's toolkit.

        Args:
            tool (BaseTool): Tool instance to add.
        """
        if tool.name not in self.tool_registry:
            self.tools.append(tool)
            self.tool_registry[tool.name] = tool
            logger.info(f"Tool '{tool.name}' added to agent {self.agent_uuid}")
        else:
            logger.warning(
                f"Tool '{tool.name}' already exists in agent {self.agent_uuid}"
            )

    def remove_tool(self, tool_name: str) -> bool:
        """
        Remove a tool from the agent's toolkit.

        Args:
            tool_name (str): Name of tool to remove.

        Returns:
            bool: True if tool was removed, False if not found.
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
        Get list of available tools with their definitions.

        Returns:
            List[Dict[str, Any]]: List of tool definitions.
        """
        return [tool.get_tool_definition() for tool in self.tools]

    def execute_tool(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a specific tool with given parameters

        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters

        Returns:
            Tool execution result
        """
        try:
            logger.info(
                f"Agent {self.agent_uuid} attempting to execute tool '{tool_name}' with parameters: {parameters}"
            )

            if tool_name not in self.tool_registry:
                error_msg = f"Tool '{tool_name}' not found in registry"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}

            tool = self.tool_registry[tool_name]
            logger.info(f"Found tool: {tool}")

            # Validate parameters (but be more lenient)
            try:
                if hasattr(tool, "validate_parameters"):
                    is_valid = tool.validate_parameters(parameters)
                    if not is_valid:
                        logger.warning(
                            f"Parameter validation failed for tool '{tool_name}', but proceeding anyway"
                        )
                        # Don't fail here, let the tool handle it
                else:
                    logger.info(
                        f"Tool '{tool_name}' doesn't have validate_parameters method"
                    )
            except Exception as validation_error:
                logger.warning(
                    f"Parameter validation error for tool '{tool_name}': {validation_error}, proceeding anyway"
                )

            # Execute tool
            logger.info(f"Executing tool '{tool_name}' with parameters: {parameters}")
            result = tool.execute(**parameters)

            logger.info(f"Tool '{tool_name}' execution result: {result}")

            if result.get("success", False):
                logger.info(
                    f"Tool '{tool_name}' executed successfully by agent {self.agent_uuid}"
                )
            else:
                logger.warning(
                    f"Tool '{tool_name}' execution failed: {result.get('error', 'Unknown error')}"
                )

            return result

        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            logger.error(f"Tool execution error in agent {self.agent_uuid}: {e}")
            return {"success": False, "error": error_msg}

    def generate_response(
        self, prompt: str, use_tools: bool = True, **kwargs
    ) -> Dict[str, Any]:
        """
        Generate response using the agent's LLM engine with intelligent tool usage.

        Args:
            prompt (str): Input prompt.
            use_tools (bool): Whether to consider tools. Defaults to True.
            **kwargs: Additional parameters for LLM.

        Returns:
            Dict[str, Any]: Response with content, tool usage information, and cost data.

        Raises:
            Exception: An error occurred while generating response.
        """
        try:
            response_data = {
                "content": "",
                "tools_used": [],
                "tool_results": {},
                "cost_info": {},
                "model_name": self.llm_engine.model_name
                if self.llm_engine
                else "unknown",
            }

            if use_tools and self.tools:
                # Let LLM decide which tools to use
                tool_analysis = self._analyze_tool_needs(prompt)

                if tool_analysis.get("should_use_tools", False):
                    needed_tools = tool_analysis.get("recommended_tools", [])

                    logger.info(
                        f"Agent {self.agent_uuid} decided to use tools: {needed_tools}"
                    )

                    # Execute recommended tools
                    for tool_name in needed_tools:
                        if tool_name in self.tool_registry:
                            logger.info(
                                f"Agent {self.agent_uuid} executing tool: {tool_name}"
                            )
                            tool_params = self._extract_tool_parameters(
                                prompt, tool_name
                            )
                            tool_result = self.execute_tool(tool_name, tool_params)

                            if tool_result.get("success", False):
                                response_data["tools_used"].append(tool_name)
                                response_data["tool_results"][tool_name] = tool_result
                                logger.info(
                                    f"Agent {self.agent_uuid} successfully used tool: {tool_name}"
                                )
                            else:
                                logger.warning(
                                    f"Agent {self.agent_uuid} tool failed: {tool_name} - {tool_result.get('error', 'Unknown error')}"
                                )
                        else:
                            logger.warning(
                                f"Agent {self.agent_uuid} requested unknown tool: {tool_name}"
                            )

                    if response_data["tools_used"]:
                        logger.info(
                            f"Agent {self.agent_uuid} generating response with tool results from: {response_data['tools_used']}"
                        )
                        # Generate response with tool results
                        response_data["content"] = (
                            self._generate_response_with_tool_results(
                                prompt, response_data["tool_results"], **kwargs
                            )
                        )
                    else:
                        logger.info(
                            f"Agent {self.agent_uuid} no tools succeeded, generating normal response"
                        )
                        # Generate response without tools
                        response_data["content"] = self.llm_engine.generate_response(
                            prompt, **kwargs
                        )
                else:
                    logger.info(f"Agent {self.agent_uuid} decided not to use tools")
                    # Generate response without tools
                    response_data["content"] = self.llm_engine.generate_response(
                        prompt, **kwargs
                    )
            else:
                # Generate response without tools
                response_data["content"] = self.llm_engine.generate_response(
                    prompt, **kwargs
                )

            # Get cost information from LLM engine after response generation
            if hasattr(self.llm_engine, "get_cost_statistics"):
                cost_stats = self.llm_engine.get_cost_statistics()
                # Get the latest request cost information
                response_data["cost_info"] = {
                    "input_tokens": cost_stats.get("last_request_input_tokens", 0),
                    "output_tokens": cost_stats.get("last_request_output_tokens", 0),
                    "input_cost": cost_stats.get("last_request_input_cost", 0.0),
                    "output_cost": cost_stats.get("last_request_output_cost", 0.0),
                    "total_cost": cost_stats.get("last_request_total_cost", 0.0),
                }

            return response_data

        except Exception as e:
            logger.error(f"Response generation error in agent {self.agent_uuid}: {e}")
            return {
                "content": f"I apologize, but I encountered an error while processing your request: {str(e)}",
                "tools_used": [],
                "tool_results": {},
                "cost_info": {},
                "model_name": self.llm_engine.model_name
                if self.llm_engine
                else "unknown",
            }

    def _analyze_tool_needs(self, prompt: str) -> Dict[str, Any]:
        """
        Use LLM-based reasoning to determine if tools are needed and which ones.

        Args:
            prompt (str): User prompt to analyze.

        Returns:
            Dict[str, Any]: Analysis result with tool recommendations.
        """
        if not self.tools:
            return {"should_use_tools": False, "recommended_tools": []}

        try:
            # Create tool descriptions for the LLM
            tool_descriptions = []
            for tool in self.tools:
                tool_descriptions.append(f"- {tool.name}: {tool.description}")

            tools_text = "\n".join(tool_descriptions)

            # Create analysis prompt for the LLM
            analysis_prompt = f"""Analyze the following user request and determine which tools (if any) would be helpful to answer it.

User request: "{prompt}"

Available tools:
{tools_text}

Please analyze the user's request and respond with a JSON object containing:
- "should_use_tools": boolean (true if any tools would be helpful)
- "recommended_tools": list of tool names that would be useful
- "reasoning": brief explanation of your analysis

Consider:
1. Does the request require real-time information? (web_search)
2. Does it involve mathematical calculations? (calculator) 
3. Does it ask about weather conditions? (weather_check)
4. Could the request be answered with general knowledge alone?

Respond only with valid JSON, no additional text."""

            logger.info(
                f"Sending tool analysis prompt to LLM for request: {prompt[:50]}..."
            )

            # Get LLM analysis with shorter parameters to reduce cost
            llm_response = self.llm_engine.generate_response(
                analysis_prompt,
                max_tokens=200,  # Keep response short
                temperature=0.1,  # Low temperature for more consistent analysis
            )

            logger.info(f"LLM tool analysis response: {llm_response}")

            # Parse the LLM response
            import json
            import re

            # Try to extract JSON from the response
            json_match = re.search(r"\{.*\}", llm_response, re.DOTALL)
            if json_match:
                try:
                    analysis_result = json.loads(json_match.group())

                    # Validate the response structure
                    if all(
                        key in analysis_result
                        for key in [
                            "should_use_tools",
                            "recommended_tools",
                            "reasoning",
                        ]
                    ):
                        # Filter recommended tools to only include available ones
                        available_tool_names = [tool.name for tool in self.tools]
                        filtered_tools = [
                            tool
                            for tool in analysis_result["recommended_tools"]
                            if tool in available_tool_names
                        ]

                        result = {
                            "should_use_tools": analysis_result["should_use_tools"]
                            and len(filtered_tools) > 0,
                            "recommended_tools": filtered_tools,
                            "reasoning": analysis_result["reasoning"],
                        }

                        logger.info(f"LLM-based tool analysis result: {result}")
                        return result
                    else:
                        logger.warning(
                            "LLM response missing required keys, falling back to keyword analysis"
                        )

                except json.JSONDecodeError as e:
                    logger.warning(
                        f"Failed to parse LLM JSON response: {e}, falling back to keyword analysis"
                    )
            else:
                logger.warning(
                    "No JSON found in LLM response, falling back to keyword analysis"
                )

        except Exception as e:
            logger.error(
                f"Error in LLM-based tool analysis: {e}, falling back to keyword analysis"
            )

        # Fallback to keyword-based analysis if LLM analysis fails
        logger.info("Using fallback keyword-based tool analysis")
        return self._fallback_keyword_analysis(prompt)

    def _fallback_keyword_analysis(self, prompt: str) -> Dict[str, Any]:
        """
        Fallback keyword-based analysis when LLM analysis fails.

        Args:
            prompt (str): User prompt to analyze.

        Returns:
            Dict[str, Any]: Analysis result with tool recommendations.
        """
        recommended_tools = []
        prompt_lower = prompt.lower()

        # Simple keyword-based tool recommendation
        for tool in self.tools:
            if tool.name == "web_search":
                search_keywords = [
                    "search",
                    "find",
                    "lookup",
                    "latest",
                    "current",
                    "recent",
                    "information about",
                    "what is",
                    "tell me about",
                    "查找",
                    "搜尋",
                    "最新",
                    "資訊",
                    "什麼是",
                ]
                if any(keyword in prompt_lower for keyword in search_keywords):
                    recommended_tools.append(tool.name)

            elif tool.name == "calculator":
                calc_keywords = [
                    "calculate",
                    "compute",
                    "math",
                    "計算",
                    "數學",
                    "plus",
                    "minus",
                    "times",
                    "divided",
                    "+",
                    "-",
                    "*",
                    "/",
                    "=",
                    "×",
                    "÷",
                    "加",
                    "減",
                    "乘",
                    "除",
                ]
                import re

                has_numbers = re.search(r"\d+", prompt)
                has_calc_keywords = any(
                    keyword in prompt_lower for keyword in calc_keywords
                )

                if has_calc_keywords or (
                    has_numbers
                    and any(op in prompt for op in ["+", "-", "*", "/", "×", "÷"])
                ):
                    recommended_tools.append(tool.name)

            elif tool.name == "weather_check":
                weather_keywords = [
                    "weather",
                    "temperature",
                    "temp",
                    "forecast",
                    "climate",
                    "rain",
                    "sunny",
                    "cloudy",
                    "天氣",
                    "氣溫",
                    "預報",
                    "下雨",
                    "晴天",
                    "陰天",
                    "degrees",
                    "celsius",
                    "fahrenheit",
                    "hot",
                    "cold",
                    "warm",
                    "cool",
                    "humidity",
                    "wind",
                ]
                if any(keyword in prompt_lower for keyword in weather_keywords):
                    recommended_tools.append(tool.name)

        should_use = len(recommended_tools) > 0

        result = {
            "should_use_tools": should_use,
            "recommended_tools": recommended_tools,
            "reasoning": f"Keyword-based fallback analysis found {len(recommended_tools)} relevant tools",
        }

        logger.info(f"Fallback keyword analysis result: {result}")
        return result

    def _extract_tool_parameters(self, prompt: str, tool_name: str) -> Dict[str, Any]:
        """
        Extract parameters for a specific tool from the prompt with improved logic.

        Args:
            prompt (str): User prompt.
            tool_name (str): Name of the tool.

        Returns:
            Dict[str, Any]: Extracted parameters.
        """
        logger.info(
            f"Extracting parameters for tool '{tool_name}' from prompt: {prompt[:100]}..."
        )

        if tool_name == "web_search":
            # For web search, use the entire prompt as query but clean it up
            query = prompt.strip()
            # Remove common question words to make better search query
            query_words = query.split()
            filtered_words = [
                word
                for word in query_words
                if word.lower() not in ["what", "is", "the", "tell", "me", "about"]
            ]
            if filtered_words:
                query = " ".join(filtered_words)

            params = {"query": query, "max_results": 5}
            logger.info(f"Web search parameters: {params}")
            return params

        elif tool_name == "calculator":
            # Extract mathematical expressions with better patterns
            import re

            # Look for explicit math expressions
            math_patterns = [
                r"(\d+(?:\.\d+)?\s*[+\-*/×÷]\s*\d+(?:\.\d+)?(?:\s*[+\-*/×÷]\s*\d+(?:\.\d+)?)*)",
                r"(\d+\s*\+\s*\d+)",
                r"(\d+\s*\-\s*\d+)",
                r"(\d+\s*\*\s*\d+)",
                r"(\d+\s*/\s*\d+)",
                r"(\d+\s*×\s*\d+)",
                r"(\d+\s*÷\s*\d+)",
            ]

            expression = None
            for pattern in math_patterns:
                match = re.search(pattern, prompt)
                if match:
                    expression = match.group(1).strip()
                    break

            # If no explicit math found, look for numbers and assume it's a calculation
            if not expression:
                numbers = re.findall(r"\d+(?:\.\d+)?", prompt)
                if len(numbers) >= 2:
                    expression = " + ".join(numbers)  # Default to addition
                elif len(numbers) == 1:
                    expression = numbers[0]
                else:
                    expression = prompt  # Fallback to entire prompt

            params = {"expression": expression}
            logger.info(f"Calculator parameters: {params}")
            return params

        elif tool_name == "weather_check":
            # Extract location with better patterns
            import re

            # Multiple patterns to find location - ordered from most specific to most general
            location_patterns = [
                r"(?:weather|temperature|temp|forecast).*?(?:in|at|for)\s+([A-Za-z\s,]+?)(?:\s|$|[.?!])",
                r"(?:in|at|for)\s+([A-Za-z\s,]+?)(?:\s|$|[.?!])",
                r"([A-Za-z\s,]+?)(?:\s+weather|\s+temperature|\s+temp|\s+forecast)",
                r"^([A-Za-z\s,]+?)(?:\s+temp|temperature)(?:\s|$|[.?!])",  # For "tokyo temp"
                r"(\w+(?:\s+\w+)*)\s*[?]?$",  # Last resort - end of sentence
            ]

            location = "current location"  # Default

            for pattern in location_patterns:
                match = re.search(pattern, prompt, re.IGNORECASE)
                if match:
                    potential_location = match.group(1).strip().rstrip(".,?!")
                    # Filter out common non-location words
                    if potential_location.lower() not in [
                        "the",
                        "weather",
                        "temperature",
                        "temp",
                        "forecast",
                        "what",
                        "is",
                        "check",
                        "get",
                    ]:
                        location = potential_location
                        logger.info(
                            f"Found location '{location}' using pattern: {pattern}"
                        )
                        break

            params = {"location": location}
            logger.info(f"Weather check parameters: {params}")
            return params

        else:
            logger.warning(f"Unknown tool name: {tool_name}")
            return {}

    def _generate_response_with_tool_results(
        self, original_prompt: str, tool_results: Dict[str, Any], **kwargs
    ) -> str:
        """
        Generate response incorporating tool results.

        Args:
            original_prompt (str): Original user prompt.
            tool_results (Dict[str, Any]): Results from executed tools.
            **kwargs: Additional LLM parameters.

        Returns:
            str: Generated response with tool results integrated.
        """
        if not tool_results:
            return self.llm_engine.generate_response(original_prompt, **kwargs)

        # Format tool results for inclusion in prompt
        tool_context = []
        for tool_name, result in tool_results.items():
            if result.get("success", False):
                tool_context.append(f"\n{tool_name.upper()} RESULTS:")
                if tool_name == "web_search":
                    results = result.get("results", [])
                    for i, res in enumerate(results[:3], 1):
                        title = res.get("title", "No title")
                        snippet = res.get("snippet", "No description")
                        tool_context.append(f"{i}. {title}: {snippet}")
                elif tool_name == "calculator":
                    calc_result = result.get("result", "No result")
                    tool_context.append(f"Calculation result: {calc_result}")
                elif tool_name == "weather_check":
                    weather_info = result.get("weather", "No weather data")
                    tool_context.append(f"Weather information: {weather_info}")

        enhanced_prompt = f"""User request: {original_prompt}

Additional information from tools:
{chr(10).join(tool_context)}

Please provide a comprehensive response to the user's question, incorporating the relevant information from the tools above. Make sure your response is natural and well-integrated."""

        return self.llm_engine.generate_response(enhanced_prompt, **kwargs)

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
            "tool_count": len(self.tools),
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
            tool_descriptions = (
                "\n\nYou have access to the following tools:\n" + "\n".join(tool_list)
            )

        return f"""You are a {self.agent_type} agent.
Description: {self.description}

Your role is to help users with tasks related to your specialization.
Provide helpful, accurate, and detailed responses.{tool_descriptions}

Always be professional, friendly, and educational in your responses."""
