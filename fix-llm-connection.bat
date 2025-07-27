@echo off
setlocal enabledelayedexpansion

echo 🔧 修復 LLM 引擎連接問題
echo.

echo 📋 當前問題：agentic-app 無法連接到 LLM 引擎
echo 💡 解決方案：添加啟動延遲和重試邏輯
echo.

echo 🛑 停止 agentic-app...
docker-compose -f docker-compose.ollama.yml stop agentic-app

echo ⏳ 等待其他服務穩定 (15 秒)...
timeout /t 15 /nobreak > nul

echo 🧪 測試 Ollama 連接...
docker exec kafka wget -qO- http://ollama:11434/api/tags

echo.
echo 🚀 重新啟動 agentic-app...
docker-compose -f docker-compose.ollama.yml up -d agentic-app

echo ⏳ 等待應用程式啟動 (10 秒)...
timeout /t 10 /nobreak > nul

echo 📋 檢查容器狀態...
docker ps

echo.
echo 📋 檢查應用程式日誌...
docker logs agentic-app --tail=20

echo.
echo ✅ 如果仍有問題，請執行：
echo    docker logs agentic-app -f  # 查看實時日誌
echo    interactive-test.bat        # 進行功能測試
echo.
pause
