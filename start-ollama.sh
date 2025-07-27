#!/bin/bash

# Ollama Startup Script for Linux/macOS
echo "🦙 Starting Agentic Teaching System with Ollama in Docker..."
echo

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo
    echo "✅ .env file created with Ollama configuration!"
    echo
else
    echo "📁 Found existing .env file"
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "🔧 This will start Ollama inside Docker containers"
echo "📥 First time setup will download the Ollama model (this may take a while)"
echo

# Clean up any existing containers
echo "🧹 Cleaning up existing containers..."
docker-compose -f docker-compose.ollama.yml down > /dev/null 2>&1

# Start the system with Ollama
echo "🔨 Building and starting containers (including Ollama)..."
docker-compose -f docker-compose.ollama.yml up --build -d zookeeper kafka ollama

if [ $? -ne 0 ]; then
    echo "❌ Failed to start infrastructure containers. Please check the error messages above."
    exit 1
fi

echo "⏳ Waiting for Kafka and Ollama to be healthy..."
echo "🔄 This may take 1-2 minutes for first-time setup..."

# Wait for services to be healthy
check_health() {
    local service=$1
    local status=$(docker inspect $service --format="{{.State.Health.Status}}" 2>/dev/null)
    if [ "$status" = "healthy" ]; then
        return 0
    else
        return 1
    fi
}

# Wait loop
while true; do
    sleep 5
    
    if check_health kafka && check_health ollama; then
        echo "✅ Infrastructure services are ready!"
        break
    else
        if ! check_health kafka; then
            echo "🔄 Waiting for Kafka to be ready..."
        fi
        if ! check_health ollama; then
            echo "🔄 Waiting for Ollama to be ready..."
        fi
    fi
done

echo "📥 Pulling Llama model (this may take several minutes on first run)..."
docker exec ollama ollama pull llama2

if [ $? -ne 0 ]; then
    echo "⚠️  Model pull failed, but continuing anyway..."
    echo "💡 You can manually pull the model later with: docker exec ollama ollama pull llama2"
fi

echo "🚀 Starting main application..."
docker-compose -f docker-compose.ollama.yml up -d agentic-app

echo "✅ Setup complete! Showing application logs..."
docker-compose -f docker-compose.ollama.yml logs -f agentic-app

echo "🛑 System stopped."
