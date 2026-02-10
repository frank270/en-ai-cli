# 下次開發 Session 起點

**版本**: v0.4.0  
**日期**: 2026-02-10  
**目標**: 實作 Slash Commands (斜線指令) 系統，提昇對話中的工具操作效率。

## 當前狀態回顧

### 已完成
- ✅ **角色系統 (Phase 4)**: 支持角色實體化設定與切換。
- ✅ **安全防護 (Phase 5)**: 分級警告 UI、`cd` 攔截、路徑分析 (`..` 防護)。
- ✅ **測試驗證**: 40/40 測試通過，包含核心邏輯與邊界安全性測試。

## 待辦事項 (Phase 6: Slash Commands)

<h3>1. 實作 Slash Command 核心攔截器</h3>
- [ ] 在 `cli.py` 的 `chat` 迴圈中加入攔截邏輯（如 `message.startswith('/')`）。
- [ ] 定義指令映射表 (Command Registry)。

<h3>2. 內建指令開發</h3>
- [ ] `/help`: 顯示精美的 Rich Table 表格，列出所有可用斜線指令。
- [ ] `/role [name]`: 在不離開 chat 模式的情況下切換目前角色（Session 持久化）。
- [ ] `/stats`: 即時顯示當前 Session 的 Token 數或訊息計數。
- [ ] `/clear`: 清理當前畫面（`rich.console.clear`）。
- [ ] `/exit`: 離開對話模式（同 `exit`/`quit`）。

<h3>3. UI/UX 優化</h3>
- [ ] 使用 Dim 顏色或特定 Prefix (例如 `[SYSTEM]`) 顯示指令執行結果。
- [ ] 加入指令建議提示 (Autocomplete 候補，若 `prompt-toolkit` 支援)。

## 測試計畫
- [ ] `/help` 顯示正確性。
- [ ] 開啟對話後，成功使用 `/role code_reviewer` 切換角色且 AI 回應風格改變。
- [ ] 測試 `/invalid` 是否有友善的錯誤提示。

## 預期問題
- 切換角色後，System Prompt 在 Session 中的即時更新邏輯是否完全無誤。
- 與 AI 正規對話內容若剛好以 `/` 開頭的衝突處理（轉義機制）。

---
**提示**: 下次開發前請先執行 `pytest` 確保環境底層依然穩定。
