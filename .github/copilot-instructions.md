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
│   │   ├── executor.py      # 指令執行引擎（待實作）
│   │   └── session.py       # Session 管理（待實作）
│   ├── services/            # 服務層
│   │   ├── openrouter.py    # ✓ OpenRouter API 客戶端（Free 模型優先）
│   │   └── history.py       # 對話歷程記錄（待實作）
│   └── ui/                  # 使用者介面
│       ├── terminal.py      # ✓ Rich 終端介面工具
│       └── prompts.py       # 互動提示（待實作）
├── tests/                   # 測試（pytest）
├── docs/                    # 自動生成文檔
│   └── DEVELOPMENT.md       # 開發文檔
├── pyproject.toml           # Poetry 專案配置
└── README.md
```

### Key Implementation Details

**ConfigManager** (src/en_ai_cli/core/config.py):

- 雙層配置：workspace (`./.en-ai/config.json`) 優先於 global (`~/.en-ai/config.json`)
- 使用 `ConfigScope` enum 區分作用域
- 支援初始化、讀取、寫入配置

**PlatformDetector** (src/en_ai_cli/core/platform.py):

- 自動偵測平台類型（Unix/PowerShell/CMD）
- 提供跨平台指令轉換功能
- Shell 名稱識別（fish/bash/zsh 等）

**OpenRouterClient** (src/en_ai_cli/services/openrouter.py):

- Free 模型優先策略
- 模型列表快取（1 小時 TTL）
- 智慧模型選擇邏輯

**CLI 命令架構** (src/en_ai_cli/cli.py):

- 使用 Click 框架
- 已實作: init, config (set/get/list), models (list), info
- 待實作: chat, session 相關命令

**SessionManager** (src/en_ai_cli/core/session.py - 待實作):

- Session ID 生成與追蹤
- 訊息計數與上限檢查（預設 50 則，可配置）
- 上下文警告機制（達 80% 時提醒用戶）
- Session 切換與管理

**HistoryLogger** (src/en_ai_cli/services/history.py - 待實作):

- JSONL 格式存儲對話歷程
- Markdown 匯出功能（封存對話記錄）
- 訊息查詢與過濾
- 支援 workspace/global 雙層存儲

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

### Phase 2: 核心對話功能 🚧
- [ ] 指令執行引擎 (executor.py)
- [ ] Session 管理器 (session.py)
  - [ ] Session ID 生成與追蹤
  - [ ] 訊息計數與上限檢查
  - [ ] 上下文警告機制
- [ ] 對話歷程記錄 (history.py)
  - [ ] JSONL 格式存儲
  - [ ] Markdown 匯出功能
  - [ ] 訊息查詢與過濾
- [ ] chat 命令實作
  - [ ] AI 對話循環
  - [ ] 指令建議與確認
  - [ ] 執行結果回饋
  - [ ] 上下文警告整合
- [ ] 互動提示介面 (prompts.py)

### Phase 3: Session 管理與封存 📅
- [ ] Session 命令群組
  - [ ] session list/new/switch
  - [ ] session export/archive
  - [ ] session stats
- [ ] 自動封存功能
- [ ] 封存檔案管理
- [ ] 歷程查詢與搜尋

### Phase 4: 優化與擴展 🔮
- [ ] 效能優化
- [ ] 錯誤處理強化
- [ ] 多語言支援（如需要）
- [ ] 插件系統（可選）

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
