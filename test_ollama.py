#!/usr/bin/env python3
"""
Test Ollama integration
"""
from llm_engines.factory import LLMEngineFactory
import time

def test_ollama():
    print("🚀 Testing Ollama AI Response...")
    
    try:
        # Create LLM engine
        engine = LLMEngineFactory.create_for_agent(agent_type='english_teacher')
        print(f"✅ Created {type(engine).__name__} with model: {engine.model_name}")
        
        # Test conversation
        messages = [
            {
                'role': 'user', 
                'content': 'What is the difference between "their", "there", and "they\'re"? Please give a short explanation.'
            }
        ]
        
        print("📤 Sending message to Ollama...")
        start_time = time.time()
        response = engine.generate_response(messages)
        end_time = time.time()
        
        print(f"✅ Response received in {end_time - start_time:.2f} seconds")
        print(f"📝 Response: {response}")
        print("🎉 Ollama AI test passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_ollama()
