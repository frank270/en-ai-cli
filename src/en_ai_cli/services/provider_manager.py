"""Provider Manager：管理所有 LLM Providers"""

from typing import Dict, Any, Optional, List
from .llm_provider import LLMProvider
from .ollama import OllamaProvider
from .openrouter import OpenRouterProvider


class ProviderManager:
    """管理所有 LLM Providers"""
    
    # 支援的 provider 類型
    PROVIDERS = {
        "ollama": OllamaProvider,
        "openrouter": OpenRouterProvider,
    }
    
    def __init__(self, config: Dict[str, Any]):
        """初始化 Provider Manager
        
        Args:
            config: 配置字典
        """
        self.config = config
        self._providers: Dict[str, LLMProvider] = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """初始化所有 providers"""
        for name, provider_class in self.PROVIDERS.items():
            try:
                provider = provider_class(self.config)
                self._providers[name] = provider
            except Exception as e:
                # 初始化失敗時記錄，但不中斷
                pass
    
    def get_available_providers(self) -> List[str]:
        """取得所有可用的 provider 名稱
        
        Returns:
            可用 provider 名稱列表
        """
        available = []
        for name, provider in self._providers.items():
            if provider.is_available():
                available.append(name)
        return available
    
    def get_provider_status(self, name: str) -> Dict[str, Any]:
        """取得特定 provider 的狀態
        
        Args:
            name: Provider 名稱
        
        Returns:
            狀態字典，包含 available, config_valid 等資訊
        """
        if name not in self._providers:
            return {
                "exists": False,
                "available": False,
                "config_valid": False,
            }
        
        provider = self._providers[name]
        return {
            "exists": True,
            "available": provider.is_available(),
            "config_valid": provider.validate_config(),
            "default_model": provider.get_default_model(),
        }
    
    def get_current_provider(self) -> Optional[LLMProvider]:
        """取得當前應使用的 provider
        
        根據配置和可用性選擇：
        1. 檢查 preferred_provider 配置
        2. 若該 provider 不可用，拋出異常（不自動 fallback）
        3. 若未配置 preferred_provider，預設偵測順序：ollama -> openrouter
        
        Returns:
            LLM Provider 實例
        
        Raises:
            RuntimeError: 當沒有可用的 provider 時
        """
        preferred = self.config.get("preferred_provider")
        
        if preferred:
            # 使用者明確指定了 provider
            if preferred not in self._providers:
                raise RuntimeError(f"未知的 provider: {preferred}")
            
            provider = self._providers[preferred]
            if not provider.is_available():
                raise RuntimeError(
                    f"Provider '{preferred}' 不可用。"
                    f"請檢查配置或切換到其他 provider。"
                )
            
            return provider
        
        # 未指定 provider，按優先順序自動偵測
        detection_order = ["ollama", "openrouter"]
        
        for name in detection_order:
            if name in self._providers:
                provider = self._providers[name]
                if provider.is_available():
                    return provider
        
        # 沒有任何可用的 provider
        raise RuntimeError(
            "沒有可用的 LLM provider。\n"
            "請檢查：\n"
            "1. Ollama 是否已安裝並執行中\n"
            "2. OpenRouter API Key 是否已設定（使用 'en-ai config set openrouter_api_key <key>'）"
        )
    
    def switch_provider(self, name: str) -> bool:
        """切換到指定的 provider
        
        Args:
            name: Provider 名稱
        
        Returns:
            True 表示切換成功，False 表示失敗
        
        Raises:
            ValueError: 當 provider 不存在或不可用時
        """
        if name not in self._providers:
            raise ValueError(f"未知的 provider: {name}")
        
        provider = self._providers[name]
        if not provider.is_available():
            raise ValueError(f"Provider '{name}' 不可用，無法切換")
        
        # 更新配置（需要由外部儲存）
        self.config["preferred_provider"] = name
        return True
    
    def list_all_providers(self) -> Dict[str, Dict[str, Any]]:
        """列出所有 providers 及其狀態
        
        Returns:
            Provider 狀態字典
        """
        result = {}
        for name in self.PROVIDERS.keys():
            result[name] = self.get_provider_status(name)
        return result
    
    def get_provider(self, name: str) -> Optional[LLMProvider]:
        """取得指定的 provider
        
        Args:
            name: Provider 名稱
        
        Returns:
            Provider 實例，若不存在則返回 None
        """
        return self._providers.get(name)
