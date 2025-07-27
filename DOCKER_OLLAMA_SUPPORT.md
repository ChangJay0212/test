# 🚀 Docker Compose 和啟動腳本的 Ollama 支援

## ✅ 現在完全支援 Ollama！

我已經更新了所有的 Docker Compose 配置和啟動腳本來支援 Ollama。

## 📋 可用的啟動選項

### 1. 標準啟動（推薦）
```bash
start.bat          # Windows
./start.sh          # Linux/macOS
.\start.ps1         # PowerShell
```

**特點：**
- 自動偵測 `.env` 中的引擎配置
- 支援本地安裝的 Ollama
- 支援 Gemini 雲端 API
- 智能檢查和驗證

### 2. Ollama 容器化啟動
```bash
start-ollama.bat    # Windows (新增)
```

**特點：**
- 在 Docker 容器中運行 Ollama
- 自動下載和設定模型
- 不需要本地安裝 Ollama
- 完全容器化的解決方案

## 🔧 Docker Compose 更新

### 主要的 docker-compose.yml
```yaml
agentic-app:
  environment:
    - GEMINI_API_KEY=${GEMINI_API_KEY}
    - DEFAULT_LLM_ENGINE=${DEFAULT_LLM_ENGINE:-gemini}
    - OLLAMA_BASE_URL=${OLLAMA_BASE_URL:-http://host.docker.internal:11434}
    - OLLAMA_MODEL=${OLLAMA_MODEL:-llama2}
    - OLLAMA_TIMEOUT=${OLLAMA_TIMEOUT:-60}
  extra_hosts:
    - "host.docker.internal:host-gateway"  # 允許訪問主機上的 Ollama
```

### Ollama 專用的 docker-compose.ollama.yml
```yaml
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
      
  agentic-app:
    depends_on:
      - ollama
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434  # 容器內部連接
```

## 🎯 使用場景

### 場景 1：本地 Ollama + Docker 應用
```bash
# 1. 安裝 Ollama 到您的系統
# 2. 配置 .env
DEFAULT_LLM_ENGINE=ollama
OLLAMA_BASE_URL=http://localhost:11434

# 3. 啟動
start.bat
```

### 場景 2：完全容器化
```bash
# 1. 配置 .env（或使用預設值）
DEFAULT_LLM_ENGINE=ollama

# 2. 啟動（包含 Ollama 容器）
start-ollama.bat
```

### 場景 3：Gemini 雲端
```bash
# 1. 配置 .env
DEFAULT_LLM_ENGINE=gemini
GEMINI_API_KEY=your_api_key_here

# 2. 啟動
start.bat
```

## 🔍 啟動腳本功能

### start.bat 新功能
- ✅ 自動偵測引擎類型
- ✅ 檢查 Ollama 伺服器狀態
- ✅ 驗證 Gemini API 金鑰
- ✅ 智能錯誤提示
- ✅ 彩色輸出和圖示

### start-ollama.bat 功能
- ✅ 完全容器化部署
- ✅ 自動模型下載
- ✅ 等待服務就緒
- ✅ 容器日誌顯示

## 🛠️ 環境變數支援

所有這些環境變數現在都會自動傳遞到 Docker 容器：

```env
DEFAULT_LLM_ENGINE=ollama|gemini
GEMINI_API_KEY=your_key
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OLLAMA_TIMEOUT=60
```

## 🎉 主要改進

1. **網路配置**：添加了 `host.docker.internal` 支援，讓容器可以訪問主機上的 Ollama
2. **環境變數**：完整傳遞所有 LLM 引擎配置
3. **智能檢查**：啟動前驗證引擎可用性
4. **多種部署方式**：支援本地和容器化 Ollama
5. **向後相容**：保持對現有 Gemini 配置的完整支援

## 🚀 快速開始

選擇最適合您的方式：

```bash
# 如果您想要本地 Ollama（更快，更靈活）
.\setup-ollama.ps1
start.bat

# 如果您想要完全容器化（更簡單，無需安裝）
start-ollama.bat

# 如果您想要使用 Gemini
# 編輯 .env 設定 GEMINI_API_KEY
start.bat
```

## 🧪 啟動後如何測試

### 快速測試
```bash
# 執行自動化測試
quick-test.bat          # Windows
./quick-test.sh         # Linux/macOS
```

### 互動式測試
```bash
# 親自體驗系統功能
interactive-test.bat    # Windows
```

### 詳細測試指南
查看 `TESTING_GUIDE.md` 獲得完整的測試步驟和故障排除指南。

現在您的系統完全支援 Ollama 了！ 🎉
