#!/usr/bin/env python3
"""
Simple test to verify Ollama integration works
"""
from llm_engines.factory import LLMEngineFactory

def quick_test():
    print("=== Ollama Integration Test ===")
    
    # Test 1: Engine creation
    print("1. Testing engine creation...")
    try:
        engine = LLMEngineFactory.create_for_agent(agent_type='english_teacher')
        print(f"   ✅ Engine created: {type(engine).__name__}")
        print(f"   ✅ Model: {engine.model_name}")
        print(f"   ✅ Base URL: {engine.base_url}")
    except Exception as e:
        print(f"   ❌ Engine creation failed: {e}")
        return False
    
    # Test 2: Simple response
    print("2. Testing simple response...")
    try:
        messages = [{'role': 'user', 'content': 'Hello'}]
        response = engine.generate_response(messages)
        print(f"   ✅ Response: {response[:100]}...")
    except Exception as e:
        print(f"   ❌ Response test failed: {e}")
        return False
    
    print("🎉 All tests passed!")
    return True

if __name__ == "__main__":
    quick_test()
