# PowerShell startup script for Agentic Teaching System
Write-Host "🚀 Starting Agentic Teaching System..." -ForegroundColor Green

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host ""
    Write-Host "📋 .env file created! Please configure your preferred LLM engine:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "For Gemini (cloud-based):" -ForegroundColor White
    Write-Host "  - Add your GEMINI_API_KEY" -ForegroundColor Gray
    Write-Host "  - Set DEFAULT_LLM_ENGINE=gemini" -ForegroundColor Gray
    Write-Host ""
    Write-Host "For Ollama (local):" -ForegroundColor White
    Write-Host "  - Install Ollama: https://ollama.ai" -ForegroundColor Gray
    Write-Host "  - Run: ollama pull llama2" -ForegroundColor Gray
    Write-Host "  - Run: ollama serve" -ForegroundColor Gray
    Write-Host "  - Set DEFAULT_LLM_ENGINE=ollama" -ForegroundColor Gray
    Write-Host "  - (GEMINI_API_KEY can remain empty)" -ForegroundColor Green
    Write-Host ""
    Write-Host "💡 Tip: You can keep both configurations and switch between them!" -ForegroundColor Yellow
    exit 1
}

# Check if Docker is running
try {
    docker info | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker not accessible"
    }
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check which LLM engine is configured
Write-Host "🔍 Checking LLM engine configuration..." -ForegroundColor Cyan

$envContent = Get-Content ".env" -Raw
if ($envContent -match "DEFAULT_LLM_ENGINE=ollama") {
    Write-Host "🦙 Configured for Ollama (local engine)" -ForegroundColor Green
    
    # Check if Ollama is running
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "✅ Ollama server is running" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Ollama server not detected. Please make sure:" -ForegroundColor Yellow
        Write-Host "   1. Ollama is installed: https://ollama.ai" -ForegroundColor Gray
        Write-Host "   2. Run: ollama serve" -ForegroundColor Gray
        Write-Host "   3. Run: ollama pull llama2" -ForegroundColor Gray
        Write-Host ""
        Write-Host "🤔 Continue anyway? System will fall back to other engines if available." -ForegroundColor Yellow
        $continue = Read-Host "Continue? (y/N)"
        if ($continue -ne "y" -and $continue -ne "Y") {
            exit 1
        }
    }
} elseif ($envContent -match "DEFAULT_LLM_ENGINE=gemini") {
    Write-Host "🌟 Configured for Gemini (cloud engine)" -ForegroundColor Green
    
    if ($envContent -match "GEMINI_API_KEY=your_gemini_api_key_here" -or $envContent -notmatch "GEMINI_API_KEY=.+") {
        Write-Host "⚠️  GEMINI_API_KEY not configured properly" -ForegroundColor Yellow
        Write-Host "💡 Please add your Gemini API key to .env file" -ForegroundColor Gray
    } else {
        Write-Host "✅ Gemini API key configured" -ForegroundColor Green
    }
} else {
    Write-Host "🔧 No specific engine configured, will auto-detect available engines" -ForegroundColor Yellow
}

# Build and start the system
Write-Host ""
Write-Host "🔨 Building and starting containers..." -ForegroundColor Cyan
docker-compose up --build

Write-Host "🛑 System stopped." -ForegroundColor Red
