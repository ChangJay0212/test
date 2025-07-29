# 🚀 AI Agent Teaching System

智能 AI 教學系統，基於 Docker + Kafka + Ollama 構建的多智能體教學平台。支持英文和中文教學，並集成工具調用功能（計算器、天氣查詢、網路搜尋）。

## 🏗️ 系統架構

```
學生問題 → Kafka → 動態分配 → AI教師智能體 → 工具調用 → 回應結果
                    ↓
             [英文教師] [中文教師]
                    ↓
            [Ollama LLM + 工具系統]
```

## ⚡ 快速啟動

### 📋 必要條件

- ✅ **Docker** 和 **Docker Compose** 已安裝
- 🐳 **4GB+ RAM** 可用記憶體
- 🦙 **Ollama** 本地 LLM（推薦，免費且隱私）

### 🚀 安裝步驟

1. **啟動系統容器**
   ```bash
   ## use ollama 
   docker-compose -f docker-compose.ollama.yml up -d

   ## use Gemini 
   docker-compose -f docker-compose.yml up -d
   ```

2. **進入應用容器並啟動互動服務**
   ```bash
   docker exec -it agentic-app bash
   python3 interactive_service.py
   ```

3. **開始使用**
   ```
   系統啟動後，可以直接提問：
   - What is the difference between "their", "there", and "they're"?
   - 什麼是成語？請給我幾個例子
   - What's 15 * 24?  (會調用計算器工具)
   - tokyo temp?      (會調用天氣查詢工具)
   ```

## 🔧 工具系統

系統集成了多種實用工具，會根據問題內容自動調用：

### � 計算器工具
```
問題範例: What's 15 * 24?
系統會自動調用計算器並返回結果: 360
```

### 🌤️ 天氣查詢工具
```
問題範例: tokyo temp? 或 What's the weather in London?
系統會自動調用天氣工具並返回當地天氣資訊
```

### � 網路搜尋工具
```
問題範例: Tell me about recent AI developments
系統會自動搜尋最新資訊並整合到回應中
```

## �️ 系統管理

### 啟動系統
```bash
docker-compose -f docker-compose.ollama.yml up -d
```

### 停止系統
```bash
docker-compose -f docker-compose.ollama.yml down
```

### 查看容器狀態
```bash
docker ps
```

### 查看系統日誌
```bash
docker-compose logs -f agentic-app
```

### 進入互動模式
```bash
docker exec -it agentic-app bash
python3 interactive_service.py
```

## 🧪 測試驗證

### 快速健康檢查
```bash
# 檢查所有容器是否正常運行
docker ps

# 檢查 Ollama 是否可用
docker exec ollama ollama list

# 檢查應用日誌
docker logs agentic-app
```

### 測試問題範例
進入互動模式後，可以嘗試以下問題：
```
✅ 英文語法: What's the difference between "who" and "whom"?
✅ 中文教學: 解釋一下「有志者事竟成」的含義
✅ 數學計算: What's 156 * 73?
✅ 天氣查詢: What's the weather in Tokyo?
✅ 資訊搜尋: Tell me about machine learning
```

## 🐛 故障排除

### 常見問題

1. **容器無法啟動**
   ```bash
   # 檢查 Docker 資源
   docker system df
   # 清理後重啟
   docker-compose down
   docker-compose -f docker-compose.ollama.yml up -d
   ```

2. **Ollama 模型未找到**
   ```bash
   # 檢查可用模型
   docker exec ollama ollama list
   # 下載模型
   docker exec ollama ollama pull llama3.1:8b
   ```

3. **智能體無回應**
   ```bash
   # 檢查應用日誌
   docker logs agentic-app | grep "agent processing"
   # 重啟系統
   docker-compose restart agentic-app
   ```

4. **工具調用失敗**
   ```bash
   # 檢查工具相關日誌
   docker logs agentic-app | grep "tool"
   ```

## � 系統架構詳細

### 核心組件
- **Dynamic Assignment**: 智能路由，自動選擇最適合的教師
- **English Teacher Agent**: 專門處理英文教學問題
- **Chinese Teacher Agent**: 專門處理中文教學問題
- **Tool System**: 可擴展的工具框架
- **Kafka**: 可靠的訊息佇列系統
- **Ollama**: 本地 LLM 引擎

### 訊息流程
1. 學生提問 → Interactive Service
2. Dynamic Assignment 智能分配到適當的教師
3. 教師智能體處理問題，必要時調用工具
4. 返回整合工具結果的完整回應

## 📁 重要檔案

- `docker-compose.ollama.yml` - Ollama 部署配置
- `interactive_service.py` - 互動服務主程式
- `agents/` - 智能體實現
- `tools/` - 工具系統
- `llm_engines/` - LLM 引擎
- `config/` - 系統配置

## 💰 成本管理配置

系統支持靈活的 token 成本配置，可以追蹤不同 LLM 服務的使用費用：

### 📋 設置成本參數

1. **複製環境變數模板**
   ```bash
   cp .env.example .env
   ```

2. **編輯成本配置**
   ```bash
   # Gemini 定價 (每 1K tokens 的美元費用)
   GEMINI_INPUT_COST_PER_1K=0.0005
   GEMINI_OUTPUT_COST_PER_1K=0.0015
   
   # Ollama 定價 (本地部署免費)
   OLLAMA_COMPUTE_COST_PER_1K=0.0
   
   # 成本警報閾值 (每日費用超過此金額時警報)
   COST_ALERT_THRESHOLD=10.0
   
   # 啟用/禁用成本追蹤
   COST_TRACKING_ENABLED=true
   ```

### 📊 成本監控功能

- **即時成本追蹤**: 每個請求的 token 使用和費用
- **統計報表**: 小時、日、週的成本分析
- **費用警報**: 超出預設閾值時自動警報
- **多引擎支持**: 支持 Gemini、Ollama、OpenAI、Claude 等

### 💡 成本優化建議

```bash
# 查看成本統計
docker logs agentic-app | grep "cost"

# 使用 Ollama (免費) 降低成本
docker-compose -f docker-compose.ollama.yml up -d

# 設置較低的成本警報閾值
COST_ALERT_THRESHOLD=5.0
```

---

**最後更新**: 2025-07-28  
**系統版本**: AI Agent Teaching System v2.1
