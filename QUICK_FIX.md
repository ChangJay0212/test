# 🚨 Kafka 連接和 LLM 引擎問題解決

## 🔍 已識別的問題

### 問題 1: Kafka 連接被拒絕
```
ERROR - Connect attempt to <BrokerConnection> returned error 111. Disconnecting.
```

### 問題 2: LLM 引擎創建失敗
```
Exception: No available LLM engines could be created
```

## ✅ 解決方案

### 🎯 推薦解決方式（按順序嘗試）

#### 方法 1: 使用簡單啟動腳本（最推薦）
```bat
start-ollama-simple.bat
```
這個腳本：
- 按正確順序啟動服務
- 給每個步驟足夠的等待時間
- 提供詳細的狀態檢查

#### 方法 2: 使用健康檢查版本
```bat
start-ollama.bat
```
現在包含：
- Docker 健康檢查
- 服務依賴等待
- 更好的錯誤處理

#### 方法 3: 完全重建
```bat
clean-rebuild.bat
```

### 🔧 手動步驟（如果腳本失敗）

```bat
# 1. 完全清理
docker-compose -f docker-compose.ollama.yml down
docker system prune -f

# 2. 按順序啟動基礎設施
docker-compose -f docker-compose.ollama.yml up -d zookeeper
timeout /t 10

docker-compose -f docker-compose.ollama.yml up -d kafka  
timeout /t 20

docker-compose -f docker-compose.ollama.yml up -d ollama
timeout /t 15

# 3. 下載模型
docker exec ollama ollama pull llama2

# 4. 啟動應用
docker-compose -f docker-compose.ollama.yml up --build -d agentic-app

# 5. 查看日誌
docker-compose -f docker-compose.ollama.yml logs -f agentic-app
```

## 📊 檢查服務狀態

```bat
# 檢查所有容器狀態
docker-compose -f docker-compose.ollama.yml ps

# 檢查健康狀態
docker-compose -f docker-compose.ollama.yml ps --filter "status=running"

# 檢查特定服務日誌
docker-compose -f docker-compose.ollama.yml logs kafka
docker-compose -f docker-compose.ollama.yml logs ollama
docker-compose -f docker-compose.ollama.yml logs agentic-app
```

## 🔍 故障診斷

### Kafka 問題診斷
```bat
# 檢查 Kafka 是否響應
docker exec kafka kafka-broker-api-versions --bootstrap-server localhost:29092

# 檢查主題
docker exec kafka kafka-topics --bootstrap-server localhost:29092 --list
```

### Ollama 問題診斷  
```bat
# 檢查 Ollama API
docker exec ollama curl -f http://localhost:11434/api/tags

# 檢查已下載的模型
docker exec ollama ollama list

# 手動下載模型
docker exec ollama ollama pull llama2
```

### 應用程式問題診斷
```bat
# 檢查環境變數
docker exec agentic-app env | findstr -i llm
docker exec agentic-app env | findstr -i ollama

# 測試連接
docker exec agentic-app ping kafka
docker exec agentic-app ping ollama
```

## 🎯 重要改進

### Docker Compose 更新
- ✅ 添加健康檢查
- ✅ 服務依賴等待
- ✅ 重啟策略
- ✅ 環境變數默認值

### 啟動腳本改進
- ✅ 分步驟啟動
- ✅ 狀態檢查
- ✅ 更好的錯誤處理
- ✅ 詳細的進度報告

## 🚀 現在嘗試

選擇最適合的方式：

```bat
# 最簡單可靠的方式
start-ollama-simple.bat

# 如果上面失敗，試試這個
clean-rebuild.bat

# 或者手動步驟（見上面的手動步驟）
```

現在的配置應該能解決 Kafka 連接和 LLM 引擎的問題！ 🎉

## 📝 預期的成功輸出

當一切正常工作時，您應該看到：
```
✅ All services started! Checking status...
   NAME          IMAGE                           STATUS
   zookeeper     confluentinc/cp-zookeeper:7.4.0 Up (healthy)
   kafka         confluentinc/cp-kafka:7.4.0      Up (healthy)  
   ollama        ollama/ollama:latest             Up (healthy)
   agentic-app   agentic_system-agentic-app       Up

🚀 Starting to show application logs...
agentic-app  | 2025-07-27 14:15:00 - agentic_system - INFO - System initialized successfully
agentic-app  | 2025-07-27 14:15:00 - agentic_system - INFO - Ollama engine ready
agentic-app  | 2025-07-27 14:15:00 - agentic_system - INFO - Kafka connected successfully
```
