@echo off
setlocal enabledelayedexpansion

REM Startup script for Agentic Teaching System (Windows)
echo 🚀 Starting Agentic Teaching System...
echo.

REM Check if .env file exists
if not exist ".env" (
    echo 📝 Creating .env file from template...
    copy .env.example .env >nul
    echo.
    echo 📋 .env file created! Please configure your preferred LLM engine:
    echo.
    echo For Gemini (cloud-based):
    echo   - Add your GEMINI_API_KEY
    echo   - Set DEFAULT_LLM_ENGINE=gemini
    echo.
    echo For Ollama (local):
    echo   - Install Ollama: https://ollama.ai
    echo   - Run: ollama pull llama2
    echo   - Run: ollama serve
    echo   - Set DEFAULT_LLM_ENGINE=ollama
    echo   - (GEMINI_API_KEY can remain empty)
    echo.
    pause
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Check which LLM engine is configured
echo 🔍 Checking LLM engine configuration...

findstr /c:"DEFAULT_LLM_ENGINE=ollama" ".env" >nul
if !errorlevel! equ 0 (
    echo 🦙 Configured for Ollama (local engine)
    
    REM Check if Ollama is running using PowerShell
    powershell -command "try { Invoke-WebRequest -Uri 'http://localhost:11434/api/tags' -TimeoutSec 3 -UseBasicParsing | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ Ollama server is running
    ) else (
        echo ⚠️  Ollama server not detected. Please make sure:
        echo    1. Ollama is installed: https://ollama.ai
        echo    2. Run: ollama serve
        echo    3. Run: ollama pull llama2
        echo.
        echo 🤔 Continue anyway? System will fall back to other engines if available.
        set /p continue="Continue? (y/N): "
        if /i "!continue!" neq "y" (
            exit /b 1
        )
    )
) else (
    findstr /c:"DEFAULT_LLM_ENGINE=gemini" ".env" >nul
    if !errorlevel! equ 0 (
        echo 🌟 Configured for Gemini (cloud engine)
        
        findstr /c:"GEMINI_API_KEY=your_gemini_api_key_here" ".env" >nul
        if !errorlevel! equ 0 (
            echo ⚠️  GEMINI_API_KEY not configured properly
            echo 💡 Please add your Gemini API key to .env file
        ) else (
            findstr /c:"GEMINI_API_KEY=" ".env" | findstr /v /c:"GEMINI_API_KEY=$" | findstr /v /c:"GEMINI_API_KEY= " >nul
            if !errorlevel! equ 0 (
                echo ✅ Gemini API key configured
            ) else (
                echo ⚠️  GEMINI_API_KEY appears to be empty
            )
        )
    ) else (
        echo 🔧 No specific engine configured, will auto-detect available engines
    )
)

REM Build and start the system
echo.
echo 🔨 Building and starting containers...
docker-compose up --build

echo 🛑 System stopped.
pause
