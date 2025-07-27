# PowerShell Compatible Ollama Startup Script
Write-Host "🦙 Starting Agentic Teaching System with Ollama" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ .env file created with Ollama configuration!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "📁 Found existing .env file" -ForegroundColor Cyan
}

# Check if Docker is running
try {
    docker info | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker not accessible"
    }
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "🔧 Starting Ollama system in Docker containers" -ForegroundColor Cyan
Write-Host "📥 This may take a few minutes for first-time setup" -ForegroundColor Yellow
Write-Host ""

# Clean up existing containers
Write-Host "🧹 Cleaning up existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.ollama.yml down 2>$null

# Step 1: Start Zookeeper
Write-Host "🔧 Step 1/5: Starting Zookeeper..." -ForegroundColor Cyan
docker-compose -f docker-compose.ollama.yml up -d zookeeper
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start Zookeeper" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "⏳ Waiting 15 seconds for Zookeeper..." -ForegroundColor Yellow
Start-Sleep 15

# Step 2: Start Kafka
Write-Host "🔧 Step 2/5: Starting Kafka..." -ForegroundColor Cyan
docker-compose -f docker-compose.ollama.yml up -d kafka
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start Kafka" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "⏳ Waiting 45 seconds for Kafka to be ready..." -ForegroundColor Yellow
for ($i = 1; $i -le 45; $i++) {
    if ($i -le 15) { Write-Host "Kafka starting... ($i/45)" -ForegroundColor Gray }
    elseif ($i -le 30) { Write-Host "Kafka initializing... ($i/45)" -ForegroundColor Gray }
    else { Write-Host "Kafka almost ready... ($i/45)" -ForegroundColor Gray }
    Start-Sleep 1
}

# Step 3: Start Ollama
Write-Host "🦙 Step 3/5: Starting Ollama..." -ForegroundColor Cyan
docker-compose -f docker-compose.ollama.yml up -d ollama
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start Ollama" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "⏳ Waiting 30 seconds for Ollama to be ready..." -ForegroundColor Yellow
for ($i = 1; $i -le 30; $i++) {
    if ($i -le 10) { Write-Host "Ollama starting... ($i/30)" -ForegroundColor Gray }
    elseif ($i -le 20) { Write-Host "Ollama loading... ($i/30)" -ForegroundColor Gray }
    else { Write-Host "Ollama ready soon... ($i/30)" -ForegroundColor Gray }
    Start-Sleep 1
}

# Step 4: Download model
Write-Host "📥 Step 4/5: Downloading Llama model (may take several minutes)..." -ForegroundColor Cyan
docker exec ollama ollama pull llama2
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Model download failed, but continuing..." -ForegroundColor Yellow
    Write-Host "💡 You can try again later with: docker exec ollama ollama pull llama2" -ForegroundColor Gray
    Write-Host ""
}

# Step 5: Start application
Write-Host "🚀 Step 5/5: Building and starting main application..." -ForegroundColor Cyan
docker-compose -f docker-compose.ollama.yml up --build -d agentic-app
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start application" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "⏳ Waiting 15 seconds for application to start..." -ForegroundColor Yellow
Start-Sleep 15

Write-Host ""
Write-Host "✅ Setup complete! Checking container status..." -ForegroundColor Green

# Check container status
$containers = docker ps --format "table {{.Names}}\t{{.Status}}" --filter "name=zookeeper" --filter "name=kafka" --filter "name=ollama" --filter "name=agentic-app"
Write-Host $containers

Write-Host ""
Write-Host "🔍 Quick health checks:" -ForegroundColor Cyan

# Test Ollama
Write-Host "🦙 Testing Ollama API..." -ForegroundColor Yellow
try {
    docker exec ollama curl -s http://localhost:11434/api/tags | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Ollama: API responding" -ForegroundColor Green
        Write-Host "📚 Available models:" -ForegroundColor Cyan
        docker exec ollama ollama list
    } else {
        throw "API not responding"
    }
} catch {
    Write-Host "⚠️  Ollama: Still starting up (this is normal)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 System startup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 What you can do now:" -ForegroundColor Cyan
Write-Host "  📊 View logs:        docker-compose -f docker-compose.ollama.yml logs -f agentic-app" -ForegroundColor Gray
Write-Host "  🔍 Check status:     docker ps" -ForegroundColor Gray
Write-Host "  🛑 Stop system:      docker-compose -f docker-compose.ollama.yml down" -ForegroundColor Gray
Write-Host "  📝 Test Ollama:      docker exec ollama ollama list" -ForegroundColor Gray
Write-Host ""

$showLogs = Read-Host "Show application logs now? (y/N)"
if ($showLogs -eq "y" -or $showLogs -eq "Y") {
    Write-Host ""
    Write-Host "📊 Application logs (Press Ctrl+C to stop):" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Gray
    docker-compose -f docker-compose.ollama.yml logs -f agentic-app
}

Write-Host ""
Write-Host "🛑 Done!" -ForegroundColor Green
Read-Host "Press Enter to exit"
