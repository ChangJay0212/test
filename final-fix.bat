@echo off
echo 🎯 最終解決方案：LLM 引擎啟動問題
echo.

echo 📋 問題分析：
echo - Kafka: ✅ 正常
echo - Ollama: ✅ 正常 (有 llama2 模型)
echo - 網路: ✅ 正常
echo - 環境變數: ✅ 正確設定
echo - 問題: LLM 引擎初始化時序
echo.

echo 🔧 解決步驟：
echo.

echo 1. 停止 agentic-app 容器
docker-compose -f docker-compose.ollama.yml stop agentic-app

echo.
echo 2. 驗證 Ollama 完全準備好
echo 等待 5 秒...
timeout /t 5 /nobreak > nul

echo 測試 Ollama API...
docker exec ollama ollama list

echo.
echo 3. 重新啟動 agentic-app (帶額外延遲)
docker-compose -f docker-compose.ollama.yml up -d agentic-app

echo.
echo 4. 監控啟動過程
echo 等待 15 秒讓應用程式完全啟動...
timeout /t 15 /nobreak > nul

echo.
echo 📋 檢查結果...
docker ps --format "table {{.Names}}\t{{.Status}}"

echo.
echo 📋 應用程式日誌 (最後 10 行)...
docker logs agentic-app --tail=10

echo.
echo ✅ 如果看到成功訊息，系統就準備好了！
echo 💡 現在可以執行：
echo    interactive-test.bat  # 進行功能測試
echo    quick-test.bat       # 快速健康檢查
echo.
pause
