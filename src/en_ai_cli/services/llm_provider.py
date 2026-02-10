"""LLM Provider 抽象基類

定義所有 LLM Provider 必須實作的統一介面。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ModelInfo:
    """模型資訊"""
    id: str
    name: str
    context_length: Optional[int] = None
    description: Optional[str] = None
    pricing: Optional[Dict[str, Any]] = None
    is_free: bool = False


@dataclass
class ChatMessage:
    """聊天訊息"""
    role: str  # "user", "assistant", "system"
    content: str


@dataclass
class ChatResponse:
    """聊天回應"""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None


class LLMProvider(ABC):
    """LLM Provider 抽象基類"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化 Provider
        
        Args:
            config: 配置字典
        """
        self.config = config
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """取得 Provider 名稱
        
        Returns:
            Provider 名稱（例如："ollama", "openrouter"）
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """檢查 Provider 是否可用
        
        Returns:
            True 表示可用，False 表示不可用
        """
        pass
    
    @abstractmethod
    def list_models(self) -> List[ModelInfo]:
        """取得可用模型列表
        
        Returns:
            模型資訊列表
        
        Raises:
            Exception: 當無法取得模型列表時
        """
        pass
    
    @abstractmethod
    def chat_completion(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatResponse:
        """聊天完成
        
        Args:
            messages: 訊息列表
            model: 模型名稱（若為 None，使用預設模型）
            temperature: 溫度參數 (0.0-1.0)
            max_tokens: 最大 token 數
            **kwargs: 其他參數
        
        Returns:
            聊天回應
        
        Raises:
            Exception: 當請求失敗時
        """
        pass
    
    def get_default_model(self) -> Optional[str]:
        """取得預設模型
        
        Returns:
            預設模型名稱，若無則返回 None
        """
        return None
    
    def validate_config(self) -> bool:
        """驗證配置是否有效
        
        Returns:
            True 表示配置有效，False 表示無效
        """
        return True
