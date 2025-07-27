#!/usr/bin/env python3
"""
Debug script to test LLM engine connectivity
"""
import os
import sys
import requests
import time

def test_ollama_connection():
    """Test Ollama connection"""
    print("🔍 Testing Ollama Connection...")
    
    ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    print(f"OLLAMA_BASE_URL: {ollama_url}")
    
    try:
        print("Attempting to connect to Ollama...")
        response = requests.get(f"{ollama_url}/api/tags", timeout=10)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama connected! Available models: {[m['name'] for m in models]}")
            return True
        else:
            print(f"❌ Ollama responded with error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to connect to Ollama: {e}")
        return False

def test_gemini_config():
    """Test Gemini configuration"""
    print("\n🔍 Testing Gemini Configuration...")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print(f"✅ GEMINI_API_KEY is set (length: {len(api_key)})")
        return True
    else:
        print("❌ GEMINI_API_KEY is not set")
        return False

def test_environment():
    """Test environment variables"""
    print("\n🔍 Environment Variables:")
    
    env_vars = [
        'DEFAULT_LLM_ENGINE',
        'OLLAMA_BASE_URL', 
        'OLLAMA_MODEL',
        'OLLAMA_TIMEOUT',
        'GEMINI_API_KEY'
    ]
    
    for var in env_vars:
        value = os.getenv(var, 'NOT SET')
        if var == 'GEMINI_API_KEY' and value != 'NOT SET':
            value = f"SET (length: {len(value)})"
        print(f"  {var}: {value}")

def test_network_connectivity():
    """Test network connectivity"""
    print("\n🔍 Testing Network Connectivity...")
    
    # Test internal Docker network
    hosts_to_test = [
        'ollama:11434',
        'localhost:11434',
        'kafka:29092',
        'zookeeper:2181'
    ]
    
    for host in hosts_to_test:
        try:
            import socket
            hostname, port = host.split(':')
            port = int(port)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((hostname, port))
            sock.close()
            
            if result == 0:
                print(f"✅ {host} is reachable")
            else:
                print(f"❌ {host} is not reachable")
                
        except Exception as e:
            print(f"❌ Error testing {host}: {e}")

def main():
    print("🧪 LLM Engine Connectivity Test")
    print("=" * 50)
    
    test_environment()
    test_network_connectivity() 
    
    ollama_ok = test_ollama_connection()
    gemini_ok = test_gemini_config()
    
    print("\n📋 Summary:")
    print(f"  Ollama: {'✅ Available' if ollama_ok else '❌ Not Available'}")
    print(f"  Gemini: {'✅ Configured' if gemini_ok else '❌ Not Configured'}")
    
    if not ollama_ok and not gemini_ok:
        print("\n❌ No LLM engines are available!")
        print("💡 Suggestions:")
        print("  1. Check if Ollama container is running and healthy")
        print("  2. Verify OLLAMA_BASE_URL points to correct container")
        print("  3. Or configure GEMINI_API_KEY for fallback")
        sys.exit(1)
    else:
        print("\n✅ At least one LLM engine should work!")

if __name__ == "__main__":
    main()
