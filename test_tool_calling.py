#!/usr/bin/env python3
"""
Test tool calling functionality
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_tool_analysis():
    """Test tool analysis logic"""
    print("🔍 Testing Tool Analysis Logic")
    print("=" * 50)
    
    try:
        from agents.english_teacher import EnglishTeacherAgent
        from llm_engines.factory import LLMEngineFactory
        
        # Create a simple mock engine for testing
        class MockEngine:
            def __init__(self):
                self.model_name = "test-model"
            
            def generate_response(self, prompt):
                return "Mock response for testing"
            
            def get_cost_statistics(self):
                return {
                    "last_request_input_tokens": 10,
                    "last_request_output_tokens": 5,
                    "last_request_total_cost": 0.001
                }
        
        # Create agent with mock engine
        mock_engine = MockEngine()
        agent = EnglishTeacherAgent(mock_engine)
        
        print(f"Agent created with {len(agent.tools)} tools:")
        for tool in agent.tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # Test different types of prompts
        test_prompts = [
            "What's 15 * 24?",  # Should trigger calculator
            "Search for information about machine learning",  # Should trigger web_search
            "What's the weather in Tokyo?",  # Should trigger weather_check
            "Calculate 2 + 2 * 3",  # Should trigger calculator
            "Find latest news about AI",  # Should trigger web_search
            "Tell me about metaphors in literature",  # Might not trigger tools
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n--- Test {i}: {prompt} ---")
            
            # Test tool analysis
            analysis = agent._analyze_tool_needs(prompt)
            print(f"Analysis result: {analysis}")
            
            # Test parameter extraction for recommended tools
            for tool_name in analysis.get("recommended_tools", []):
                params = agent._extract_tool_parameters(prompt, tool_name)
                print(f"Parameters for {tool_name}: {params}")
        
        print("\n✅ Tool analysis testing completed!")
        
    except Exception as e:
        print(f"❌ Error during tool analysis testing: {e}")
        import traceback
        traceback.print_exc()

def test_direct_tool_execution():
    """Test direct tool execution"""
    print("\n🔧 Testing Direct Tool Execution")
    print("=" * 50)
    
    try:
        from tools.calculator import Calculator
        from tools.web_search import WebSearchTool
        from tools.weather_check import WeatherCheck
        
        # Test Calculator
        print("\n1. Testing Calculator:")
        calc = Calculator()
        result = calc.execute(expression="2 + 2 * 3")
        print(f"Result: {result}")
        
        # Test Web Search
        print("\n2. Testing Web Search:")
        search = WebSearchTool()
        result = search.execute(query="artificial intelligence", max_results=3)
        print(f"Result: {result}")
        
        # Test Weather Check
        print("\n3. Testing Weather Check:")
        weather = WeatherCheck()
        result = weather.execute(location="Tokyo")
        print(f"Result: {result}")
        
        print("\n✅ Direct tool execution testing completed!")
        
    except Exception as e:
        print(f"❌ Error during direct tool testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tool_analysis()
    test_direct_tool_execution()
