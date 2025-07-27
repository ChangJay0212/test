@echo off
echo 🦙 Starting Agentic Teaching System with Ollama...
echo.

REM Start the system
echo 🔨 Starting containers...
docker-compose -f docker-compose.ollama.yml up -d

REM Wait for startup
echo ⏳ Waiting for startup (30 seconds)...
powershell -Command "Start-Sleep -Seconds 30"

REM Check status
echo 📋 Container status:
docker ps

echo.
echo ✅ System started! You can now run tests with:
echo    quick-test.bat
echo    interactive-test.bat
echo.
pause
