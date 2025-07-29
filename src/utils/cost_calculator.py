"""
Cost calculation utilities and helpers
"""

from typing import Any, Dict

import src.config.settings as settings
from src.utils.logger import logger


class CostCalculator:
    """
    Cost calculator for different LLM providers
    """

    @staticmethod
    def get_provider_costs(provider: str) -> Dict[str, float]:
        """
        Get cost configuration for a specific provider

        Args:
            provider: Provider name (gemini, ollama, openai, claude)

        Returns:
            Dictionary with input_cost_per_1k and output_cost_per_1k
        """
        provider = provider.lower()

        if provider == "gemini":
            return {
                "input_cost_per_1k": settings.GEMINI_INPUT_COST_PER_1K,
                "output_cost_per_1k": settings.GEMINI_OUTPUT_COST_PER_1K,
            }
        elif provider == "ollama":
            return {
                "input_cost_per_1k": settings.OLLAMA_COMPUTE_COST_PER_1K,
                "output_cost_per_1k": settings.OLLAMA_COMPUTE_COST_PER_1K,
            }
        elif provider == "openai":
            return {
                "input_cost_per_1k": settings.OPENAI_INPUT_COST_PER_1K,
                "output_cost_per_1k": settings.OPENAI_OUTPUT_COST_PER_1K,
            }
        elif provider == "claude":
            return {
                "input_cost_per_1k": settings.CLAUDE_INPUT_COST_PER_1K,
                "output_cost_per_1k": settings.CLAUDE_OUTPUT_COST_PER_1K,
            }
        else:
            logger.warning(f"Unknown provider: {provider}, using default costs")
            return {"input_cost_per_1k": 0.001, "output_cost_per_1k": 0.002}

    @staticmethod
    def calculate_request_cost(
        provider: str, input_tokens: int, output_tokens: int
    ) -> Dict[str, float]:
        """
        Calculate cost for a specific request

        Args:
            provider: Provider name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Dictionary with input_cost, output_cost, and total_cost
        """
        costs = CostCalculator.get_provider_costs(provider)

        input_cost = (input_tokens / 1000) * costs["input_cost_per_1k"]
        output_cost = (output_tokens / 1000) * costs["output_cost_per_1k"]
        total_cost = input_cost + output_cost

        return {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
        }

    @staticmethod
    def get_cost_summary() -> Dict[str, Any]:
        """
        Get a summary of all cost configurations

        Returns:
            Dictionary with cost settings for all providers
        """
        return {
            "providers": {
                "gemini": CostCalculator.get_provider_costs("gemini"),
                "ollama": CostCalculator.get_provider_costs("ollama"),
                "openai": CostCalculator.get_provider_costs("openai"),
                "claude": CostCalculator.get_provider_costs("claude"),
            },
            "settings": {
                "cost_alert_threshold": settings.COST_ALERT_THRESHOLD,
                "cost_tracking_enabled": settings.COST_TRACKING_ENABLED,
            },
        }

    @staticmethod
    def validate_configuration() -> bool:
        """
        Validate that cost configuration is properly set

        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Check if all cost parameters are numbers and non-negative
            cost_params = [
                settings.GEMINI_INPUT_COST_PER_1K,
                settings.GEMINI_OUTPUT_COST_PER_1K,
                settings.OLLAMA_COMPUTE_COST_PER_1K,
                settings.OPENAI_INPUT_COST_PER_1K,
                settings.OPENAI_OUTPUT_COST_PER_1K,
                settings.CLAUDE_INPUT_COST_PER_1K,
                settings.CLAUDE_OUTPUT_COST_PER_1K,
                settings.COST_ALERT_THRESHOLD,
            ]

            for param in cost_params:
                if not isinstance(param, (int, float)) or param < 0:
                    logger.error(f"Invalid cost parameter: {param}")
                    return False

            logger.info("Cost configuration validation passed")
            return True

        except Exception as e:
            logger.error(f"Cost configuration validation failed: {e}")
            return False


# Global cost calculator instance
cost_calculator = CostCalculator()
