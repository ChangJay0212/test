# 🔧 Windows 命令相容性問題解決方案

## 🚨 發現的問題

您的 Windows 系統缺少一些標準命令：
- `ping` 命令不可用
- `find` 命令不可用
- `findstr` 命令不可用

這通常發生在某些 Windows 配置或受限環境中。

## ✅ 解決方案

我已經創建了多個相容性版本，請按順序嘗試：

### 🥇 選項 1: PowerShell 版本（最推薦）
```powershell
.\start-powershell.ps1
```

**特點**：
- ✅ 純 PowerShell，不依賴外部命令
- ✅ 彩色輸出和進度指示
- ✅ 完整的錯誤處理
- ✅ 所有 Windows 系統都支援

### 🥈 選項 2: 相容批次文件
```cmd
start-compatible.bat
```

**特點**：
- ✅ 使用 `timeout` 或 PowerShell Sleep 作為後備
- ✅ 不依賴 ping/find/findstr
- ✅ 傳統批次文件語法

### 🥉 選項 3: 原始版本（如果修復了環境）
```cmd
start-ultra-simple.bat
```

## 🚀 推薦使用流程

### 步驟 1: 嘗試 PowerShell 版本
```powershell
# 在 PowerShell 中執行
.\start-powershell.ps1
```

### 步驟 2: 如果 PowerShell 有問題，嘗試相容版本
```cmd
# 在命令提示字元中執行
start-compatible.bat
```

### 步驟 3: 檢查狀態
```cmd
# 檢查所有容器狀態
docker ps

# 檢查應用日誌
docker-compose -f docker-compose.ollama.yml logs agentic-app
```

## 🔍 預期的成功輸出

當系統正常啟動時，您應該看到：

```
✅ Setup complete! Checking container status...
NAME          STATUS
zookeeper     Up 2 minutes
kafka         Up 2 minutes (healthy)
ollama        Up 2 minutes (healthy)
agentic-app   Up 30 seconds

🔍 Quick health checks:
🦙 Testing Ollama API...
✅ Ollama: API responding
📚 Available models:
NAME     ID              SIZE    MODIFIED
llama2   78e26419b446    3.8 GB  2 minutes ago

🎉 System startup complete!
```

## 🛠️ 故障排除

### 如果 PowerShell 執行策略有問題
```powershell
# 允許執行 PowerShell 腳本（以管理員身份執行）
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# 或者直接執行內容
Get-Content .\start-powershell.ps1 | PowerShell.exe -noprofile -
```

### 如果仍然有命令問題
```cmd
# 手動步驟（不依賴任何特殊命令）
docker-compose -f docker-compose.ollama.yml down
docker-compose -f docker-compose.ollama.yml up -d zookeeper
REM 等待約 15 秒
docker-compose -f docker-compose.ollama.yml up -d kafka
REM 等待約 45 秒
docker-compose -f docker-compose.ollama.yml up -d ollama
REM 等待約 30 秒
docker exec ollama ollama pull llama2
docker-compose -f docker-compose.ollama.yml up --build -d agentic-app
```

### 檢查系統路徑
```cmd
# 檢查基本命令是否可用
where ping
where find
where findstr

# 如果缺少，可能需要修復 Windows 系統路徑
echo %PATH%
```

## 📋 系統需求確認

確保您有：
- ✅ Docker Desktop 已安裝並運行
- ✅ PowerShell 5.0+ （Windows 10+ 內建）
- ✅ 足夠的磁碟空間（至少 5GB 用於 Docker 鏡像）
- ✅ 足夠的記憶體（建議 8GB+）

## 🎯 快速測試

啟動後，用這些命令驗證系統：

```cmd
# 測試 Kafka
docker exec kafka kafka-broker-api-versions --bootstrap-server localhost:29092

# 測試 Ollama
docker exec ollama curl http://localhost:11434/api/tags
docker exec ollama ollama list

# 查看應用日誌
docker logs agentic-app --tail 20
```

## 🚀 現在就試試！

```powershell
# 首選方法
.\start-powershell.ps1
```

如果遇到任何問題，PowerShell 版本會提供詳細的錯誤信息和解決建議！ 🎉
