@echo off
setlocal enabledelayedexpansion

echo 🦙 Starting Agentic Teaching System with Ollama in Docker...
echo.

REM Check if .env file exists
if not exist ".env" (
    echo 📝 Creating .env file from template...
    copy ".env.example" ".env" >nul
    echo.
    echo ✅ .env file created with Ollama configuration!
    echo.
) else (
    echo 📁 Found existing .env file
)

REM Check if Docker is running
docker info >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo 🔧 This will start Ollama inside Docker containers
echo 📥 First time setup will download the Ollama model (this may take a while)
echo.

REM Start the system with Ollama
echo 🔨 Building and starting containers (including Ollama)...
docker-compose -f docker-compose.ollama.yml up --build -d zookeeper kafka ollama

if !errorlevel! neq 0 (
    echo ❌ Failed to start infrastructure containers. Please check the error messages above.
    pause
    exit /b 1
)

echo ⏳ Waiting for Kafka and Ollama to be healthy...
echo 🔄 This may take 1-2 minutes for first-time setup...

:wait_loop
ping 127.0.0.1 -n 6 > nul

REM Check if services are healthy using docker inspect
docker inspect kafka --format="{{.State.Health.Status}}" 2>nul | find "healthy" >nul
set kafka_ready=!errorlevel!

docker inspect ollama --format="{{.State.Health.Status}}" 2>nul | find "healthy" >nul
set ollama_ready=!errorlevel!

if !kafka_ready! neq 0 (
    echo 🔄 Waiting for Kafka to be ready...
    goto wait_loop
)

if !ollama_ready! neq 0 (
    echo 🔄 Waiting for Ollama to be ready...
    goto wait_loop
)

echo ✅ Infrastructure services are ready!

echo 📥 Pulling Llama model (this may take several minutes on first run)...
docker exec ollama ollama pull llama2

if !errorlevel! neq 0 (
    echo ⚠️  Model pull failed, but continuing anyway...
    echo 💡 You can manually pull the model later with: docker exec ollama ollama pull llama2
)

echo 🚀 Starting main application...
docker-compose -f docker-compose.ollama.yml up -d agentic-app

echo ✅ Setup complete! Showing application logs...
docker-compose -f docker-compose.ollama.yml logs -f agentic-app

echo 🛑 System stopped.
pause
