"""OpenRouter API 客戶端：支援 Free 模型優先選擇"""

import httpx
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Model:
    """AI 模型資料結構"""
    id: str
    name: str
    context_length: int
    is_free: bool
    pricing: Dict[str, str]
    description: Optional[str] = None


class OpenRouterClient:
    """OpenRouter API 客戶端"""

    BASE_URL = "https://openrouter.ai/api/v1"
    
    # 已知的 Free 模型列表（作為 fallback）
    KNOWN_FREE_MODELS = [
        "meta-llama/llama-3.2-3b-instruct:free",
        "meta-llama/llama-3.2-1b-instruct:free",
        "google/gemma-2-9b-it:free",
        "microsoft/phi-3-mini-128k-instruct:free",
        "nousresearch/hermes-3-llama-3.1-405b:free",
    ]

    def __init__(self, api_key: str, prefer_free: bool = True):
        """
        初始化 OpenRouter 客戶端
        
        Args:
            api_key: OpenRouter API Key
            prefer_free: 是否優先使用 free 模型
        """
        self.api_key = api_key
        self.prefer_free = prefer_free
        self.client = httpx.Client(timeout=30.0)
        self._models_cache: Optional[List[Model]] = None
        self._cache_time: Optional[datetime] = None
        self._cache_ttl = timedelta(hours=1)  # 快取 1 小時

    def test_connection(self) -> bool:
        """
        測試 API 連線是否正常
        
        Returns:
            True 如果連線成功
        """
        try:
            response = self.client.get(
                f"{self.BASE_URL}/models",
                headers=self._get_headers()
            )
            return response.status_code == 200
        except Exception:
            return False

    def get_models(self, force_refresh: bool = False) -> List[Model]:
        """
        取得可用模型列表（帶快取）
        
        Args:
            force_refresh: 是否強制重新取得
            
        Returns:
            模型列表
        """
        # 檢查快取
        if not force_refresh and self._is_cache_valid():
            return self._models_cache
        
        try:
            response = self.client.get(
                f"{self.BASE_URL}/models",
                headers=self._get_headers()
            )
            response.raise_for_status()
            
            data = response.json()
            models = []
            
            for model_data in data.get("data", []):
                pricing = model_data.get("pricing", {})
                prompt_price = float(pricing.get("prompt", "0"))
                completion_price = float(pricing.get("completion", "0"))
                is_free = prompt_price == 0 and completion_price == 0
                
                model = Model(
                    id=model_data["id"],
                    name=model_data.get("name", model_data["id"]),
                    context_length=model_data.get("context_length", 0),
                    is_free=is_free,
                    pricing=pricing,
                    description=model_data.get("description"),
                )
                models.append(model)
            
            # 更新快取
            self._models_cache = models
            self._cache_time = datetime.now()
            
            return models
            
        except Exception as e:
            # API 失敗時使用已知的 free 模型作為 fallback
            return self._get_fallback_models()

    def get_free_models(self) -> List[Model]:
        """
        取得所有 free 模型
        
        Returns:
            Free 模型列表
        """
        all_models = self.get_models()
        return [m for m in all_models if m.is_free]

    def select_best_model(self, prefer_free: Optional[bool] = None) -> Optional[str]:
        """
        智慧選擇最佳模型
        
        Args:
            prefer_free: 是否優先 free 模型（覆蓋實例設定）
            
        Returns:
            模型 ID，如果沒有可用模型則返回 None
        """
        prefer_free = prefer_free if prefer_free is not None else self.prefer_free
        
        if prefer_free:
            free_models = self.get_free_models()
            if free_models:
                # 依上下文長度排序，選擇最大的
                return max(free_models, key=lambda m: m.context_length).id
        
        # 如果不優先 free 或沒有 free 模型，選擇最佳的付費模型
        all_models = self.get_models()
        if all_models:
            return max(all_models, key=lambda m: m.context_length).id
        
        return None

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 1000,
    ) -> Dict[str, Any]:
        """
        發送對話請求
        
        Args:
            messages: 對話訊息列表
            model: 模型 ID（如果為 None，自動選擇）
            max_tokens: 最大 token 數
            
        Returns:
            API 回應
        """
        if model is None:
            model = self.select_best_model()
            if model is None:
                raise ValueError("沒有可用的模型")
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
        }
        
        response = self.client.post(
            f"{self.BASE_URL}/chat/completions",
            headers=self._get_headers(),
            json=payload,
        )
        response.raise_for_status()
        
        return response.json()

    def _get_headers(self) -> Dict[str, str]:
        """取得 API 請求標頭"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _is_cache_valid(self) -> bool:
        """檢查快取是否有效"""
        if self._models_cache is None or self._cache_time is None:
            return False
        return datetime.now() - self._cache_time < self._cache_ttl

    def _get_fallback_models(self) -> List[Model]:
        """取得 fallback 模型列表"""
        return [
            Model(
                id=model_id,
                name=model_id,
                context_length=8192,  # 假設的值
                is_free=True,
                pricing={"prompt": "0", "completion": "0"},
            )
            for model_id in self.KNOWN_FREE_MODELS
        ]

    def __del__(self):
        """清理資源"""
        if hasattr(self, 'client'):
            self.client.close()
