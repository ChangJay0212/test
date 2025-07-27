# 🧪 Agentic Teaching System 測試指南

## 🚀 啟動後的測試步驟

### 1. 檢查 Docker 容器狀態

```bash
# 檢查所有容器是否正在運行
docker ps

# 應該看到類似這樣的輸出：
# CONTAINER ID   IMAGE              COMMAND                  STATUS
# abc123def456   agentic-app        "python app.py"          Up 2 minutes (healthy)
# def456ghi789   confluentinc/cp-kafka  "/etc/confluent/dock…"  Up 3 minutes (healthy)
# ghi789jkl012   confluentinc/cp-zookeeper  "/etc/confluent/dock…"  Up 3 minutes (healthy)
# [如果使用 Ollama 容器] ollama/ollama  "/bin/ollama serve"  Up 3 minutes (healthy)
```

### 2. 檢查應用程式日誌

```bash
# 查看主應用程式日誌
docker-compose logs agentic-app

# 或使用 Ollama 版本
docker-compose -f docker-compose.ollama.yml logs agentic-app

# 正常的日誌應該包含：
# ✅ Successfully connected to Kafka
# ✅ LLM Engine initialized: [gemini/ollama]
# 🚀 Agentic Teaching System started successfully
```

### 3. 測試 LLM 引擎連接

#### 測試 Ollama（如果使用）
```bash
# 如果使用容器化 Ollama
docker exec ollama ollama list

# 如果使用本地 Ollama
curl http://localhost:11434/api/tags

# 應該看到可用的模型列表，例如：
# NAME            ID              SIZE    MODIFIED
# llama2:latest   abc123def456    3.8GB   2 days ago
```

#### 測試 Gemini（如果使用）
```bash
# 檢查 API 金鑰是否設定正確
docker exec agentic-app python -c "
import os
print('GEMINI_API_KEY:', 'SET' if os.environ.get('GEMINI_API_KEY') else 'NOT SET')
print('DEFAULT_LLM_ENGINE:', os.environ.get('DEFAULT_LLM_ENGINE', 'not set'))
"
```

### 4. 互動式測試

#### 方法 1：使用 Docker exec 進入容器
```bash
# 進入應用程式容器
docker exec -it agentic-app bash

# 在容器內測試 Python 腳本
python -c "
from llm_engines.factory import LLMEngineFactory
engine = LLMEngineFactory.create_engine()
print(f'Engine type: {type(engine).__name__}')
response = engine.generate_response('Hello, please say hi back!')
print(f'Response: {response}')
"
```

#### 方法 2：創建測試腳本
```bash
# 創建一個簡單的測試檔案
echo 'from llm_engines.factory import LLMEngineFactory

print("🧪 Testing LLM Engine...")
engine = LLMEngineFactory.create_engine()
print(f"✅ Engine created: {type(engine).__name__}")

# 測試簡單的對話
response = engine.generate_response("請用中文回答：你好嗎？")
print(f"📝 Response: {response}")

print("✅ Test completed successfully!")
' > test_llm.py

# 在容器內執行測試
docker exec agentic-app python test_llm.py
```

### 5. 測試教學代理功能

```bash
# 測試數學代理
docker exec agentic-app python -c "
from agents.math_agent import MathAgent
agent = MathAgent()
response = agent.solve_problem('請解這個方程式：2x + 5 = 15')
print(f'Math Agent Response: {response}')
"

# 測試語言代理
docker exec agentic-app python -c "
from agents.language_agent import LanguageAgent
agent = LanguageAgent()
response = agent.explain_grammar('請解釋英文的現在完成式')
print(f'Language Agent Response: {response}')
"
```

### 6. 測試 Kafka 消息系統

```bash
# 檢查 Kafka 主題
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list

# 應該看到系統創建的主題，例如：
# math-problems
# language-questions
# system-events
```

### 7. 效能測試

```bash
# 測試回應時間
docker exec agentic-app python -c "
import time
from llm_engines.factory import LLMEngineFactory

engine = LLMEngineFactory.create_engine()
start_time = time.time()
response = engine.generate_response('Hello!')
end_time = time.time()
print(f'Response time: {end_time - start_time:.2f} seconds')
print(f'Response: {response[:100]}...')
"
```

## 🔍 常見問題排除

### 問題 1：容器無法啟動
```bash
# 檢查 Docker 資源使用情況
docker system df
docker stats

# 清理未使用的資源
docker system prune
```

### 問題 2：Ollama 模型下載失敗
```bash
# 手動下載模型
docker exec ollama ollama pull llama2

# 檢查模型狀態
docker exec ollama ollama list
```

### 問題 3：Kafka 連接問題
```bash
# 重啟 Kafka 相關服務
docker-compose restart zookeeper kafka

# 檢查 Kafka 日誌
docker-compose logs kafka
```

### 問題 4：API 回應錯誤
```bash
# 檢查環境變數
docker exec agentic-app env | grep -E "(GEMINI|OLLAMA|DEFAULT)"

# 檢查網路連接
docker exec agentic-app ping host.docker.internal
```

## ✅ 成功指標

系統正常運行時，您應該看到：

1. **容器狀態**：所有容器都顯示 "healthy" 狀態
2. **日誌輸出**：沒有錯誤訊息，有成功連接的訊息
3. **LLM 回應**：能夠獲得合理的文字回應
4. **代理功能**：數學和語言代理能正常工作
5. **Kafka 運作**：訊息主題正常創建

## 🎯 下一步

如果所有測試都通過：
- 您可以開始使用系統進行教學
- 嘗試不同的問題類型
- 探索代理之間的協作功能
- 檢查成本追蹤和使用統計

如果遇到問題：
- 檢查上述排除故障步驟
- 查看詳細的容器日誌
- 確認 `.env` 檔案配置正確
- 重新啟動系統
