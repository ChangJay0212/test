# 🏗️ 新架構說明文件

## 📋 重構後的模組結構

```
/mnt/other/test/
├── agents/          # Agent 管理模組
│   ├── __init__.py
│   ├── base_agent.py
│   ├── chinese_teacher.py
│   ├── english_teacher.py
│   └── registry.py         # 從 core/registry.py 移動而來
├── messaging/       # 消息系統模組
│   ├── __init__.py
│   └── kafka_client.py     # 從 core/kafka_client.py 移動而來
├── monitoring/      # 監控系統模組
│   ├── __init__.py
│   ├── health_check.py     # 從 core/health_check.py 移動而來
│   ├── cost_manager.py     # 從 core/cost_manager.py 移動而來
│   └── cost_monitor.py     # 從 core/cost_monitor.py 移動而來
├── routing/         # 路由分配模組 (已移除)
│   ├── __init__.py
│   └── dynamic_assign.py   # → 移動到 producer/utils/
├── utils/           # 通用工具模組
│   ├── __init__.py
│   └── logger.py           # 從 core/logger.py 移動而來
├── config/          # 配置模組 (unchanged)
├── consumer/        # 消費者模組 (unchanged)
├── producer/        # 生產者模組
│   ├── __init__.py
│   ├── producer.py
│   └── utils/           # Producer 專用工具
│       ├── __init__.py
│       └── dynamic_assign.py  # 智能路由分配 (從 routing/ 移動)
├── llm_engines/     # LLM 引擎模組 (unchanged)
├── tools/           # 工具模組 (unchanged)
└── scripts/         # 腳本模組 (unchanged)
```

## 🎯 重構的好處

### 1. **功能模組化**
- ❌ 舊: 所有核心功能混在 `core/` 中
- ✅ 新: 按功能分組，職責清晰

### 2. **更好的層級結構**
- ❌ 舊: `core` 概念模糊，包含各種不相關功能
- ✅ 新: 每個模組有明確的功能範疇

### 3. **易於擴展**
- ✅ 要添加新的 agent 功能 → 在 `agents/` 模組中添加
- ✅ 要添加新的監控功能 → 在 `monitoring/` 模組中添加
- ✅ 要添加新的路由策略 → 在 `routing/` 模組中添加

### 4. **更好的依賴管理**
- ✅ `utils/` 是真正的通用工具，被其他模組依賴
- ✅ 每個功能模組是獨立的，可以單獨測試和部署

## 📦 模組職責說明

### `agents/` - Agent 管理
- 管理所有 AI 教師 agent
- agent 註冊和發現
- agent 元數據管理

### `messaging/` - 消息系統  
- Kafka 客戶端封裝
- 消息的發送和接收
- Topic 管理

### `monitoring/` - 監控系統
- 系統健康檢查
- 成本監控和統計
- 性能指標收集

### `routing/` - 路由分配
- 動態 agent 分配邏輯
- 智能路由策略
- 負載均衡

### `utils/` - 通用工具
- 日誌系統
- 共享的工具函數
- 全局配置工具

## 🔧 如何添加新功能

### 添加新的 Agent
1. 在 `agents/` 中創建新的 agent 類
2. 在 `agents/registry.py` 中註冊
3. 無需修改其他模組

### 添加新的監控功能
1. 在 `monitoring/` 中創建新的監控器
2. 在 `monitoring/__init__.py` 中導出
3. 在需要的地方導入使用

### 添加新的路由策略
1. 在 `routing/` 中實現新策略
2. 通過配置選擇不同策略
3. 支持插件化擴展

## 🚀 未來擴展方向

- **plugins/** - 插件系統
- **security/** - 安全模組
- **analytics/** - 分析模組
- **deployment/** - 部署工具

這個新架構讓系統更加模組化、可維護和可擴展！
