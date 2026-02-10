# Copilot Instructions for en-ai-cli

## Language & Communication

- **CRITICAL**: All responses, documentation, and explanations must be in **Traditional Chinese (繁體中文)**, even when reading English source files
- User environment: macOS (Apple M1)
- Be direct and focused - address the core question without unnecessary context

## Development Workflow

### Pre-Implementation Requirements

**MANDATORY**: Before writing any code:

1. Perform requirement analysis first
2. **NO assumptions** - if information is unclear, STOP and ask the user
3. For architectural changes or complex features, provide **3 different approaches** with pros/cons for user selection

### Execution Control

🔴 **CRITICAL STOP RULE**:

- **Never generate code in the first response**
- Output must end with `Implementation Plan`
- Must explicitly state: "請確認以上計畫,批准後我才會開始執行。"
- Only proceed with implementation after user confirms with "確認" or "Go"

### Version Control Practice

**MANDATORY**: After completing each development phase:

1. **Commit Changes**: Use git to commit all changes with descriptive messages
2. **Commit Message Format**:
   ```
   [Phase X] Brief description
   
   - Implemented feature 1
   - Implemented feature 2
   - Updated documentation
   ```
3. **Git Workflow**:
   ```bash
   git add .
   git commit -m "[Phase X] Description"
   git tag -a vX.Y.Z -m "Phase X completion"
   ```
4. **Phase Completion Checklist**:
   - [ ] All planned features implemented
   - [ ] Tests written and passing
   - [ ] Documentation updated
   - [ ] Git commit created
   - [ ] Tag created (optional, for major phases)

## Documentation Standards

### Code Analysis

- When asked to analyze the project, read ALL relevant files thoroughly
- Never provide superficial analysis

### Auto-Documentation

- Store architecture diagrams and logic explanations as `.md` files
- Path convention: `./docs/<feature-name>/`
- Create directories with `mkdir` if they don't exist
- Never modify user's original text/data without permission

## Project Overview

### Purpose

En-Ai-Cli is a CLI-based AI conversation environment with the following core features:

1. Interactive AI dialogue in terminal
2. OpenRouter API integration for multiple LLM models
3. Command suggestion from AI responses with user confirmation
4. Command execution with result feedback
5. Cross-platform shell environment support

### Key Responsibilities

- **User Safety First**: Always confirm before executing system commands
- **Platform Awareness**: Detect and adapt to Unix-like/PowerShell/CMD environments
- **Permission Handling**: Consider system privilege requirements for operations

## Architecture Guidelines

### Cross-Platform Strategy

- **Environment Detection**: Identify shell type (fish/bash/zsh/PowerShell/CMD) before command generation
- **Command Translation**: Adapt commands for target platform (e.g., `ls` vs `dir`, path separators)
- **Platform-Specific Code**: Isolate platform logic into dedicated modules for maintainability

### Security Patterns

- **Command Confirmation Flow**:
  1. AI generates command suggestion
  2. Display command with clear explanation
  3. Require explicit user approval ("確認" or "Go")
  4. Execute only after confirmation
- **Privilege Escalation**: Ask before using `sudo`/`Run as Administrator`
- **Dangerous Operations**: Extra confirmation for destructive commands (rm, format, etc.)

### API Integration

- **OpenRouter Configuration**:
  - Store API keys securely (config file with appropriate permissions)
  - Support model selection and switching
  - Handle API errors gracefully with user-friendly messages
- **Model Management**:
  - Cache available models list
  - Allow user preferences for default model
  - Display model capabilities when relevant

## Project Structure

```
en-ai-cli/
├── src/en_ai_cli/           # 主程式碼
│   ├── __init__.py
│   ├── __main__.py          # 支援 python -m 執行
│   ├── cli.py               # CLI 命令入口（Click）
│   ├── core/                # 核心功能模組
│   │   ├── config.py        # ✓ 雙層配置管理（workspace/global）
│   │   ├── platform.py      # ✓ 平台偵測與指令轉換
│   │   ├── executor.py      # ✓ 指令執行引擎與安全防護
│   │   └── session.py       # ✓ Session 與角色管理
│   ├── services/            # 服務層
│   │   ├── provider_manager.py # ✓ Provider 自動偵測與調度
│   │   ├── llm_provider.py  # ✓ LLM Provider 抽象基類
│   │   ├── ollama.py        # ✓ Ollama 本地端支援
│   │   ├── openrouter.py    # ✓ OpenRouter API 客戶端
│   │   └── history.py       # ✓ 對話歷程記錄（JSONL/Markdown）
│   └── ui/                  # 使用者介面
│       ├── terminal.py      # ✓ Rich 終端介面工具
│       └── prompts.py       # ✓ 指令確認與安全警告 UI
├── tests/                   # 測試（pytest）
├── docs/                    # 自動生成文檔
│   └── DEVELOPMENT.md       # 開發文檔
├── pyproject.toml           # Poetry 專案配置
└── README.md
```

### Key Implementation Details

**ConfigManager** (src/en_ai_cli/core/config.py):

- 雙層配置：workspace (`./.en-ai/config.json`) 優先於 global (`~/.en-ai/config.json`)
- 實體化角色設定：將 `DEFAULT_ROLES` 寫入設定檔供使用者自定義

**CommandExecutor** (src/en_ai_cli/core/executor.py):

- **目錄追蹤**: 攔截 `cd` 指令並使用 `os.chdir` 維護 Python 程序內部的 cwd
- **安全防護**: `analyze_path_safety` 偵測 `..` 指令與系統關鍵路徑
- **權限管理**: 偵測並提示 `sudo` 指令

**SessionManager** (src/en_ai_cli/core/session.py):

- Session ID 生成與追蹤
- 訊息計數與上限檢查（預設 50 則，可配置）
- 角色 (Role) 資訊持久化與 System Prompt 注入
- Session 切換與自動封存

**ProviderManager** (src/en_ai_cli/services/provider_manager.py):

- 自動偵測 Ollama 與 OpenRouter 狀態
- 優先順序策略（Ollama > OpenRouter）
- 統一模型切換與調度

**Prompts System** (src/en_ai_cli/ui/prompts.py):

- 分級警告 UI：Cyan (安全), Yellow (危險), Bold Red (致命風險)
- 高風險操作需使用者鍵入 `YES` 確認

**HistoryLogger** (src/en_ai_cli/services/history.py):

- JSONL 格式存儲對話歷程
- Markdown 匯出功能（封存對話記錄）

### Configuration Files

**全域配置** (`~/.en-ai/config.json`):

```json
{
  "openrouter_api_key": "sk-xxx",
  "Context Management & Archiving

### Session Context Tracking

- **Purpose**: 防止上下文過長影響 AI 回應品質
- **Mechanism**: 
  - 追蹤當前 session 的訊息數量
  - 達到警告閾值（預設 80%）時提醒用戶
  - 建議封存對話並開啟新 session

### Archive Workflow

1. **觸發時機**:
   - 訊息數達到 `max_context_messages * context_warning_threshold`
   - 用戶手動執行 `en-ai session archive`

2. **警告提示**:
   ```
   ⚠️  上下文即將達到限制 (40/50)
   建議操作：
     1. 封存當前對話並開新 session
     2. 繼續對話（可能影響 AI 回應品質）
     3. 手動清理歷史訊息
   ```

3. **封存格式**:
   - 檔案格式: Markdown
   - 命名規則: `session_{session_id}_{timestamp}.md`
   - 存放位置: `.en-ai/archives/` (workspace) 或 `~/.en-ai/archives/` (global)

4. **Markdown 內容結構**:
   ```markdown
   # AI 對話記錄
   **Session ID**: abc123
   **建立時間**: 2026-02-10 11:20:15
   **訊息總數**: 48
   
   ## 對話內容
   ### 時間戳記
   **User**: 用戶輸入
   **Assistant**: AI 回應
   **System**: 系統訊息（指令執行結果）
   ```

### Configuration Options

新增配置選項：
```json
{
  "max_context_messages": 50,
  "context_warning_threshold": 0.8,
  "auto_archive_on_limit": false,
  "archive_path": ".en-ai/archives/"
}
```

### CLI Commands

待實作的 session 相關命令：
```bash
en-ai session list                    # 列出所有 session
en-ai session new                     # 建立新 session
en-ai session switch <id>             # 切換 session
en-ai session export <id>             # 匯出為 Markdown
en-ai session archive                 # 封存當前 session
en-ai session stats                   # 顯示統計資訊
```

## Development Roadmap

### Phase 1: 基礎架構 ✅
- [x] 專案結構與 Poetry 配置
- [x] 雙層配置系統 (ConfigManager)
- [x] 平台偵測模組 (PlatformDetector)
- [x] OpenRouter API 客戶端 (Free 模型優先)
- [x] 基本 CLI 命令 (init, config, models, info)
- [x] Rich 終端介面工具

### Phase 2: 核心對話功能 ✅
- [x] 指令執行引擎 (executor.py)
- [x] Session 管理器 (session.py)
- [x] 對話歷程記錄 (history.py)
- [x] chat 命令實作 (AI 對話循環)
- [x] 指令建議與確認 UI (prompts.py)

### Phase 3: Session 管理與封存 ✅
- [x] Session 命令群組 (list/new/switch)
- [x] 自動封存功能與 Markdown 匯出
- [x] 閾值警告機制

### Phase 4: 角色系統與 Ollama 整合 ✅
- [x] 實體化角色設定與 `en-ai role` 指令
- [x] Ollama 本地端 Provider 整合
- [x] ProviderManager 多源調度

### Phase 5: 安全防護與指令強化 ✅
- [x] 終端目錄追蹤 (`cd` 攔截)
- [x] 路徑安全分析與分級警告 UI
- [x] `YES` 強制確認機制

### Phase 6: 斜線指令 (Slash Commands) 🚧
- [ ] 攔截 `/help`, `/role`, `/stats`
- [ ] 不離開對話切換角色
- [ ] 精美的表格回饋

### Phase 7: 優化與擴展 🔮
- [ ] 效能優化與插件系統
- [ ] 多語言支援

## default_model": "meta-llama/llama-3.2-3b-instruct:free",
  "prefer_free_models": true,
  "fallback_to_paid": false,
  "color_mode": true,
  "auto_save_history": true,
  "max_context_messages": 50
}
```

**Workspace 配置** (`./.en-ai/config.json`):

- 繼承 global 配置
- 可覆蓋特定專案需求的設定

## Pre-Response Checklist

Before completing any response, verify:

- [ ] Did I stop at "Implementation Plan" if code changes are needed?
- [ ] Did I ask for clarification instead of making assumptions?
- [ ] Did I respond in Traditional Chinese?
- [ ] Did I provide multiple options for significant decisions?
