@echo off
setlocal enabledelayedexpansion

echo 🔧 修復 Kafka 配置問題
echo.
echo 💡 問題：Confluent 指標報告器未找到
echo ✅ 解決方案：已移除 Confluent 特定配置，使用純 Apache Kafka
echo.

echo 🛑 停止所有容器...
docker-compose -f docker-compose.ollama.yml down
docker-compose down

echo 🧹 清理舊的容器和網路...
docker system prune -f

echo 🔨 重新啟動修復後的系統...
docker-compose -f docker-compose.ollama.yml up --build -d zookeeper kafka ollama

if !errorlevel! neq 0 (
    echo ❌ 啟動失敗，請檢查 Docker 日誌
    pause
    exit /b 1
)

echo ⏳ 等待服務啟動 (約 30 秒)...
timeout /t 30 /nobreak > nul

echo 📋 檢查容器狀態...
docker ps

echo.
echo ✅ 修復完成！現在您可以：
echo 1. 運行 quick-test.bat 進行健康檢查
echo 2. 運行 interactive-test.bat 進行互動式測試
echo 3. 重新啟動主應用程式：docker-compose -f docker-compose.ollama.yml up -d agentic-app
echo.
pause
