# 🔧 Windows 編碼問題解決方案

## ❌ 問題描述
如果您看到類似這樣的亂碼：
```
隢??皜祈岫???踝?
'?敹恍摨瑟炎??' 不是內部或外部命令、可執行的程式或批次檔。
```

## ✅ 解決方案

### 方案1: 使用推薦的聊天工具（最簡單）
```bash
.\chat.bat
```
這個文件完全沒有編碼問題，可以直接使用。

### 方案2: 使用修復版本
```bash
.\interactive-test-fixed.bat
.\simple-chat.bat
.\interactive-simple.bat
```

### 方案3: 手動修復編碼（如果其他方案不行）
```bash
# 1. 設置控制台編碼
chcp 65001

# 2. 然後運行腳本
.\interactive-test.bat
```

## 🎯 推薦使用順序

1. **首選**: `.\chat.bat` - 最可靠，無編碼問題
2. **次選**: `.\interactive-test-fixed.bat` - 功能完整
3. **備選**: `.\simple-chat.bat` - 極簡界面

## 🧪 測試步驟

1. 啟動系統：
   ```bash
   .\start-ollama.bat
   ```

2. 檢查健康狀態：
   ```bash
   .\quick-test.bat
   ```

3. 開始聊天：
   ```bash
   .\chat.bat
   ```

4. 測試問題：
   ```
   Your question: What is the difference between their, there, and they're?
   Your question: What are Chinese idioms?
   Your question: How can I improve my writing?
   ```

## 📞 如果還有問題

如果所有方案都不行，請檢查：
1. Docker 是否正在運行：`docker ps`
2. 所有容器是否健康：`.\quick-test.bat`
3. 控制台是否支持 UTF-8：`chcp 65001`

---
*最後更新：2025-07-27*
