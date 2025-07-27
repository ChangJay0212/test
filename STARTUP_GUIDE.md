# 🚀 Agentic Teaching System - 啟動指南

## 📋 可用的啟動腳本

### 🎯 主要啟動腳本

#### 1. **start-ollama.bat** （推薦）
```bash
start-ollama.bat
```
- 🦙 使用 Ollama 本地 LLM 引擎
- 📦 完全容器化（包含 Ollama）
- 🔄 自動下載模型
- 💰 完全免費

#### 2. **start.bat**
```bash
start.bat
```
- 🌐 使用 Gemini 雲端 API
- 🔑 需要設定 GEMINI_API_KEY
- ⚡ 回應速度快
- 💳 按使用量付費

### 🧪 測試腳本

#### 3. **quick-test.bat**
```bash
quick-test.bat
```
- ✅ 快速健康檢查
- 🔍 檢查所有服務狀態
- 📊 顯示系統概況

#### 4. **interactive-test.bat**
```bash
interactive-test.bat
```
- 🎮 互動式功能測試
- 💬 對話測試
- 🔢 數學問題求解
- 📚 語言學習輔助
- 🤖 代理協作演示

## 🚀 快速開始

### 首次使用（推薦）
```bash
# 1. 啟動系統
start-ollama.bat

# 2. 等待啟動完成後進行測試
interactive-test.bat
```

### 使用 Gemini
```bash
# 1. 編輯 .env 文件，添加您的 API 金鑰
# GEMINI_API_KEY=your_api_key_here

# 2. 啟動系統
start.bat

# 3. 測試
quick-test.bat
```

## 🔧 故障排除

如果遇到問題：
1. 📖 查看 `trouble.txt` - 詳細的故障排除指南
2. 📋 執行 `quick-test.bat` - 診斷系統狀態  
3. 📝 查看 `TESTING_GUIDE.md` - 完整測試說明
4. 🐳 檢查 Docker 容器：`docker ps`
5. 📄 查看日誌：`docker logs agentic-app`

## 📚 文檔參考

- `DOCKER_OLLAMA_SUPPORT.md` - Ollama 支援說明
- `TESTING_GUIDE.md` - 詳細測試指南
- `trouble.txt` - 故障排除記錄
- `WINDOWS_COMPATIBILITY.md` - Windows 相容性指南

## 🎉 享受您的 AI 教學助手！
