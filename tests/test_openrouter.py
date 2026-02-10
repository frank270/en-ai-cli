"""測試 OpenRouter Provider"""

import pytest
from unittest.mock import Mock, patch
from en_ai_cli.services.openrouter import OpenRouterProvider
from en_ai_cli.services.llm_provider import ModelInfo, ChatMessage


@pytest.fixture
def config():
    """測試配置"""
    return {
        "openrouter_api_key": "test_api_key",
        "prefer_free_models": True,
        "openrouter_default_model": "meta-llama/llama-3.2-3b-instruct:free",
    }


@pytest.fixture
def provider(config):
    """建立測試用的 provider"""
    return OpenRouterProvider(config)


def test_provider_initialization(provider):
    """測試 provider 初始化"""
    assert provider.api_key == "test_api_key"
    assert provider.prefer_free is True
    assert provider.get_provider_name() == "openrouter"


def test_fallback_models(provider):
    """測試 fallback 模型列表"""
    models = provider._get_fallback_models()
    assert len(models) > 0
    assert all(isinstance(m, ModelInfo) for m in models)
    assert all(m.is_free for m in models)


def test_model_info_dataclass():
    """測試 ModelInfo 資料結構"""
    model = ModelInfo(
        id="test-model",
        name="Test Model",
        context_length=8192,
        is_free=True,
        pricing={"prompt": "0", "completion": "0"}
    )
    
    assert model.id == "test-model"
    assert model.is_free is True
    assert model.context_length == 8192
