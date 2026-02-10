"""Ollama Provider 實作

提供本地 Ollama 服務的整合。
"""

import requests
from typing import List, Dict, Any, Optional
from .llm_provider import LLMProvider, ModelInfo, ChatMessage, ChatResponse


class OllamaProvider(LLMProvider):
    """Ollama Provider 實作"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化 Ollama Provider
        
        Args:
            config: 配置字典，應包含：
                - ollama_endpoint: Ollama API 端點（預設 http://localhost:11434）
                - ollama_default_model: 預設模型名稱
        """
        super().__init__(config)
        self.endpoint = config.get("ollama_endpoint", "http://localhost:11434")
        self.default_model = config.get("ollama_default_model", "qwen2.5-coder:3b")
        self._timeout = 30  # 請求逾時時間（秒）
    
    def get_provider_name(self) -> str:
        """取得 Provider 名稱"""
        return "ollama"
    
    def is_available(self) -> bool:
        """檢查 Ollama 是否可用
        
        嘗試連接 Ollama API 的 /api/version 端點。
        
        Returns:
            True 表示 Ollama 正在執行且可連接，False 表示不可用
        """
        try:
            response = requests.get(
                f"{self.endpoint}/api/version",
                timeout=3  # 快速檢查，3 秒逾時
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def list_models(self) -> List[ModelInfo]:
        """取得 Ollama 已安裝的模型列表
        
        Returns:
            模型資訊列表
        
        Raises:
            Exception: 當無法取得模型列表時
        """
        try:
            response = requests.get(
                f"{self.endpoint}/api/tags",
                timeout=self._timeout
            )
            response.raise_for_status()
            
            data = response.json()
            models = []
            
            for model_data in data.get("models", []):
                model_info = ModelInfo(
                    id=model_data.get("name", ""),
                    name=model_data.get("name", ""),
                    description=f"Size: {model_data.get('size', 0) / (1024**3):.2f} GB",
                    is_free=True  # Ollama 模型都是本地免費的
                )
                models.append(model_info)
            
            return models
        
        except Exception as e:
            raise Exception(f"無法取得 Ollama 模型列表: {str(e)}")
    
    def chat_completion(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatResponse:
        """Ollama 聊天完成
        
        Args:
            messages: 訊息列表
            model: 模型名稱（若為 None，使用預設模型）
            temperature: 溫度參數 (0.0-1.0)
            max_tokens: 最大 token 數（Ollama 使用 num_predict 參數）
            **kwargs: 其他 Ollama 參數
        
        Returns:
            聊天回應
        
        Raises:
            Exception: 當請求失敗時
        """
        selected_model = model or self.default_model
        
        # 轉換訊息格式
        ollama_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # 建立請求參數
        payload = {
            "model": selected_model,
            "messages": ollama_messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }
        
        # 若有指定 max_tokens，加入 num_predict 參數
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        # 加入其他自定義參數
        if kwargs:
            payload["options"].update(kwargs)
        
        try:
            response = requests.post(
                f"{self.endpoint}/api/chat",
                json=payload,
                timeout=self._timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            # 解析回應
            return ChatResponse(
                content=data.get("message", {}).get("content", ""),
                model=selected_model,
                usage={
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                },
                finish_reason=data.get("done_reason", "stop")
            )
        
        except Exception as e:
            raise Exception(f"Ollama 請求失敗: {str(e)}")
    
    def get_default_model(self) -> Optional[str]:
        """取得預設模型"""
        return self.default_model
    
    def validate_config(self) -> bool:
        """驗證配置是否有效
        
        檢查 endpoint 格式是否正確。
        
        Returns:
            True 表示配置有效，False 表示無效
        """
        if not self.endpoint:
            return False
        
        # 簡單檢查 URL 格式
        if not (self.endpoint.startswith("http://") or self.endpoint.startswith("https://")):
            return False
        
        return True
    
    def get_version(self) -> Optional[str]:
        """取得 Ollama 版本資訊
        
        Returns:
            版本字串，若無法取得則返回 None
        """
        try:
            response = requests.get(
                f"{self.endpoint}/api/version",
                timeout=3
            )
            response.raise_for_status()
            data = response.json()
            return data.get("version", "unknown")
        except Exception:
            return None
