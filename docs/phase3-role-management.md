# Phase 3 Completion: Role & Persona Management

## 實作內容

### 1. 核心邏輯 (Core)
- **ConfigManager (`src/en_ai_cli/core/config.py`)**:
    - 定義了 `DEFAULT_ROLES` (default, shell, code)。
    - 新增 `get_roles()`, `get_active_role_name()`, `get_active_role_prompt()`。
    - 在預設配置中加入 `active_role` 與 `roles` 欄位。
- **Session (`src/en_ai_cli/core/session.py`)**:
    - `Session` 資料結構現在包含 `role` 屬性。
    - `SessionManager` 在建立新 Session 時會自動帶入當前活躍的角色。
    - `get_session_info()` 現在包含角色資訊。

### 2. CLI 指令 (Commands)
- 新增 `en-ai role` 指令群組：
    - `list`: 以表格列出所有角色及其狀態。
    - `set <name>`: 切換活躍角色。
    - `add <name> --prompt "..."`: 新增自定義角色。
    - `show <name>`: 顯示角色的詳細 System Prompt。
    - `delete <name>`: 刪除角色（不允許刪除 default）。
- 更新 `en-ai init`: 支援在初始化時選擇初始角色。

### 3. 對話整合 (Chat Integration)
- `en-ai chat`:
    - 歡迎畫面現在會顯示目前使用的角色。
    - 每一則發送給 AI 的訊息都會動態注入該角色的 `system_prompt`。
- `stats`: Session 統計資訊現在包含當前角色。

## 驗證狀態
- 角色切換邏輯已整合至 Config 雙層系統。
- `prompt-toolkit` 完美支援方向鍵與輸入流。
- UI 樣式已完成相容性修復。
- **單元測試完成**：已通過 `tests/test_role.py` 中的 6 個測試案例，涵蓋：
    - 預設角色載入。
    - 活躍角色切換邏輯。
    - 自定義角色覆蓋。
    - Session 角色持久化。
    - 舊版本 Session 相容性（自動修補 `role` 欄位）。
    - SessionManager 自動角色分配。

## 後續計畫
- [ ] 支援從外部 Markdown 檔案匯入角色。
- [ ] 增加更多預設專家角色（如 Git 專家、Python 導師）。
