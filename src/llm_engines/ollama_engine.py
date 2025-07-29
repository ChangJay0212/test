"""
Ollama LLM Engine implementation with cost monitoring
"""

import time
from typing import Any, Dict, List

import requests

import src.config.settings as settings
from src.llm_engines.base_engine import BaseLLMEngine
from src.utils.cost_calculator import cost_calculator
from src.utils.logger import logger


class OllamaEngine(BaseLLMEngine):
    """
    OllamaEngine class for Ollama LLM engine implementation for local models.
    """

    def __init__(
        self, model_name: str = None, api_key: str = None, base_url: str = None
    ):
        if model_name is None:
            model_name = getattr(settings, "OLLAMA_MODEL", "llama2")
        if base_url is None:
            base_url = getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434")

        # Set base_url before calling super().__init__
        self.base_url = base_url.rstrip("/")
        self.timeout = getattr(settings, "OLLAMA_TIMEOUT", 60)

        # Cost tracking attributes (Ollama is free but we track usage)
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_requests = 0
        self.total_cost = 0.0  # Always 0 for local models

        # Last request tracking
        self.last_request_input_tokens = 0
        self.last_request_output_tokens = 0
        self.last_request_input_cost = 0.0
        self.last_request_output_cost = 0.0
        self.last_request_total_cost = 0.0

        # No actual cost for local models, but we can estimate computational cost from settings
        self.compute_cost_per_1k = settings.OLLAMA_COMPUTE_COST_PER_1K

        # Ollama doesn't require API key but we keep it for interface consistency
        super().__init__(model_name, api_key)

    def _initialize_client(self):
        """
        Initialize Ollama client by checking server availability with retry logic.

        Raises:
            ConnectionError:
                If unable to connect to Ollama server after retries.
            Exception:
                An error occurred while initializing the client.
        """
        max_retries = 5
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Attempting to connect to Ollama server at {self.base_url} (attempt {attempt + 1}/{max_retries})"
                )

                # Check if Ollama server is running
                response = requests.get(f"{self.base_url}/api/tags", timeout=10)
                if response.status_code == 200:
                    available_models = response.json().get("models", [])
                    model_names = [model["name"] for model in available_models]

                    if self.model_name not in model_names:
                        logger.warning(
                            f"Model '{self.model_name}' not found in Ollama. Available models: {model_names}"
                        )
                        logger.info(f"Attempting to pull model '{self.model_name}'...")
                        self._pull_model()

                    logger.info(
                        f"Ollama engine initialized with model: {self.model_name}"
                    )
                    return  # Success!
                else:
                    raise ConnectionError(
                        f"Ollama server not responding: {response.status_code}"
                    )

            except requests.RequestException as e:
                logger.warning(
                    f"Attempt {attempt + 1} failed to connect to Ollama server at {self.base_url}: {e}"
                )

                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 1.5  # Exponential backoff
                else:
                    logger.error(
                        f"Failed to connect to Ollama server after {max_retries} attempts"
                    )
                    raise ConnectionError(
                        f"Ollama server unavailable after {max_retries} attempts: {e}"
                    )

    def _pull_model(self):
        """
        Pull model if not available locally.

        Raises:
            Exception:
                An error occurred while pulling the model.
        """
        try:
            logger.info(f"Pulling model '{self.model_name}' from Ollama...")
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": self.model_name},
                timeout=300,  # 5 minutes timeout for model download
            )

            if response.status_code == 200:
                logger.info(f"Model '{self.model_name}' pulled successfully")
            else:
                logger.error(
                    f"Failed to pull model '{self.model_name}': {response.text}"
                )

        except Exception as e:
            logger.error(f"Error pulling model: {e}")

    def generate_response(self, prompt: str, user_id: str = "anonymous", **kwargs) -> str:
        """
        Generate response using Ollama.

        Args:
            prompt (str): Input prompt.
            user_id (str): User identifier for cost tracking.
            **kwargs: Additional generation parameters.

        Returns:
            str: Generated text response.

        Raises:
            Exception:
                An error occurred while generating response.
        """
        start_time = time.time()
        request_id = kwargs.get("request_id", f"ollama_{int(start_time)}")
        agent_uuid = kwargs.get("agent_uuid", "")
        agent_type = kwargs.get("agent_type", "")

        try:
            # Extract parameters
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 1024)
            stream = kwargs.get("stream", False)

            # Prepare request payload
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": stream,
                "options": {"temperature": temperature, "num_predict": max_tokens},
            }

            # Make request to Ollama
            response = requests.post(
                f"{self.base_url}/api/generate", json=payload, timeout=self.timeout
            )

            if response.status_code != 200:
                raise Exception(
                    f"Ollama API error: {response.status_code} - {response.text}"
                )

            # Parse response
            response_data = response.json()
            generated_text = response_data.get("response", "")

            # Calculate token usage (estimation based on character count)
            input_tokens, output_tokens = self._estimate_token_usage(prompt, generated_text)

            # Update tracking
            self.total_requests += 1

            end_time = time.time()
            response_time = end_time - start_time

            # Send token usage to cost monitor
            self._send_token_usage_to_cost_monitor(
                request_id=request_id,
                user_id=user_id,
                agent_uuid=agent_uuid,
                agent_type=agent_type,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                response_time=response_time,
                success=True
            )

            # Log usage information
            logger.info(
                f"Ollama request completed: "
                f"Input tokens: {input_tokens}, "
                f"Output tokens: {output_tokens}, "
                f"Response time: {response_time:.2f}s"
            )

            if generated_text:
                logger.debug(f"Generated response: {generated_text[:100]}...")
                return generated_text
            else:
                raise Exception("Empty response from Ollama")

        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            # Send failed request info to cost monitor
            self._send_token_usage_to_cost_monitor(
                request_id=request_id,
                user_id=user_id,
                agent_uuid=agent_uuid,
                agent_type=agent_type,
                input_tokens=0,
                output_tokens=0,
                response_time=response_time,
                success=False,
                error_message=str(e)
            )
            
            logger.error(f"Ollama generation failed: {e}")
            raise

    def generate_with_tools(
        self, prompt: str, tools: List[Dict[str, Any]], user_id: str = "anonymous", **kwargs
    ) -> str:
        """
        Generate response with tool calling capability
        Note: Basic implementation for tool integration

        Args:
            prompt: Input prompt
            tools: List of available tools
            user_id: User identifier for cost tracking
            **kwargs: Additional parameters

        Returns:
            Generated response
        """
        try:
            # Format tools for prompt inclusion
            tool_descriptions = self._format_tools_for_prompt(tools)

            enhanced_prompt = f"""You are an AI assistant with access to the following tools:

{tool_descriptions}

User request: {prompt}

Please provide a helpful response. If you need to use any tools, mention which tool you would use and why, but focus on providing a direct answer to the user's question."""

            return self.generate_response(enhanced_prompt, user_id=user_id, **kwargs)

        except Exception as e:
            logger.error(f"Error generating response with tools: {e}")
            raise

    def _format_tools_for_prompt(self, tools: List[Dict[str, Any]]) -> str:
        """
        Format tool descriptions for inclusion in prompt

        Args:
            tools: List of tool definitions

        Returns:
            Formatted tool descriptions
        """
        if not tools:
            return "No additional tools available."

        tool_list = []
        for tool in tools:
            name = tool.get("name", "Unknown")
            description = tool.get("description", "No description available")
            tool_list.append(f"- {name}: {description}")

        return "\n".join(tool_list)

    def _calculate_request_cost(self, prompt: str, response: str) -> Dict[str, Any]:
        """
        Calculate usage statistics for a single request using cost_calculator
        Note: Ollama is free but we can track computational cost if configured

        Args:
            prompt: Input prompt
            response: Generated response

        Returns:
            Dictionary with usage breakdown
        """
        try:
            # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
            input_tokens = len(prompt) // 4
            output_tokens = len(response) // 4

            # Calculate costs using cost_calculator (usually 0 for Ollama)
            cost_breakdown = cost_calculator.calculate_request_cost(
                "ollama", input_tokens, output_tokens
            )

            # Store last request data
            self.last_request_input_tokens = input_tokens
            self.last_request_output_tokens = output_tokens
            self.last_request_input_cost = cost_breakdown["input_cost"]
            self.last_request_output_cost = cost_breakdown["output_cost"]
            self.last_request_total_cost = cost_breakdown["total_cost"]

            # Update totals
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens
            self.total_cost += cost_breakdown["total_cost"]

            return {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "input_cost": cost_breakdown["input_cost"],
                "output_cost": cost_breakdown["output_cost"],
                "total_cost": cost_breakdown["total_cost"],
            }

        except Exception as e:
            logger.error(f"Error calculating request usage: {e}")
            # Reset last request data on error
            self.last_request_input_tokens = 0
            self.last_request_output_tokens = 0
            self.last_request_input_cost = 0.0
            self.last_request_output_cost = 0.0
            self.last_request_total_cost = 0.0

            return {
                "input_tokens": 0,
                "output_tokens": 0,
                "input_cost": 0.0,
                "output_cost": 0.0,
                "total_cost": 0.0,
            }

    def get_cost_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive usage statistics

        Returns:
            Dictionary with usage statistics
        """
        return {
            "total_requests": self.total_requests,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost": self.total_cost,  # Always 0 for local models
            "average_cost_per_request": 0.0,  # Always 0
            "average_tokens_per_request": (
                self.total_input_tokens + self.total_output_tokens
            )
            / max(self.total_requests, 1),
            "compute_cost_per_1k": self.compute_cost_per_1k,
            "model_name": self.model_name,
            "engine_type": "ollama",
            "deployment_type": "local",
            # Last request data
            "last_request_input_tokens": self.last_request_input_tokens,
            "last_request_output_tokens": self.last_request_output_tokens,
            "last_request_input_cost": self.last_request_input_cost,
            "last_request_output_cost": self.last_request_output_cost,
            "last_request_total_cost": self.last_request_total_cost,
        }

    def reset_cost_tracking(self):
        """Reset all usage tracking counters"""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_requests = 0
        self.total_cost = 0.0

        # Reset last request data
        self.last_request_input_tokens = 0
        self.last_request_output_tokens = 0
        self.last_request_input_cost = 0.0
        self.last_request_output_cost = 0.0
        self.last_request_total_cost = 0.0

        logger.info("Ollama usage tracking counters reset")

    def validate_api_key(self) -> bool:
        """
        Validate connection to Ollama server with retry logic

        Returns:
            True if server is accessible, False otherwise
        """
        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Validating Ollama server connection (attempt {attempt + 1}/{max_retries})"
                )
                response = requests.get(f"{self.base_url}/api/tags", timeout=10)
                if response.status_code == 200:
                    logger.info("Ollama server validation successful")
                    return True
                else:
                    logger.warning(
                        f"Ollama server returned status {response.status_code}"
                    )
            except Exception as e:
                logger.warning(
                    f"Ollama server validation attempt {attempt + 1} failed: {e}"
                )
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff

        logger.error("Ollama server validation failed after all attempts")
        return False

    def requires_api_key(self) -> bool:
        """
        Check if this engine requires an API key

        Returns:
            False since Ollama doesn't require API keys
        """
        return False

    def get_available_models(self) -> List[str]:
        """
        Get list of available models in Ollama

        Returns:
            List of model names
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
            else:
                logger.error(f"Failed to get models: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return []

    def _estimate_token_usage(self, prompt: str, response: str) -> tuple:
        """
        Estimate token usage for prompt and response.
        
        Args:
            prompt: Input prompt
            response: Generated response
            
        Returns:
            Tuple of (input_tokens, output_tokens)
        """
        # Rough approximation: 1 token ≈ 4 characters for English text
        input_tokens = max(len(prompt) // 4, 1)
        output_tokens = max(len(response) // 4, 1)
        return input_tokens, output_tokens

    def _get_provider_name(self) -> str:
        """Get the provider name for this engine."""
        return "ollama"

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get detailed model information

        Returns:
            Dictionary containing model metadata
        """
        base_info = super().get_model_info()
        base_info.update(
            {
                "base_url": self.base_url,
                "deployment_type": "local",
                "cost_model": "free",
                "timeout": self.timeout,
            }
        )
        return base_info
