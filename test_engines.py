#!/usr/bin/env python3
"""
Test script for different LLM engines
Demonstrates usage of Gemini and Ollama engines
"""

import sys
import time
from typing import Dict, Any

# Add project root to path
sys.path.append('.')

from llm_engines.factory import LLMEngineFactory
from agents.english_teacher import EnglishTeacherAgent
from agents.chinese_teacher import ChineseTeacherAgent
from core.logger import logger


def test_engine_availability():
    """Test which engines are available and working"""
    print("\n" + "="*60)
    print("🔍 TESTING ENGINE AVAILABILITY")
    print("="*60)
    
    factory = LLMEngineFactory()
    available_engines = factory.get_available_engines()
    
    for engine_type, info in available_engines.items():
        print(f"\n📋 {engine_type.upper()} Engine:")
        print(f"   Name: {info.get('name', 'Unknown')}")
        print(f"   Type: {info.get('type', 'Unknown')}")
        print(f"   Requires API Key: {info.get('requires_api_key', 'Unknown')}")
        print(f"   Default Model: {info.get('default_model', 'Unknown')}")
        print(f"   Cost Model: {info.get('cost_model', 'Unknown')}")
        
        # Validate configuration
        validation = factory.validate_engine_config(engine_type)
        if validation.get('valid', False):
            print(f"   ✅ Status: Available")
            print(f"   📝 Message: {validation.get('message', '')}")
        else:
            print(f"   ❌ Status: Unavailable")
            print(f"   🚨 Error: {validation.get('error', '')}")
            if 'suggestion' in validation:
                print(f"   💡 Suggestion: {validation['suggestion']}")


def test_engine_creation():
    """Test creating different engines"""
    print("\n" + "="*60)
    print("🏭 TESTING ENGINE CREATION")
    print("="*60)
    
    engines_to_test = ['gemini', 'ollama']
    
    for engine_type in engines_to_test:
        print(f"\n🔧 Testing {engine_type.upper()} engine creation...")
        try:
            engine = LLMEngineFactory.create_engine(engine_type)
            print(f"   ✅ Successfully created {engine_type} engine")
            print(f"   📋 Model: {engine.model_name}")
            print(f"   🏷️  Type: {type(engine).__name__}")
            
            # Test basic functionality
            if engine.validate_api_key():
                print(f"   🔑 Connection: Valid")
            else:
                print(f"   ❌ Connection: Failed")
                
        except Exception as e:
            print(f"   ❌ Failed to create {engine_type} engine: {e}")


def test_simple_generation():
    """Test simple text generation with different engines"""
    print("\n" + "="*60)
    print("✍️  TESTING SIMPLE TEXT GENERATION")
    print("="*60)
    
    test_prompt = "Hello! Please introduce yourself briefly."
    engines_to_test = ['gemini', 'ollama']
    
    for engine_type in engines_to_test:
        print(f"\n🤖 Testing {engine_type.upper()} generation...")
        try:
            engine = LLMEngineFactory.create_engine(engine_type)
            
            start_time = time.time()
            response = engine.generate_response(test_prompt, max_tokens=100)
            end_time = time.time()
            
            print(f"   ⏱️  Response time: {end_time - start_time:.2f} seconds")
            print(f"   📝 Response length: {len(response)} characters")
            print(f"   💬 Response preview: {response[:100]}...")
            
            # Get cost statistics
            stats = engine.get_cost_statistics()
            print(f"   📊 Total requests: {stats['total_requests']}")
            print(f"   🪙 Total cost: ${stats['total_cost']:.4f}")
            
        except Exception as e:
            print(f"   ❌ Failed to generate with {engine_type}: {e}")


def test_agent_integration():
    """Test agents with different engines"""
    print("\n" + "="*60)
    print("👨‍🏫 TESTING AGENT INTEGRATION")
    print("="*60)
    
    engines_to_test = ['gemini', 'ollama']
    test_message = {
        "message": "Can you help me understand the difference between 'affect' and 'effect'?",
        "user_id": "test_user",
        "timestamp": time.time()
    }
    
    for engine_type in engines_to_test:
        print(f"\n🎭 Testing English Teacher with {engine_type.upper()}...")
        try:
            teacher = EnglishTeacherAgent(
                agent_uuid=f"test_teacher_{engine_type}",
                engine_type=engine_type
            )
            
            start_time = time.time()
            response = teacher.process_message(test_message)
            end_time = time.time()
            
            print(f"   ✅ Agent created successfully")
            print(f"   ⏱️  Processing time: {end_time - start_time:.2f} seconds")
            print(f"   🎯 Agent type: {teacher.agent_type}")
            print(f"   🤖 Engine type: {type(teacher.llm_engine).__name__}")
            print(f"   📏 Response length: {len(response.get('response', ''))} characters")
            
            if response.get('success'):
                print(f"   ✅ Processing: Successful")
                print(f"   💬 Response preview: {response.get('response', '')[:100]}...")
            else:
                print(f"   ❌ Processing: Failed - {response.get('error', '')}")
                
        except Exception as e:
            print(f"   ❌ Failed to test agent with {engine_type}: {e}")


def test_cost_monitoring():
    """Test cost monitoring across different engines"""
    print("\n" + "="*60)
    print("💰 TESTING COST MONITORING")
    print("="*60)
    
    engines_to_test = ['gemini', 'ollama']
    
    for engine_type in engines_to_test:
        print(f"\n📊 Cost monitoring for {engine_type.upper()}...")
        try:
            engine = LLMEngineFactory.create_engine(engine_type)
            
            # Generate a few responses
            for i in range(3):
                response = engine.generate_response(f"Test message {i+1}", max_tokens=50)
            
            # Get comprehensive statistics
            stats = engine.get_cost_statistics()
            
            print(f"   📈 Total requests: {stats['total_requests']}")
            print(f"   🔢 Total input tokens: {stats['total_input_tokens']}")
            print(f"   🔢 Total output tokens: {stats['total_output_tokens']}")
            print(f"   🪙 Total cost: ${stats['total_cost']:.6f}")
            print(f"   📊 Avg tokens/request: {stats['average_tokens_per_request']:.1f}")
            print(f"   💡 Engine type: {stats['engine_type']}")
            
            if engine_type == 'ollama':
                print(f"   🏠 Deployment: {stats['deployment_type']}")
            
        except Exception as e:
            print(f"   ❌ Failed to test cost monitoring for {engine_type}: {e}")


def test_factory_preferences():
    """Test factory engine preferences for different agent types"""
    print("\n" + "="*60)
    print("🎯 TESTING FACTORY PREFERENCES")
    print("="*60)
    
    agent_types = ['english_teacher', 'chinese_teacher', 'dynamic_assign']
    
    for agent_type in agent_types:
        print(f"\n🏭 Testing factory for {agent_type}...")
        try:
            engine = LLMEngineFactory.create_for_agent(agent_type=agent_type)
            
            print(f"   ✅ Engine created: {type(engine).__name__}")
            print(f"   📋 Model: {engine.model_name}")
            print(f"   🎯 Agent type: {agent_type}")
            
            # Test with specific preference
            if agent_type == 'english_teacher':
                try:
                    ollama_engine = LLMEngineFactory.create_for_agent(
                        agent_type=agent_type,
                        preferred_engine='ollama'
                    )
                    print(f"   🎭 Preferred engine: {type(ollama_engine).__name__}")
                except Exception as e:
                    print(f"   ⚠️  Preferred engine failed: {e}")
            
        except Exception as e:
            print(f"   ❌ Failed to create engine for {agent_type}: {e}")


def main():
    """Run all tests"""
    print("🚀 STARTING LLM ENGINE TESTS")
    print("This script will test different LLM engines and their integration")
    
    try:
        # Run all test suites
        test_engine_availability()
        test_engine_creation()
        test_simple_generation()
        test_agent_integration()
        test_cost_monitoring()
        test_factory_preferences()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS COMPLETED")
        print("="*60)
        print("✅ Check the results above to see which engines are working")
        print("💡 Make sure to install and configure your preferred engines")
        print("📚 See docs/Ollama使用指南.md for Ollama setup instructions")
        
    except KeyboardInterrupt:
        print("\n⛔ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        logger.error(f"Test suite error: {e}")


if __name__ == "__main__":
    main()
