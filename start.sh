#!/bin/bash

# Agentic Teaching System Startup Script for Linux/macOS
echo "🎯 Starting Agentic Teaching System in Docker..."
echo

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo
    echo "✅ .env file created! Please configure your preferred LLM engine:"
    echo
    echo "For Gemini (cloud-based):"
    echo "  - Add your GEMINI_API_KEY"
    echo "  - Set DEFAULT_LLM_ENGINE=gemini"
    echo
    echo "For Ollama (local):"
    echo "  - Use the start-ollama.sh script for Docker-based Ollama"
    echo "  - Or install Ollama locally: https://ollama.ai"
    echo "  - Set DEFAULT_LLM_ENGINE=ollama"
    echo
    echo "💡 For Ollama in Docker, use: ./start-ollama.sh"
    echo
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Clean up any existing containers
echo "🧹 Cleaning up existing containers..."
docker-compose down > /dev/null 2>&1

# Start the system
echo "🔨 Building and starting containers..."
docker-compose up --build -d zookeeper kafka

if [ $? -ne 0 ]; then
    echo "❌ Failed to start infrastructure containers. Please check the error messages above."
    exit 1
fi

echo "⏳ Waiting for Kafka to be healthy..."
echo "🔄 This may take 1-2 minutes for first-time setup..."

# Wait for Kafka to be healthy
while true; do
    sleep 5
    
    local status=$(docker inspect kafka --format="{{.State.Health.Status}}" 2>/dev/null)
    if [ "$status" = "healthy" ]; then
        echo "✅ Infrastructure services are ready!"
        break
    else
        echo "🔄 Waiting for Kafka to be ready..."
    fi
done

echo "🚀 Starting main application..."
docker-compose up -d agentic-app

echo "✅ Setup complete! Showing application logs..."
docker-compose logs -f agentic-app

echo "🛑 System stopped."
