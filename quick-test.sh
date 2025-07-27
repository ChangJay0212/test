#!/bin/bash

echo "🧪 Agentic Teaching System - 快速測試腳本"
echo

echo "📋 1. 檢查 Docker 容器狀態..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo

echo "📋 2. 檢查 LLM 引擎配置..."
docker exec agentic-app python -c "import os; print('DEFAULT_LLM_ENGINE:', os.environ.get('DEFAULT_LLM_ENGINE', 'not set')); print('GEMINI_API_KEY:', 'SET' if os.environ.get('GEMINI_API_KEY') else 'NOT SET'); print('OLLAMA_BASE_URL:', os.environ.get('OLLAMA_BASE_URL', 'not set'))"
echo

echo "📋 3. 測試 LLM 引擎連接..."
docker exec agentic-app python -c "
try:
    from llm_engines.factory import LLMEngineFactory
    engine = LLMEngineFactory.create_engine()
    print(f'✅ Engine created: {type(engine).__name__}')
    
    import time
    start_time = time.time()
    response = engine.generate_response('請簡短回答：你好嗎？')
    end_time = time.time()
    
    print(f'✅ Response time: {end_time - start_time:.2f} seconds')
    print(f'✅ Response: {response[:100]}...')
except Exception as e:
    print(f'❌ Error: {e}')
"
echo

echo "📋 4. 測試數學代理..."
docker exec agentic-app python -c "
try:
    from agents.math_agent import MathAgent
    agent = MathAgent()
    response = agent.solve_problem('計算 5 + 3 = ?')
    print(f'✅ Math Agent works: {response[:50]}...')
except Exception as e:
    print(f'❌ Math Agent Error: {e}')
"
echo

echo "📋 5. 測試語言代理..."
docker exec agentic-app python -c "
try:
    from agents.language_agent import LanguageAgent
    agent = LanguageAgent()
    response = agent.explain_grammar('英文單字 hello 的意思')
    print(f'✅ Language Agent works: {response[:50]}...')
except Exception as e:
    print(f'❌ Language Agent Error: {e}')
"
echo

echo "📋 6. 檢查 Kafka 連接..."
if docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list > /dev/null 2>&1; then
    echo "✅ Kafka is working"
else
    echo "❌ Kafka connection failed"
fi
echo

echo "📋 7. 檢查應用程式日誌 (最近 5 行)..."
docker-compose logs --tail=5 agentic-app
echo

# 如果使用 Ollama 容器，額外檢查
if docker ps | grep -q ollama; then
    echo "📋 8. 檢查 Ollama 模型..."
    docker exec ollama ollama list
    echo
fi

echo "✅ 測試完成！"
echo
echo "💡 如果所有測試都顯示 ✅，您的系統就準備好了！"
echo "💡 如果看到 ❌，請查看 TESTING_GUIDE.md 中的排除故障指南"
