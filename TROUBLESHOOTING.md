# 🔧 Docker Ollama 啟動問題修復指南

## 已修復的問題

### ✅ 1. 依賴衝突問題
**問題**: `google-generativeai==0.3.2` 和 `langchain-google-genai==0.0.11` 版本衝突

**解決方案**: 更新 `requirements.txt`
```
google-generativeai>=0.4.1,<0.5.0  # 改為相容版本範圍
```

### ✅ 2. Windows timeout 命令問題
**問題**: `'timeout' 不是內部或外部命令`

**解決方案**: 替換為 `ping` 命令
```bat
ping 127.0.0.1 -n 11 > nul  # 等待 10 秒
```

### ✅ 3. Docker Compose 版本警告
**問題**: `version` 屬性過時

**解決方案**: 移除 `version: '3.8'` 行

## 🚀 現在可以使用的啟動方式

### 選項 1: 清理重建（推薦）
```bat
clean-rebuild.bat
```
這個腳本會：
- 清理舊容器
- 強制重建鏡像
- 重新下載模型
- 提供詳細的錯誤處理

### 選項 2: 正常啟動
```bat
start-ollama.bat
```
現在修復了 timeout 問題和錯誤處理

### 選項 3: 手動步驟
```bat
# 1. 停止舊容器
docker-compose -f docker-compose.ollama.yml down

# 2. 清理鏡像
docker rmi agentic_system-agentic-app

# 3. 重新構建
docker-compose -f docker-compose.ollama.yml up --build -d

# 4. 下載模型
docker exec ollama ollama pull llama2

# 5. 查看日誌
docker-compose -f docker-compose.ollama.yml logs -f agentic-app
```

## 📋 依賴更新詳情

### 新的 requirements.txt
```
kafka-python==2.0.2
langchain==0.1.0
langchain-google-genai==0.0.11
google-generativeai>=0.4.1,<0.5.0  # 修復版本衝突
requests==2.31.0
python-dotenv==1.0.0
pydantic==2.5.0
```

### 版本相容性
- `langchain-google-genai==0.0.11` 需要 `google-generativeai>=0.4.1,<0.5.0`
- 使用版本範圍而不是固定版本，提高相容性

## 🛠️ 故障排除

### 如果構建仍然失敗
```bat
# 清理 Docker 系統
docker system prune -f

# 清理所有未使用的鏡像
docker image prune -a -f

# 重新嘗試
clean-rebuild.bat
```

### 如果 Ollama 模型下載失敗
```bat
# 手動下載其他模型
docker exec ollama ollama pull llama3.1:8b
docker exec ollama ollama pull mistral
docker exec ollama ollama pull codellama

# 列出可用模型
docker exec ollama ollama list
```

### 如果容器無法啟動
```bat
# 檢查容器狀態
docker-compose -f docker-compose.ollama.yml ps

# 查看詳細日誌
docker-compose -f docker-compose.ollama.yml logs

# 查看特定容器日誌
docker logs ollama
docker logs agentic-app
```

## ✅ 驗證安裝

成功啟動後，您應該看到：
1. ✅ Zookeeper 容器運行
2. ✅ Kafka 容器運行  
3. ✅ Ollama 容器運行
4. ✅ Agentic-app 容器運行
5. ✅ Llama2 模型已下載

## 🎯 下一步

啟動成功後：
1. 系統會顯示應用程式日誌
2. 可以開始測試 Ollama 引擎
3. 使用 `python demo_engines.py` 測試功能

現在修復了所有已知問題，應該可以正常啟動了！ 🎉
