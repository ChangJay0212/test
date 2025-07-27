# 🦙 使用 Ollama 的快速指南

## 重要提醒

**如果您選擇使用 Ollama，`.env` 文件中的 Gemini 設定可以保持不動！**

系統會根據 `DEFAULT_LLM_ENGINE` 設定來選擇引擎，不會同時使用兩個引擎。

## 快速設定方法

### 選項 1：自動配置（推薦）
```powershell
# 執行自動設定腳本
.\setup-ollama.ps1
```

### 選項 2：手動配置
編輯 `.env` 文件：
```env
# 只需要改這一行
DEFAULT_LLM_ENGINE=ollama

# 這些可以保持不動
GEMINI_API_KEY=your_gemini_api_key_here  # 保留即可，不會被使用
GEMINI_MODEL=gemini-pro

# Ollama 設定（通常預設值就可以）
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

## 設定說明

| 設定項目 | Ollama 模式 | Gemini 模式 |
|---------|-------------|-------------|
| `DEFAULT_LLM_ENGINE` | `ollama` | `gemini` |
| `GEMINI_API_KEY` | 可以留空或保持原值 | 必須填入有效的 API 金鑰 |
| `OLLAMA_BASE_URL` | 必須正確 | 會被忽略 |
| `OLLAMA_MODEL` | 必須是已下載的模型 | 會被忽略 |

## 引擎切換

您可以隨時在兩個引擎之間切換：

```env
# 使用 Ollama
DEFAULT_LLM_ENGINE=ollama

# 切換到 Gemini
DEFAULT_LLM_ENGINE=gemini
```

系統會自動偵測並使用相應的引擎。

## 常見問題

### Q: 我可以同時保留兩個引擎的設定嗎？
**A: 可以！** 系統只會使用 `DEFAULT_LLM_ENGINE` 指定的引擎。

### Q: 如果 Ollama 沒有運行會怎樣？
**A:** 系統會自動嘗試後備引擎（如果 Gemini 有效的話）。

### Q: 我需要重新啟動系統來切換引擎嗎？
**A:** 是的，修改 `.env` 後需要重新啟動容器。

## 檢查當前設定

運行以下腳本查看當前配置：
```powershell
python demo_engines.py
```

這會顯示所有可用的引擎和當前的配置狀態。

## 開始使用

配置完成後：
```powershell
.\start.ps1
```

系統會自動檢測您的配置並使用相應的引擎！
