# Ollama 引擎使用指南

這個文檔說明如何在 Agentic System 中使用 Ollama 引擎。

## 什麼是 Ollama

Ollama 是一個本地運行的大型語言模型平台，允許您在自己的機器上運行各種開源 LLM 模型，如 Llama 2, Codellama, Mistral 等。

## 安裝和設定

### 1. 安裝 Ollama

首先在您的系統上安裝 Ollama：

**Windows/macOS/Linux:**
```bash
# 訪問 https://ollama.ai 下載並安裝 Ollama
# 或使用以下命令（Linux/macOS）
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. 啟動 Ollama 服務

```bash
# 啟動 Ollama 服務
ollama serve
```

### 3. 下載模型

```bash
# 下載 Llama 2 模型（預設）
ollama pull llama2

# 或下載其他模型
ollama pull mistral
ollama pull codellama
ollama pull vicuna
```

### 4. 環境配置

在您的 `.env` 文件中添加 Ollama 配置：

```env
# Ollama 配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OLLAMA_TIMEOUT=60

# 預設 LLM 引擎（可選）
DEFAULT_LLM_ENGINE=ollama
```

## 使用方式

### 1. 基本使用

```python
from llm_engines.ollama_engine import OllamaEngine

# 創建 Ollama 引擎
engine = OllamaEngine(
    model_name="llama2",
    base_url="http://localhost:11434"
)

# 生成回應
response = engine.generate_response("Hello, how are you?")
print(response)
```

### 2. 使用工廠模式

```python
from llm_engines.factory import LLMEngineFactory

# 創建 Ollama 引擎
engine = LLMEngineFactory.create_engine("ollama")

# 或為特定 agent 創建
engine = LLMEngineFactory.create_for_agent(
    agent_type="english_teacher",
    preferred_engine="ollama"
)
```

### 3. 在 Agent 中使用

```python
from agents.english_teacher import EnglishTeacherAgent

# 創建使用 Ollama 的英語老師
teacher = EnglishTeacherAgent(engine_type="ollama")

# 處理訊息
response = teacher.process_message({
    "message": "Can you help me with English grammar?",
    "user_id": "user123"
})
```

### 4. 動態引擎選擇

```python
from core.dynamic_assign import DynamicAssigner

# 創建使用 Ollama 的動態分配器
assigner = DynamicAssigner(engine_type="ollama")
```

## 支援的模型

Ollama 支援多種開源模型：

| 模型名稱 | 大小 | 用途 | 下載命令 |
|---------|------|------|----------|
| llama2 | 7B | 通用對話 | `ollama pull llama2` |
| llama2:13b | 13B | 更好的通用對話 | `ollama pull llama2:13b` |
| mistral | 7B | 指令跟隨 | `ollama pull mistral` |
| codellama | 7B | 程式碼生成 | `ollama pull codellama` |
| vicuna | 7B | 對話式 AI | `ollama pull vicuna` |
| orca-mini | 3B | 輕量級模型 | `ollama pull orca-mini` |

## 優勢與限制

### 優勢
- **隱私安全**: 數據不會離開您的機器
- **無 API 成本**: 完全免費使用
- **離線工作**: 不需要網路連接
- **可自定義**: 可以微調和修改模型

### 限制
- **硬體需求**: 需要足夠的 RAM（至少 8GB，推薦 16GB+）
- **處理速度**: 比雲端 API 慢，取決於硬體
- **模型限制**: 受限於可用的開源模型
- **維護成本**: 需要自己管理和更新

## 效能最佳化

### 1. 硬體建議
- **RAM**: 最少 8GB，推薦 16GB 或更多
- **GPU**: 支援 CUDA 的 NVIDIA GPU 會大幅提升速度
- **CPU**: 多核心 CPU 有助於推理速度

### 2. 配置調整

```python
# 創建引擎時調整參數
engine = OllamaEngine(
    model_name="llama2",
    base_url="http://localhost:11434"
)

# 生成時調整參數
response = engine.generate_response(
    prompt="Your question here",
    temperature=0.7,      # 控制創造性（0.0-1.0）
    max_tokens=512,       # 限制回應長度
)
```

### 3. 模型選擇建議

- **輕量級應用**: 使用 `orca-mini` 或 `llama2:7b`
- **平衡性能**: 使用 `mistral` 或 `llama2:13b`
- **程式碼相關**: 使用 `codellama`
- **多語言支援**: 使用 `llama2` 或 `mistral`

## 故障排除

### 1. 連接問題

```bash
# 檢查 Ollama 服務狀態
curl http://localhost:11434/api/tags
```

### 2. 模型未找到

```bash
# 列出已安裝的模型
ollama list

# 下載需要的模型
ollama pull <model_name>
```

### 3. 記憶體不足

```bash
# 使用較小的模型
ollama pull orca-mini

# 或調整系統交換空間
```

### 4. 效能問題

- 確保使用 SSD 硬碟
- 關閉不必要的應用程式
- 考慮使用量化版本的模型

## 成本監控

即使 Ollama 是免費的，系統仍會追蹤使用情況：

```python
# 獲取使用統計
stats = engine.get_cost_statistics()
print(f"總請求數: {stats['total_requests']}")
print(f"總 tokens: {stats['total_tokens']}")
print(f"平均每請求 tokens: {stats['average_tokens_per_request']}")
```

## 與 Gemini 比較

| 特性 | Ollama | Gemini |
|------|--------|--------|
| 成本 | 免費 | 按使用付費 |
| 隱私 | 完全私有 | 數據傳送到 Google |
| 速度 | 取決於硬體 | 通常較快 |
| 模型品質 | 開源模型 | Google 最新模型 |
| 離線使用 | 支援 | 不支援 |
| 硬體需求 | 高 | 無 |

## 生產環境部署

在生產環境中使用 Ollama 時的注意事項：

### 1. Docker 部署

```dockerfile
# 在 docker-compose.yml 中添加 Ollama 服務
services:
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0

volumes:
  ollama-data:
```

### 2. 負載平衡

對於高負載情況，可以運行多個 Ollama 實例：

```python
# 在 settings.py 中配置多個 Ollama 端點
OLLAMA_ENDPOINTS = [
    "http://ollama1:11434",
    "http://ollama2:11434",
    "http://ollama3:11434"
]
```

### 3. 監控和日誌

確保監控 Ollama 服務的健康狀態和效能：

```python
# 健康檢查
def check_ollama_health():
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False
```

這個指南應該幫助您成功整合和使用 Ollama 引擎在您的 Agentic System 中！
