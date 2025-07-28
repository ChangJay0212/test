#!/usr/bin/env python3
"""
Quick test for tokyo temp query
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.base_agent import BaseAgent
from tools.weather_check import WeatherCheck
from tools.calculator import Calculator
from llm_engines.ollama_engine import OllamaEngine
from core.logger import logger

class TestAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="test_agent",
            llm_engine=OllamaEngine(model_name="llama3.1:8b")
        )
        
        # Add tools
        self.add_tool(WeatherCheck())
        self.add_tool(Calculator())
    
    def process_message(self, message):
        return {"response": "Test response"}

def test_tokyo_temp():
    print("=== Testing 'tokyo temp?' query ===")
    
    agent = TestAgent()
    
    # Test tool analysis
    prompt = "tokyo temp?"
    print(f"\nTesting prompt: '{prompt}'")
    
    # Test tool analysis
    tool_analysis = agent._analyze_tool_needs(prompt)
    print(f"Tool analysis result: {tool_analysis}")
    
    # Test parameter extraction for weather_check
    if "weather_check" in tool_analysis.get("recommended_tools", []):
        params = agent._extract_tool_parameters(prompt, "weather_check")
        print(f"Weather check parameters: {params}")
        
        # Test weather check execution
        weather_tool = agent.tool_registry["weather_check"]
        result = weather_tool.execute(**params)
        print(f"Weather check result: {result}")
    else:
        print("❌ weather_check was not recommended!")
    
    # Test parameter extraction for calculator (should not be triggered)
    if "calculator" in tool_analysis.get("recommended_tools", []):
        params = agent._extract_tool_parameters(prompt, "calculator")
        print(f"Calculator parameters: {params}")
        print("❌ Calculator was incorrectly recommended for weather query!")
    else:
        print("✅ Calculator was correctly not recommended")

if __name__ == "__main__":
    test_tokyo_temp()
