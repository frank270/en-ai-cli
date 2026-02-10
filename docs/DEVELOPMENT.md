# En-Ai-Cli 開發文檔

## 快速開始

### 安裝依賴

```bash
# 使用 Poetry 安裝依賴
poetry install
```

### 開發模式運行

```bash
# 方式 1: 使用 Poetry
poetry run en-ai --help

# 方式 2: 使用 Python 模組
poetry run python -m en_ai_cli --help
```

### 測試

```bash
# 執行所有測試
poetry run pytest

# 執行測試並顯示覆蓋率
poetry run pytest --cov=en_ai_cli --cov-report=html

# 執行特定測試檔案
poetry run pytest tests/test_config.py -v
```

### 程式碼格式化

```bash
# 使用 Black 格式化程式碼
poetry run black src/

# 使用 Ruff 檢查程式碼
poetry run ruff check src/
```

## 專案結構

```
en-ai-cli/
├── src/en_ai_cli/           # 主程式碼
│   ├── __init__.py
│   ├── __main__.py          # 支援 python -m 執行
│   ├── cli.py               # CLI 命令入口
│   ├── core/                # 核心功能
│   │   ├── config.py        # 雙層配置管理
│   │   ├── platform.py      # 平台偵測
│   │   ├── executor.py      # 指令執行（待實作）
│   │   └── session.py       # Session 管理（待實作）
│   ├── services/            # 服務層
│   │   ├── openrouter.py    # OpenRouter API 客戶端
│   │   └── history.py       # 對話歷程（待實作）
│   └── ui/                  # 使用者介面
│       ├── terminal.py      # Rich 終端介面
│       └── prompts.py       # 互動提示（待實作）
├── tests/                   # 測試
├── docs/                    # 文檔（自動生成）
├── pyproject.toml           # Poetry 配置
└── README.md
```

## 核心模組說明

### ConfigManager (core/config.py)
雙層配置系統，支援 workspace 和 global 層級：
- Workspace: `./.en-ai/config.json`
- Global: `~/.en-ai/config.json`
- Workspace 配置優先，fallback 到 global

### PlatformDetector (core/platform.py)
跨平台環境偵測與指令轉換：
- 自動偵測平台（Unix/PowerShell/CMD）
- 指令格式轉換（如 `ls` ↔ `dir`）
- Shell 類型識別

### OpenRouterClient (services/openrouter.py)
OpenRouter API 整合：
- Free 模型優先選擇
- 模型列表快取（1 小時 TTL）
- Chat API 呼叫

## CLI 命令

### 初始化
```bash
en-ai init              # 初始化 workspace 配置
en-ai init --global     # 初始化全域配置
```

### 配置管理
```bash
en-ai config set <key> <value>         # 設定配置
en-ai config set <key> <value> --global # 設定全域配置
en-ai config get <key>                 # 取得配置
en-ai config list                      # 列出所有配置
```

### 模型管理
```bash
en-ai models list       # 列出所有模型
en-ai models list --free # 僅列出 free 模型
```

### 系統資訊
```bash
en-ai info             # 顯示系統資訊
```

## 開發指南

### 新增功能模組

1. 在對應目錄建立 Python 檔案
2. 實作功能類別/函式
3. 在 `tests/` 建立對應測試
4. 更新 CLI 命令（如需要）

### 配置檔案格式

**Global Config** (`~/.en-ai/config.json`):
```json
{
  "openrouter_api_key": "sk-xxx",
  "default_model": "meta-llama/llama-3.2-3b-instruct:free",
  "prefer_free_models": true,
  "fallback_to_paid": false,
  "color_mode": true,
  "auto_save_history": true,
  "max_context_messages": 50,
  "model_cache_ttl": 3600
}
```

## 下一步開發

### Phase 1: 基礎架構 ✅ (已完成)
- [x] 專案結構與 Poetry 配置
- [x] 雙層配置系統 (ConfigManager)
- [x] 平台偵測模組 (PlatformDetector)
- [x] OpenRouter API 客戶端 (Free 模型優先)
- [x] 基本 CLI 命令 (init, config, models, info)
- [x] Rich 終端介面工具

### Phase 2: 核心對話功能 ✅ (已完成)
- [x] 指令執行引擎 (`core/executor.py`)
- [x] Session 管理器 (`core/session.py`)
  - Session ID 生成與追蹤
  - 訊息計數與上限檢查  
  - 上下文警告機制
- [x] 對話歷程記錄 (`services/history.py`)
  - JSONL 格式存儲
  - Markdown 匯出功能
- [x] 基本對話流程 (`cli.py` - `chat` 命令)
  - AI 對話循環
  - 指令建議與確認
  - 執行結果回饋
- [x] 指令確認提示 (`ui/prompts.py`)
- [x] 測試覆蓋
  - test_session.py
  - test_history.py
  - test_executor.py

### Phase 3: Session 管理與封存 📅 (待開發)
- [ ] Session 命令群組
  - session list/new/switch
  - session export/archive
  - session stats
- [ ] 自動封存功能
- [ ] 封存檔案管理
- [ ] 歷程查詢與搜尋

### Phase 4: 優化與擴展 🔮
- [ ] 效能優化
- [ ] 錯誤處理強化
- [ ] 多語言支援（如需要）
- [ ] 插件系統（可選）

## 常見問題

### 如何測試需要 API Key 的功能？

使用 pytest 的 mock 功能：
```python
@pytest.fixture
def mock_openrouter(monkeypatch):
    # Mock API 呼叫
    pass
```

### 如何新增支援的平台？

在 `core/platform.py` 的 `PlatformType` enum 新增類型，並更新 `detect()` 方法。
