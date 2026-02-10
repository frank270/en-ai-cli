# En-Ai-Cli 開發文檔

## 開發環境

### 系統要求

- **作業系統**: macOS (Apple Silicon M1/M2), Linux, Windows
- **Python 版本**: 3.9.13+ (建議使用 3.9.16)
- **環境管理**: Conda (推薦) 或 venv
- **套件管理**: pip 或 Poetry

### 推薦開發環境

```bash
# Python 環境
Python: 3.9.16
Conda 環境名稱: py39
平台: macOS (Apple M1)

# 核心依賴
click: ^8.1.7
httpx: ^0.27.0
pydantic: ^2.5.0
rich: ^13.7.0
requests: ^2.32.0

# 開發依賴
pytest: ^8.0.0
pytest-cov: ^7.0.0
black: ^24.0.0
```

### 環境設定

```bash
# 1. 建立 Conda 環境（推薦）
conda create -n py39 python=3.9.16
conda activate py39

# 2. 安裝專案（開發模式）
pip install -e .

# 3. 安裝開發依賴
pip install -r requirements-dev.txt

# 4. 驗證安裝
en-ai --version
pytest tests/ -v
```

### 測試環境

- **測試框架**: pytest 8.0+
- **覆蓋率工具**: pytest-cov
- **Mock 工具**: unittest.mock
- **執行環境**: py39 Conda 環境（非 base 環境）

**重要**: 所有測試都應在 `py39` 環境中執行，避免污染 base 環境：
```bash
conda activate py39
pytest tests/ -v
```

---

## 當前版本狀態

**版本**: v0.4.0  
**最後更新**: 2026-02-10  
**測試狀態**: ✅ 40/40 通過（含角色系統與安全防護測試）  
**開發階段**: Phase 3.5 - Phase 8 完成

### 已完成功能
- ✅ 雙層配置管理（workspace/global）
- ✅ 跨平台指令執行與轉換
- ✅ LLM Provider 抽象架構 (Ollama/OpenRouter)
- ✅ 角色（Persona/Role）系統：支持自定義 System Prompt 與角色切換
- ✅ 指令安全防護系統：分級警告 (Safe/Dangerous/Critical) 與 `..` 路徑分析
- ✅ 終端目錄追蹤：攔截 `cd` 與環境變數轉換工具
- ✅ Session 管理與上下文自動封存
- ✅ 對話歷程記錄（JSONL + Markdown）

### 待測試功能
- 🔬 實際 LLM Provider 連線壓力測試
- 🔬 複雜路徑安全性邊界測試
- 🔬 斜線指令 (Slash Commands) 整合驗證

---

## 快速開始

### 開發環境準備

```bash
# 1. 建立並啟用 Conda 環境
conda create -n py39 python=3.9.16
conda activate py39

# 2. 安裝專案（開發模式）
cd /path/to/en-ai-cli
pip install -e .

# 3. 安裝開發工具
pip install -r requirements-dev.txt

# 4. 驗證安裝
en-ai --version
en-ai --help
```

### 執行測試

```bash
# 確保在正確環境中
conda activate py39

# 執行所有測試
pytest tests/ -v

# 執行特定測試
pytest tests/test_ollama.py -v

# 檢查測試覆蓋率
pytest tests/ --cov=en_ai_cli --cov-report=html
```

### 開發模式運行

```bash
# 啟用開發環境
conda activate py39

# 初始化配置
en-ai init

# 測試 Provider
en-ai provider list
en-ai provider status ollama

# 測試模型列表
en-ai models list

# 開始對話
en-ai chat
```

# 使用 Python 模組
poetry run python -m en_ai_cli --help
```

### 測試

```bash
# 使用 Conda + pytest
conda activate py39
pytest

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
│   ├── cli.py               # CLI 命令入口 ✅
│   ├── core/                # 核心功能
│   │   ├── config.py        # ✅ 雙層配置管理
│   │   ├── platform.py      # ✅ 平台偵測與指令轉換
│   │   ├── executor.py      # ✅ 指令安全執行
│   │   └── session.py       # ✅ Session 管理與封存
│   ├── services/            # 服務層
│   │   ├── openrouter.py    # ✅ OpenRouter API 客戶端
│   │   └── history.py       # ✅ 對話歷程（JSONL/Markdown）
│   └── ui/                  # 使用者介面
│       ├── terminal.py      # ✅ Rich 終端介面
│       └── prompts.py       # ✅ 互動提示與警告
├── tests/                   # 測試（38 個測試全部通過）
│   ├── test_config.py       # ConfigManager 測試
│   ├── test_platform.py     # PlatformDetector 測試
│   ├── test_executor.py     # CommandExecutor 測試
│   ├── test_session.py      # SessionManager 測試
│   ├── test_history.py      # HistoryLogger 測試
│   └── test_openrouter.py   # OpenRouterClient 測試
├── docs/                    # 文檔
│   └── DEVELOPMENT.md       # 開發文檔（本文件）
├── .github/
│   └── copilot-instructions.md  # AI 開發指引
├── requirements.txt         # 核心依賴
├── requirements-dev.txt     # 開發依賴
├── setup.py                 # Pip 安裝支援
├── pyproject.toml           # Poetry 配置
└── README.md                # 專案說明
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

### Session 管理
```bash
en-ai session list                      # 列出所有 sessions
en-ai session new                       # 建立新 session
en-ai session switch <session_id>       # 切換 session
en-ai session stats [session_id]        # 顯示統計資訊
en-ai session export [output]           # 匯出為 Markdown
en-ai session archive --auto-new        # 封存當前 session
```

### Chat 對話
```bash
en-ai chat             # 開始 AI 對話（需要 API Key）
# 對話中可用命令：
# - stats: 查看 session 統計
# - exit/quit: 離開對話
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

### Phase 3: Session 管理與封存 ✅ (已完成 - v0.3.0)
- [x] SessionManager 核心方法
- [x] Session 命令群組
- [x] Chat 命令上下文管理整合
- [x] 封存系統
- [x] 測試完整性

### Phase 3.5: Ollama 整合與 Provider 管理 ✅ (已完成 - v0.3.5)
- [x] LLM Provider 抽象基類
- [x] OllamaProvider 實作
- [x] ProviderManager 自動偵測與切換
- [x] Provider CLI (list/status/switch)

### Phase 4: 角色 (Persona) 系統實體化 ✅ (已完成 - v0.3.6)
- [x] 實體化 `config.json` 中的角色設定
- [x] `en-ai role` 指令群組 (list/set/add)
- [x] Chat 模式角色注入與切換

### Phase 5: 指令執行強化與安全防護 ✅ (已完成 - v0.4.0)
- [x] 終端目錄追蹤 (`cd` 攔截)
- [x] 路徑安全分析 (防止 `..` 刪除父目錄)
- [x] 分級警告 UI (Cyan/Yellow/Red)
- [x] 高風險指令 `YES` 強制確認機制

### Phase 6: 斜線指令 (Slash Commands) 🚧 (進行中)
- [ ] 攔截 `/help`, `/role`, `/stats`, `/clear`
- [ ] 精美的表格 UI 顯示輔助資訊
- [ ] 不離開對話切換角色功能

### Phase 7: 優化與擴展 🔮 (規劃中)
- [ ] 效能優化
- [ ] 錯誤處理強化
- [ ] 多語言支援（如需要）
- [ ] 插件系統（可選）

## 常見問題

### 如何進行實際 API 測試？

1. **準備 API Key**
   ```bash
   # 取得 OpenRouter API Key (https://openrouter.ai/)
   export OPENROUTER_API_KEY="sk-or-v1-xxx"
   ```

2. **初始化配置**
   ```bash
   conda activate py39
   en-ai init
   # 輸入 API Key 並選擇模型策略
   ```

3. **測試基本對話**
   ```bash
   en-ai chat
   # 輸入簡單問題測試 AI 回應
   ```

4. **測試上下文管理**
   - 發送多則訊息達到 80% 閾值（40/50）
   - 驗證警告提示
   - 測試封存功能

5. **測試指令執行**
   - 詢問需要執行系統指令的問題
   - 確認指令提示顯示正確
   - 驗證執行結果記錄

### 如何測試需要 API Key 的功能？

**單元測試**：使用 pytest 的 mock 功能：
```python
@pytest.fixture
def mock_openrouter(monkeypatch):
    # Mock API 呼叫
    pass
```

**整合測試**：使用真實 API Key 但限制呼叫次數：
- 使用 free 模型降低成本
- 設置測試專用 session
- 測試後清理資料

### 如何除錯 chat 命令問題？

1. **啟用詳細日誌**
   ```python
   # 在 cli.py 添加 logging
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **檢查 session 狀態**
   ```bash
   en-ai session stats
   en-ai session list
   ```

3. **查看歷史記錄**
   ```bash
   # 檢查 JSONL 檔案
   cat ~/.en-ai/sessions/<session_id>.jsonl
   
   # 匯出為 Markdown 檢視
   en-ai session export output.md
   ```

### 下次對話開始前的準備工作

**新對話 Checklist**：
- [ ] 準備 OpenRouter API Key
- [ ] 執行 `en-ai init` 設定測試環境
- [ ] 確認所有測試通過：`pytest tests/ -v`
- [ ] 檢查當前版本：`git tag -l`
- [ ] 準備測試問題清單（簡單→複雜）

**測試問題範例**：
1. 簡單問答："Python 如何讀取文件？"
2. 指令建議："如何查看當前目錄下所有 Python 文件？"
3. 多輪對話：連續提問測試上下文
4. 邊界測試：發送大量訊息觸發封存

### 如何新增支援的平台？

在 `core/platform.py` 的 `PlatformType` enum 新增類型，並更新 `detect()` 方法。
