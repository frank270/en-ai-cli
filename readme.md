# 🤖 En-Ai-Cli

> 在終端機中與 AI 對話，讓 AI 成為你的命令列助手

En-Ai-Cli 是一個智慧的命令列工具，讓你可以直接在終端機中與 AI 對話，獲得指令建議並安全執行。支援跨平台環境，整合 OpenRouter API，優先使用免費模型。

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## ✨ 特色功能

- 🎯 **智慧對話**：在終端機中與 AI 直接對話，獲得即時協助
- 💡 **指令建議**：AI 根據對話內容自動建議適合的命令
- ✅ **安全執行**：所有指令執行前都需要你的確認
- 🌍 **跨平台支援**：自動偵測並適配 Unix/Linux、macOS、PowerShell、CMD 環境
- 🆓 **免費優先**：優先使用 OpenRouter 的免費 AI 模型
- 📦 **雙層配置**：支援全域和專案層級配置，靈活管理
- 💾 **對話記錄**：自動儲存對話歷程，支援 Session 管理
- 🎨 **美觀介面**：使用 Rich 套件提供彩色終端介面

## 📋 系統需求

- Python 3.9 或更高版本
- [Poetry](https://python-poetry.org/) (用於依賴管理)
- [OpenRouter API Key](https://openrouter.ai/) (免費註冊即可獲得)

## 🚀 快速開始

### 安裝

```bash
# 克隆專案
git clone https://github.com/yourusername/en-ai-cli.git
cd en-ai-cli

# 安裝依賴
poetry install
```

### 初始化

首次使用需要初始化配置：

```bash
# 初始化全域配置（推薦）
poetry run en-ai init --global

# 或初始化當前專案的 workspace 配置
poetry run en-ai init
```

初始化過程會引導你：
1. 輸入 OpenRouter API Key
2. 選擇模型策略（建議選擇「優先使用 free 模型」）
3. 設定彩色模式

### 基本使用

```bash
# 查看可用的免費模型
poetry run en-ai models list --free

# 查看當前配置
poetry run en-ai config list

# 查看系統資訊
poetry run en-ai info

# 開始對話（即將推出）
poetry run en-ai chat
```

## 📖 使用範例

### 配置管理

```bash
# 設定配置值
poetry run en-ai config set color_mode true
poetry run en-ai config set prefer_free_models true

# 取得配置值
poetry run en-ai config get default_model

# 列出所有配置（顯示 workspace 和 global）
poetry run en-ai config list
```

### 模型管理

```bash
# 列出所有可用模型
poetry run en-ai models list

# 僅列出免費模型
poetry run en-ai models list --free
```

### Workspace vs 全域配置

En-Ai-Cli 支援兩層配置：

- **全域配置** (`~/.en-ai/config.json`)：適用於所有專案
- **Workspace 配置** (`./.en-ai/config.json`)：專案特定配置，優先於全域

```bash
# 初始化全域配置
en-ai init --global

# 初始化 workspace 配置
cd my-project
en-ai init

# 設定 workspace 配置
en-ai config set default_model "meta-llama/llama-3.2-3b-instruct:free"

# 設定全域配置
en-ai config set prefer_free_models true --global
```

## 🔧 配置檔案

### 配置範例

```json
{
  "openrouter_api_key": "sk-xxx",
  "default_model": "meta-llama/llama-3.2-3b-instruct:free",
  "prefer_free_models": true,
  "fallback_to_paid": false,
  "color_mode": true,
  "auto_save_history": true,
  "max_context_messages": 50
}
```

### 配置選項說明

| 選項 | 說明 | 預設值 |
|------|------|--------|
| `openrouter_api_key` | OpenRouter API 金鑰 | - |
| `default_model` | 預設使用的模型 | 自動選擇 |
| `prefer_free_models` | 優先使用免費模型 | `true` |
| `fallback_to_paid` | 無免費模型時使用付費模型 | `false` |
| `color_mode` | 啟用彩色輸出 | `true` |
| `auto_save_history` | 自動儲存對話歷程 | `true` |
| `max_context_messages` | 最大上下文訊息數 | `50` |

## 🛠️ 開發指南

詳細的開發文檔請參考 [DEVELOPMENT.md](docs/DEVELOPMENT.md)。

### 開發環境設定

```bash
# 安裝開發依賴
poetry install

# 執行測試
poetry run pytest

# 測試覆蓋率
poetry run pytest --cov=en_ai_cli --cov-report=html

# 程式碼格式化
poetry run black src/

# 程式碼檢查
poetry run ruff check src/
```

### 專案結構

```
en-ai-cli/
├── src/en_ai_cli/          # 原始碼
│   ├── core/               # 核心功能（配置、平台偵測）
│   ├── services/           # 服務層（OpenRouter API）
│   ├── ui/                 # 使用者介面
│   └── cli.py              # CLI 命令入口
├── tests/                  # 測試檔案
├── docs/                   # 文檔
└── pyproject.toml          # Poetry 配置
```

## 🗺️ 開發路線圖

### ✅ Phase 1: 基礎架構（已完成）
- [x] 專案結構與依賴管理
- [x] 雙層配置系統
- [x] 平台偵測與指令轉換
- [x] OpenRouter API 整合
- [x] 免費模型優先邏輯
- [x] 基本 CLI 命令

### 🚧 Phase 2: 核心對話功能（開發中）
- [ ] 指令執行引擎
- [ ] AI 對話循環
- [ ] 指令確認介面
- [ ] `en-ai chat` 命令

### 📅 Phase 3: Session & History
- [ ] Session 管理
- [ ] 對話歷程記錄
- [ ] Session 切換功能
- [ ] 歷程查詢與匯出

## 🤝 貢獻

歡迎提交 Issue 或 Pull Request！

## 📄 授權

MIT License - 詳見 [LICENSE](LICENSE) 檔案

## 🙏 致謝

- [OpenRouter](https://openrouter.ai/) - 提供統一的 AI 模型 API
- [Click](https://click.palletsprojects.com/) - 優秀的 CLI 框架
- [Rich](https://rich.readthedocs.io/) - 美觀的終端介面套件

---

**注意**：本專案目前處於早期開發階段，部分功能仍在實作中。