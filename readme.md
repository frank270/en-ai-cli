# 🤖 En-Ai-Cli

> 在終端機中與 AI 對話，讓 AI 成為你的命令列助手

En-Ai-Cli 是一個智慧的命令列工具，讓你可以直接在終端機中與 AI 對話，獲得指令建議並安全執行。支援跨平台環境，整合 OpenRouter API，優先使用免費模型。

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## ✨ 特色功能

- 🎯 **智慧對話**：在終端機中與 AI 直接對話，獲得即時協助
- 💡 **指令建議**：AI 根據對話內容自動建議適合的命令
- ✅ **安全執行**：所有指令執行前都需要你的確認
- 🤖 **Ollama 整合**：支援本機 Ollama 服務，實現 100% 本機運行的隱私對話
- 🌍 **跨平台支援**：自動偵測並適配 Unix/Linux、macOS、PowerShell、CMD 環境
- 🆓 **免費優先**：優先使用 Ollama 或 OpenRouter 的免費 AI 模型
- 📦 **雙層設定**：支援全域和專案層級設定，靈活管理
- 💾 **對話記錄與工作階段**：自動儲存對話歷程，支援工作階段切換、統計與 Markdown 匯出
- 🎨 **美觀介面**：使用 Rich 套件提供彩色終端介面，包含訊息計數提示

## 📋 系統需求

- Python 3.9 或更高版本
- [pip](https://pip.pypa.io/en/stable/) (用於套件管理)
- [Ollama](https://ollama.ai/) (推薦，用於本機 AI 回應)
- [OpenRouter API 金鑰](https://openrouter.ai/) (選用，作為雲端備援)

## 🚀 快速開始

### 安裝

```bash
# 複製專案
git clone https://github.com/yourusername/en-ai-cli.git
cd en-ai-cli

# 安裝開發模式（推薦在虛擬環境中執行）
pip install -e .
```

### 初始化

首次使用建議先啟動 Ollama 並安裝模型（如 `ollama pull qwen2.5-coder:3b`），然後執行：

```bash
# 初始化設定
en-ai init
```

### 基本使用

```bash
# 開始對話
en-ai chat

# 提供者管理
en-ai provider list    # 列出可用服務（Ollama/OpenRouter）
en-ai provider status  # 查看目前狀態
en-ai provider switch  # 切換優先服務

# 查看可用模型
en-ai models list
```

## 📖 使用範例

### 對話與指令執行

在 `en-ai chat` 模式下：
1. 輸入問題，例如：「如何查看目前目錄的檔案大小？」
2. AI 會給出指令建議（例如 `du -sh *`）。
3. 系統會詢問：`是否執行此指令？ [y/n]`
4. 按下 `y` 即可執行並在終端看到結果。

### 工作階段管理

```bash
en-ai session list     # 列出歷史對話
en-ai session stats    # 查看目前對話統計
en-ai session archive  # 封存對話並開啟新工作階段
en-ai session export   # 將對話匯出為 Markdown
```

### 設定管理

```bash
# 設定設定值
en-ai config set color_mode true
en-ai config set prefer_free_models true

# 取得設定值
en-ai config get default_model

# 列出所有設定（顯示工作區和全域）
en-ai config list
```

### 模型管理

```bash
# 列出所有可用模型
en-ai models list

# 僅列出免費模型
en-ai models list --free
```

### 工作區 vs 全域設定

En-Ai-Cli 支援兩層設定：

- **全域設定** (`~/.en-ai/config.json`)：適用於所有專案
- **工作區設定** (`./.en-ai/config.json`)：專案特定設定，優先於全域

```bash
# 初始化全域設定
en-ai init --global

# 初始化工作區設定
cd my-project
en-ai init

# 設定工作區設定
en-ai config set default_model "meta-llama/llama-3.2-3b-instruct:free"

# 設定全域設定
en-ai config set prefer_free_models true --global
```

## 🔧 設定檔案

### 設定範例

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

### 設定選項說明

| 選項                   | 說明                                        | 預設值                   |
| ---------------------- | ------------------------------------------- | ------------------------ |
| `preferred_provider`   | 偏好的服務提供者 (`ollama` 或 `openrouter`) | `ollama`                 |
| `ollama_endpoint`      | Ollama API 位址                             | `http://localhost:11434` |
| `openrouter_api_key`   | OpenRouter API 金鑰                         | -                        |
| `prefer_free_models`   | 優先使用免費模型                            | `true`                   |
| `color_mode`           | 啟用彩色輸出                                | `true`                   |
| `max_context_messages` | 最大上下文訊息數                            | `50`                     |

## 🛠️ 開發指南

詳細的開發文檔請參考 [DEVELOPMENT.md](docs/DEVELOPMENT.md)。

### 開發環境設定

```bash
# 安裝開發依賴
pip install -e ".[dev]"

# 執行測試
pytest

# 測試涵蓋率
pytest --cov=en_ai_cli --cov-report=html

# 程式碼格式化
black src/

# 程式碼檢查
ruff check src/
```

### 專案結構

```
en-ai-cli/
├── src/en_ai_cli/          # 原始碼
│   ├── core/               # 核心功能（設定、平台偵測）
│   ├── services/           # 服務層（OpenRouter API）
│   ├── ui/                 # 使用者介面
│   └── cli.py              # CLI 命令入口
├── tests/                  # 測試檔案
├── docs/                   # 文檔
└── pyproject.toml          # 專案工具設定 (PEP 518)
```

## 🗺️ 開發路線圖

### ✅ 第一階段：基礎架構（已完成）
- [x] 專案結構與依賴管理
- [x] 雙層設定系統
- [x] 平台偵測與指令轉換
- [x] OpenRouter API 整合
- [x] 基本 CLI 命令

### ✅ 第二階段：核心對話功能（已完成）
- [x] 指令執行引擎
- [x] AI 對話循環
- [x] 指令確認介面
- [x] `en-ai chat` 命令

### ✅ 第三階段：工作階段與歷史記錄（已完成）
- [x] 工作階段管理與切換
- [x] 對話歷程 JSONL 儲存
- [x] 統計資訊與 Markdown 匯出
- [x] Ollama 本機端支援整合 (第 3.5 階段)

### 📅 第四階段：優化與豐富化
- [ ] 外掛系統支援
- [ ] 更強大的指令提取與安全性檢查
- [ ] 多語言支援介面
- [ ] 網路連接與逾時最佳化

## 📄 授權

MIT 授權 - 詳見 [LICENSE](LICENSE) 檔案

## 🙏 致謝

- [Ollama](https://ollama.ai/) - 強大的本機端 LLM 執行環境
- [OpenRouter](https://openrouter.ai/) - 提供統一的 AI 模型 API
- [Click](https://click.palletsprojects.com/) - 優秀的 CLI 框架
- [Rich](https://rich.readthedocs.io/) - 美觀的終端介面套件

---

**注意**：本專案目前處於早期開發階段，部分功能仍在實作測試中。
**注意**：本專案只是自己使用，尚未達到生產環境的穩定性。
