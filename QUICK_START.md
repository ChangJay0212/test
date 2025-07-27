# 🎯 系統使用快速指南

## 🚀 立即開始使用

### 1. 啟動系統
```bash
# Windows - 推薦使用 Ollama (本地 AI，免費)
.\start-ollama.bat

# 等待所有容器啟動完成 (約 1-2 分鐘)
```

### 2. 驗證系統健康
```bash
# 執行健康檢查
.\quick-test.bat

# 確認看到所有 ✅ 標記
```

### 3. 開始對話測試
```bash
# 互動式測試
.\interactive-simple.bat

# 或使用完整版本
.\interactive-test.bat
```

## 💬 測試問題範例

### 英語教學：
```
Your question: What is the difference between "their", "there", and "they're"?
Your question: How can I improve my writing skills?
Your question: english: Explain the use of passive voice
```

### 中文教學：
```
Your question: 什麼是成語？請給我幾個例子。
Your question: 解釋一下李白的《靜夜思》
Your question: chinese: 中國古典詩詞的特點是什麼？
```

### 自動分配（系統會自動選擇合適的老師）：
```
Your question: What are some common English grammar mistakes?
Your question: 中國古代文學有哪些特色？
Your question: Can you help me with pronunciation?
```

## 🔧 常用命令

### 系統管理：
```bash
# 檢查容器狀態
docker ps

# 查看系統日誌
docker logs agentic-app -f

# 停止系統
docker-compose -f docker-compose.ollama.yml down

# 重新啟動
.\start-ollama.bat
```

### 故障排除：
```bash
# 快速健康檢查
.\quick-test.bat

# 檢查 Ollama 模型
docker exec ollama ollama list

# 查看詳細日誌
docker logs agentic-app --tail 50
```

## ✅ 成功指標

系統正常運行時，你應該看到：

1. **容器狀態**：
   ```
   agentic-app    Up X minutes
   ollama         Up X minutes (healthy)  
   kafka          Up X minutes (healthy)
   zookeeper      Up X minutes
   ```

2. **健康檢查結果**：
   ```
   ✅ Engine created: OllamaEngine with model: llama2
   ✅ LLM engine connectivity test passed  
   ✅ English teacher responding
   ✅ Chinese teacher responding
   ✅ Kafka is working
   ```

3. **AI 回應範例**：
   ```
   Your question: Hello, how are you?
   📤 Sending: Hello, how are you?
   ✅ Question sent to AI teacher!
   ```

## 🆘 需要幫助？

如果遇到問題：
1. 查看 `trouble.txt` 詳細故障排除指南
2. 執行 `.\quick-test.bat` 診斷問題
3. 查看 `README.md` 完整文檔
4. 檢查 Docker 容器狀態：`docker ps`

---

## 🎉 享受你的 AI 教學系統！

現在你有一個完全本地運行的 AI 教學系統，支援：
- 🦙 本地 Ollama AI（免費、私密）
- 🤖 智能問題路由
- 📚 中英雙語教學
- 💬 實時對話互動

開始提問吧！ 🚀
