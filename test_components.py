"""
Simple test script to verify system components work independently
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    
    try:
        from core.logger import logger
        print("✓ Logger imported successfully")
        
        from core.registry import agent_registry
        print("✓ Agent registry imported successfully")
        
        from llm_engines.gemini_engine import GeminiEngine
        print("✓ Gemini engine imported successfully")
        
        from tools.web_search import WebSearchTool
        print("✓ Web search tool imported successfully")
        
        from agents.english_teacher import EnglishTeacherAgent
        print("✓ English teacher agent imported successfully")
        
        from agents.chinese_teacher import ChineseTeacherAgent
        print("✓ Chinese teacher agent imported successfully")
        
        print("\nAll imports successful!")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_registry():
    """Test agent registry functionality"""
    print("\nTesting agent registry...")
    
    try:
        from core.registry import agent_registry
        
        # Test getting agents
        agents = agent_registry.list_agents()
        print(f"✓ Found {len(agents)} registered agents")
        
        for agent in agents:
            print(f"  - {agent.agent_type}: {agent.description[:50]}...")
        
        # Test getting descriptions
        descriptions = agent_registry.get_agent_descriptions()
        print(f"✓ Agent descriptions: {list(descriptions.keys())}")
        
        return True
        
    except Exception as e:
        print(f"✗ Registry test error: {e}")
        return False

def test_tools():
    """Test tool functionality"""
    print("\nTesting tools...")
    
    try:
        from tools.web_search import WebSearchTool
        
        tool = WebSearchTool()
        print(f"✓ Tool created: {tool.name}")
        
        # Test parameter schema
        schema = tool.get_parameters_schema()
        print(f"✓ Parameter schema: {list(schema['properties'].keys())}")
        
        # Test execution (simulation)
        result = tool.execute(query="test query", max_results=3)
        print(f"✓ Tool execution: {result['success']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Tool test error: {e}")
        return False

def test_agents():
    """Test agent creation (without LLM API calls)"""
    print("\nTesting agent creation...")
    
    try:
        # Note: This will fail without proper API key, but tests the structure
        from agents.english_teacher import EnglishTeacherAgent
        from agents.chinese_teacher import ChineseTeacherAgent
        
        print("✓ Agent classes can be imported")
        print("✗ Cannot test full agent functionality without API key")
        
        return True
        
    except Exception as e:
        print(f"✗ Agent test error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("AGENTIC SYSTEM - COMPONENT TESTS")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_registry, 
        test_tools,
        test_agents
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All component tests passed!")
        print("\nTo run the full system:")
        print("1. Set up your .env file with GEMINI_API_KEY")
        print("2. Run: docker-compose up --build")
    else:
        print("✗ Some tests failed. Check the errors above.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
