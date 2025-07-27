@echo off
setlocal enabledelayedexpansion

echo 🔧 修復 Ollama 健康檢查和啟動問題
echo.

echo 🛑 停止所有容器...
docker-compose -f docker-compose.ollama.yml down

echo 🧹 移除舊的容器...
docker container rm -f agentic-app ollama kafka zookeeper 2>nul

echo 🔨 重新構建並啟動系統...
docker-compose -f docker-compose.ollama.yml up --build -d

echo ⏳ 等待服務啟動 (30 秒)...
timeout /t 30 /nobreak > nul

echo 📋 檢查容器狀態...
docker ps -a

echo.
echo 📋 檢查 Ollama 健康狀態...
docker exec ollama ollama list

echo.
echo 📋 嘗試啟動主應用程式（如果還沒啟動）...
docker-compose -f docker-compose.ollama.yml up -d agentic-app

echo.
echo ✅ 修復完成！請檢查容器狀態
echo 💡 如果 agentic-app 仍然是 Created 狀態，請運行：
echo    docker logs agentic-app
echo.
pause
