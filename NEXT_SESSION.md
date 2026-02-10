# 下次開發 Session 起點

## 當前狀態

**版本**: v0.3.5  
**日期**: 2026-02-10  
**Git Commit**: 93d9b71  
**測試狀態**: ✅ 31/31 通過（Ollama 整合）

## 已完成階段

- ✅ **Phase 1**: 基礎架構（配置、平台、API 客戶端）
- ✅ **Phase 2**: 核心對話功能（executor、session、history、chat）
- ✅ **Phase 3**: Session 管理與封存
- ✅ **Phase 3.5**: Ollama 本地端支援整合

## 下一步任務：實際 Provider 測試

### 目標

測試 En-Ai-Cli 與真實 LLM Providers（Ollama 和 OpenRouter）的整合，驗證完整功能流程。

### 準備工作

1. **安裝 Ollama（可選，推薦）**
   - 前往 https://ollama.ai/
   - 下載並安裝 Ollama
   - 運行 `ollama pull qwen2.5-coder:3b`
   - 驗證：`ollama list`

2. **取得 OpenRouter API Key（可選）**
   - 前往 https://openrouter.ai/
   - 註冊並取得 API key（建議使用 free 模型降低成本）

3. **驗證開發環境**
   ```bash
   conda activate py39
   cd /Users/n/Projects/en-ai-cli
   pytest tests/ -v  # 確認所有測試通過
   ```

4. **初始化配置**
   ```bash
   en-ai init
   # 若 Ollama 可用，會自動偵測並設為預設
   # 可選擇性設定 OpenRouter 作為備援
   ```

### 測試計畫

#### 階段 0：Provider 管理測試
- [ ] `en-ai provider list` 顯示可用 providers
- [ ] `en-ai provider status ollama` 顯示 Ollama 狀態
- [ ] `en-ai provider status openrouter` 顯示 OpenRouter 狀態
- [ ] `en-ai provider switch` 切換成功
- [ ] `en-ai models list` 顯示多個 provider 的模型
- [ ] `en-ai models list --provider ollama` 指定 provider

#### 階段 1：Ollama 本地測試（若已安裝）
- [ ] Ollama 自動偵測成功
- [ ] 模型列表取得成功
- [ ] 預設模型設定正確（qwen2.5-coder:3b）
- [ ] 本地對話功能正常

#### 階段 2：OpenRouter API 測試（若已設定）
- [ ] API Key 驗證成功
- [ ] 模型列表取得成功
- [ ] free 模型優先選擇

#### 階段 3：對話功能測試
- [ ] 簡單問答（如："Python 版本查詢指令是什麼？"）
- [ ] AI 回應顯示正常
- [ ] 歷史記錄存儲（檢查 `~/.en-ai/sessions/*.jsonl`）
- [ ] Provider 資訊顯示在對話開始

#### 階段 4：指令建議與執行
- [ ] AI 建議指令（如："查看當前目錄的 Python 文件"）
- [ ] 指令確認提示顯示
- [ ] 指令執行與結果回饋
- [ ] 執行結果記錄到歷史

#### 階段 5：上下文管理
- [ ] 80% 警告觸發測試（需發送 40+ 則訊息）
- [ ] 警告提示顯示正確
- [ ] 封存功能正常
- [ ] 100% 上限處理（強制封存或清理）

#### 階段 6：Session 管理
- [ ] `session list` 顯示正確
- [ ] `session switch` 切換成功
- [ ] `session stats` 資訊準確
- [ ] `session export` Markdown 格式正確
- [ ] `session archive` 封存完整

#### 階段 7：Provider 切換測試
- [ ] 從 Ollama 切換到 OpenRouter
- [ ] 從 OpenRouter 切換到 Ollama
- [ ] 切換後對話功能正常
- [ ] Provider 不可用時錯誤提示清楚

### 測試問題範例

**Provider 測試類**：
1. "列出所有可用的 AI providers"
2. "切換到 Ollama"
3. "顯示當前 provider 狀態"

**簡單問答類**：
1. "什麼是 Python？"
2. "如何列出目錄內容？"
3. "Git 的基本指令有哪些？"

**指令建議類**：
1. "我想查看當前目錄下所有 Python 文件，該怎麼做？"
2. "如何檢查我的 Python 版本？"
3. "幫我創建一個名為 test.txt 的空文件"

**多輪對話類**：
1. "什麼是虛擬環境？"（第1輪）
2. "如何創建虛擬環境？"（第2輪）
3. "如何啟用它？"（第3輪）

### 預期測試時間

- Provider 管理測試：5-10 分鐘
- Ollama 本地測試：10-15 分鐘
- OpenRouter API 測試：10-15 分鐘
- 完整對話流程測試：30-45 分鐘
- 邊界情況測試：另外 15-20 分鐘

### 可能遇到的問題

1. **Ollama 相關問題**
   - Ollama 未啟動：執行 `ollama serve`
   - 模型未安裝：執行 `ollama pull qwen2.5-coder:3b`
   - 端點錯誤：檢查配置中的 `ollama_endpoint`

2. **API Key 無效**
   - 檢查是否正確複製
   - 確認 OpenRouter 帳號狀態

3. **模型選擇失敗**
   - 檢查 free 模型可用性
   - 嘗試切換到其他 free 模型

4. **網路連線問題**
   - 確認網路暢通
   - 檢查防火牆設置

5. **Provider 切換問題**
   - 確認目標 provider 可用
   - 查看錯誤訊息提示

6. **上下文過長**
   - 測試封存功能
   - 驗證新 session 創建

### 除錯資訊收集

如遇問題，收集以下資訊：
- 錯誤訊息完整輸出
- `en-ai provider list` 輸出
- `en-ai provider status <name>` 輸出
- `en-ai config list` 輸出
- `en-ai session stats` 輸出
- Session 歷史檔案：`~/.en-ai/sessions/<session_id>.jsonl`
- Ollama 狀態：`ollama list` 和 `curl http://localhost:11434/api/version`

### 成功標準

- ✅ Provider 管理功能正常
- ✅ Ollama 本地對話可用（若已安裝）
- ✅ OpenRouter API 對話可用（若已設定）
- ✅ Provider 切換功能正常
- ✅ 所有對話階段測試通過
- ✅ 無異常錯誤或崩潰
- ✅ 上下文管理按預期工作
- ✅ Session 管理功能完整

完成測試後，可進入 Phase 4（優化與擴展）或根據測試結果調整功能。

---

## 技術架構更新（Phase 3.5）

### LLM Provider 架構

```
LLMProvider (抽象基類)
├── OllamaProvider (本地 Ollama)
└── OpenRouterProvider (雲端 API)

ProviderManager
├── 自動偵測可用 providers
├── 優先順序：ollama > openrouter
├── 配置管理與切換
└── 錯誤處理（不自動 fallback）
```

### 新增 CLI 指令

```bash
# Provider 管理
en-ai provider list           # 列出所有 providers 及狀態
en-ai provider status [name]  # 顯示 provider 詳細資訊
en-ai provider switch <name>  # 切換 preferred provider

# 模型管理（增強）
en-ai models list                    # 顯示所有 provider 的模型
en-ai models list --provider ollama  # 指定 provider
en-ai models list --free             # 僅顯示 free 模型
```

### 配置結構更新

```json
{
  "preferred_provider": "ollama",
  "ollama_endpoint": "http://localhost:11434",
  "ollama_default_model": "qwen2.5-coder:3b",
  "openrouter_api_key": "sk-xxx",
  "openrouter_default_model": "meta-llama/llama-3.2-3b-instruct:free",
  "prefer_free_models": true
}
```

---

**重要提示**：
- 推薦使用 Ollama 作為主要 provider（免費、本地、快速）
- OpenRouter 可作為備援或需要特定模型時使用
- free 模型通常每日有請求限制，請注意控制測試頻率
- 測試環境：**務必使用 py39 Conda 環境**，避免污染 base 環境
