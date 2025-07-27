#!/usr/bin/env python3
"""
Simple demo script showing usage of different LLM engines
"""

import sys
import os

# Add project root to path
sys.path.append('.')

from llm_engines.factory import LLMEngineFactory


def demo_gemini():
    """Demo Gemini engine usage"""
    print("\n🌟 Gemini Engine Demo")
    print("-" * 40)
    
    try:
        # Create Gemini engine
        engine = LLMEngineFactory.create_engine("gemini")
        print(f"✅ Created Gemini engine: {engine.model_name}")
        
        # Generate response
        response = engine.generate_response(
            "Hello! Please tell me about yourself in one sentence.",
            max_tokens=100,
            temperature=0.7
        )
        
        print(f"💬 Response: {response}")
        
        # Show cost statistics
        stats = engine.get_cost_statistics()
        print(f"💰 Cost: ${stats['total_cost']:.6f}")
        print(f"🔢 Tokens: {stats['total_tokens']}")
        
    except Exception as e:
        print(f"❌ Gemini demo failed: {e}")


def demo_ollama():
    """Demo Ollama engine usage"""
    print("\n🦙 Ollama Engine Demo")
    print("-" * 40)
    
    try:
        # Create Ollama engine
        engine = LLMEngineFactory.create_engine("ollama")
        print(f"✅ Created Ollama engine: {engine.model_name}")
        
        # Generate response
        response = engine.generate_response(
            "Hello! Please tell me about yourself in one sentence.",
            max_tokens=100,
            temperature=0.7
        )
        
        print(f"💬 Response: {response}")
        
        # Show usage statistics
        stats = engine.get_cost_statistics()
        print(f"💰 Cost: ${stats['total_cost']:.6f} (Free!)")
        print(f"🔢 Tokens: {stats['total_tokens']}")
        
    except Exception as e:
        print(f"❌ Ollama demo failed: {e}")
        print("💡 Make sure Ollama is installed and running:")
        print("   1. Install: Visit https://ollama.ai")
        print("   2. Pull model: ollama pull llama2")
        print("   3. Start service: ollama serve")


def demo_factory():
    """Demo factory engine selection"""
    print("\n🏭 Engine Factory Demo")
    print("-" * 40)
    
    factory = LLMEngineFactory()
    
    # Show available engines
    print("Available engines:")
    available = factory.get_available_engines()
    for name, info in available.items():
        print(f"  - {name}: {info.get('name', 'Unknown')} ({info.get('type', 'Unknown')})")
    
    # Test validation
    print("\nEngine validation:")
    for engine_type in ['gemini', 'ollama']:
        validation = factory.validate_engine_config(engine_type)
        status = "✅" if validation.get('valid') else "❌"
        print(f"  {status} {engine_type}: {validation.get('message') or validation.get('error')}")
    
    # Auto-select best engine
    try:
        engine = factory.create_for_agent("english_teacher")
        print(f"\n🎯 Auto-selected engine: {type(engine).__name__}")
        print(f"📋 Model: {engine.model_name}")
    except Exception as e:
        print(f"❌ Auto-selection failed: {e}")


def main():
    """Run all demos"""
    print("🚀 LLM Engine Demo")
    print("=" * 50)
    print("This demo shows how to use different LLM engines")
    
    # Check environment
    print(f"\n📁 Working directory: {os.getcwd()}")
    print(f"🐍 Python path: {sys.executable}")
    
    # Run demos
    demo_factory()
    demo_gemini()
    demo_ollama()
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("💡 See docs/Ollama使用指南.md for more information")


if __name__ == "__main__":
    main()
