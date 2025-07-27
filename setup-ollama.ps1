# Quick Setup Script for Ollama
# Run this script to quickly configure the system for Ollama

Write-Host "🦙 Quick Ollama Setup" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green

# Check if .env exists
if (Test-Path ".env") {
    Write-Host "📁 Found existing .env file" -ForegroundColor Yellow
} else {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Cyan
    Copy-Item ".env.example" ".env"
}

# Configure for Ollama
Write-Host "⚙️  Configuring for Ollama..." -ForegroundColor Cyan

$envContent = Get-Content ".env" -Raw

# Set default engine to ollama
$envContent = $envContent -replace "DEFAULT_LLM_ENGINE=gemini", "DEFAULT_LLM_ENGINE=ollama"
$envContent = $envContent -replace "# DEFAULT_LLM_ENGINE=ollama", "DEFAULT_LLM_ENGINE=ollama"

# Comment out Gemini API key requirement
$envContent = $envContent -replace "GEMINI_API_KEY=your_gemini_api_key_here", "# GEMINI_API_KEY=your_gemini_api_key_here  # Not needed for Ollama"

# Save the configuration
$envContent | Set-Content ".env"

Write-Host "✅ Configuration updated!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Current configuration:" -ForegroundColor Cyan
Write-Host "   Engine: Ollama (local)" -ForegroundColor White
Write-Host "   Model: llama2" -ForegroundColor White
Write-Host "   URL: http://localhost:11434" -ForegroundColor White
Write-Host ""

# Check if Ollama is installed and running
Write-Host "🔍 Checking Ollama status..." -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Ollama is running!" -ForegroundColor Green
    
    # Parse available models
    $models = ($response.Content | ConvertFrom-Json).models
    if ($models.Count -gt 0) {
        Write-Host "📚 Available models:" -ForegroundColor Cyan
        foreach ($model in $models) {
            Write-Host "   - $($model.name)" -ForegroundColor White
        }
    } else {
        Write-Host "⚠️  No models found. Run: ollama pull llama2" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Ollama not running. Please:" -ForegroundColor Red
    Write-Host "   1. Install Ollama: https://ollama.ai" -ForegroundColor Gray
    Write-Host "   2. Run: ollama serve" -ForegroundColor Gray
    Write-Host "   3. Run: ollama pull llama2" -ForegroundColor Gray
}

Write-Host ""
Write-Host "🚀 Ready to start! Run: .\start.ps1" -ForegroundColor Green
