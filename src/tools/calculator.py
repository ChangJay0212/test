"""
Calculator tool for mathematical computations
"""

import re
from typing import Any, Dict

from src.tools.base_tool import BaseTool
from src.utils.logger import logger


class Calculator(BaseTool):
    """
    Calculator class for performing mathematical operations.
    """

    def __init__(self):
        super().__init__(
            name="calculator",
            description="Perform mathematical calculations and evaluate mathematical expressions",
        )

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute mathematical calculation.

        Args:
            **kwargs: Keyword arguments containing:
                expression (str): Mathematical expression to evaluate.

        Returns:
            Dict[str, Any]: Dictionary with calculation result.

        Raises:
            Exception:
                An error occurred while executing the calculation.
        """
        try:
            expression = kwargs.get("expression", "")

            # Sanitize the expression
            expression = expression.strip()
            logger.info(f"Calculating: {expression}")

            # Replace common mathematical symbols
            expression = expression.replace("×", "*").replace("÷", "/")
            expression = expression.replace("x", "*").replace("X", "*")

            # Remove any non-mathematical characters (basic security)
            if not re.match(r"^[0-9+\-*/().\s%]+$", expression):
                return {
                    "success": False,
                    "error": "Invalid characters in mathematical expression",
                    "expression": expression,
                }

            # Evaluate the expression safely
            result = eval(expression)

            logger.info(f"Calculation result: {expression} = {result}")

            return {
                "success": True,
                "expression": expression,
                "result": result,
                "formatted_result": f"{expression} = {result}",
            }

        except ZeroDivisionError:
            error_msg = "Division by zero error"
            logger.error(f"Calculator error: {error_msg}")
            return {"success": False, "error": error_msg, "expression": expression}
        except SyntaxError as e:
            error_msg = f"Invalid mathematical expression: {str(e)}"
            logger.error(f"Calculator error: {error_msg}")
            return {"success": False, "error": error_msg, "expression": expression}
        except Exception as e:
            error_msg = f"Calculation error: {str(e)}"
            logger.error(f"Calculator error: {error_msg}")
            return {"success": False, "error": error_msg, "expression": expression}

    def get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get tool parameters schema for validation.

        Returns:
            Dict[str, Any]: JSON schema for tool parameters.
        """
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to calculate (e.g., '2+2', '15*23', '25% of 480')",
                }
            },
            "required": ["expression"],
        }

    def get_schema(self) -> Dict[str, Any]:
        """
        Get tool schema for function calling

        Returns:
            JSON schema for the tool
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to calculate (e.g., '2+2', '15*23', '25% of 480')",
                        }
                    },
                    "required": ["expression"],
                },
            },
        }

    def validate_input(self, **kwargs) -> bool:
        """
        Validate input parameters

        Returns:
            True if input is valid, False otherwise
        """
        expression = kwargs.get("expression")
        if not expression or not isinstance(expression, str):
            logger.error("Calculator requires a valid mathematical expression")
            return False
        return True
