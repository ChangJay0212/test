@echo off
setlocal enabledelayedexpansion

echo 🧪 Agentic Teaching System - 快速健康檢查
echo.

echo 📋 1. 檢查 Docker 容器狀態...
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.

echo 📋 2. 檢查 LLM 引擎配置...
docker exec agentic-app python -c "import os; print('DEFAULT_LLM_ENGINE:', os.environ.get('DEFAULT_LLM_ENGINE', 'ollama')); print('GEMINI_API_KEY:', 'SET' if os.environ.get('GEMINI_API_KEY') else 'NOT SET'); print('OLLAMA_BASE_URL:', os.environ.get('OLLAMA_BASE_URL', 'http://ollama:11434'))"
echo.

echo 📋 3. 測試 LLM 引擎連接...
docker exec agentic-app python -c "
try:
    from llm_engines.factory import LLMEngineFactory
    engine = LLMEngineFactory.create_for_agent(agent_type='english_teacher')
    print(f'✅ Engine created: {type(engine).__name__} with model: {engine.model_name}')
    print('✅ LLM engine connectivity test passed')
except Exception as e:
    print(f'❌ LLM Engine Error: {e}')
"
echo.

echo 📋 4. 測試英語老師代理...
docker exec agentic-app python -c "
try:
    from llm_engines.factory import LLMEngineFactory
    engine = LLMEngineFactory.create_for_agent(agent_type='english_teacher')
    messages = [{'role': 'user', 'content': 'Hello, can you help me?'}]
    response = engine.generate_response(messages)
    print(f'✅ English teacher responding: {response[:50]}...')
except Exception as e:
    print(f'❌ English Teacher Error: {e}')
"
echo.

echo 📋 5. 測試中文老師代理...
docker exec agentic-app python -c "
try:
    from llm_engines.factory import LLMEngineFactory  
    engine = LLMEngineFactory.create_for_agent(agent_type='chinese_teacher')
    messages = [{'role': 'user', 'content': '你好，你能幫助我嗎？'}]
    response = engine.generate_response(messages)
    print(f'✅ Chinese teacher responding: {response[:50]}...')
except Exception as e:
    print(f'❌ Chinese Teacher Error: {e}')
"
echo.

echo 📋 6. 檢查 Kafka 連接...
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Kafka is working
) else (
    echo ❌ Kafka connection failed
)
echo.

echo 📋 7. 檢查應用程式狀態 (最近 5 行日誌)...
docker logs agentic-app --tail=5
echo.

REM 如果使用 Ollama 容器，額外檢查
docker ps | findstr ollama >nul 2>&1
if !errorlevel! equ 0 (
    echo 📋 8. 檢查 Ollama 模型...
    docker exec ollama ollama list
    echo.
)

echo ✅ 健康檢查完成！
echo.
echo 💡 如果所有測試都顯示 ✅，您的系統運行正常！
echo 💡 如果看到 ❌，請查看 trouble.txt 中的排除故障指南
echo 💡 使用 interactive-test.bat 進行完整的對話測試
pause
