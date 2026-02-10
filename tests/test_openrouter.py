"""測試 OpenRouter API 客戶端"""

import pytest
from en_ai_cli.services.openrouter import OpenRouterClient, Model


@pytest.fixture
def mock_client():
    """建立測試用的客戶端（不需要真實 API Key）"""
    return OpenRouterClient("test_api_key", prefer_free=True)


def test_client_initialization(mock_client):
    """測試客戶端初始化"""
    assert mock_client.api_key == "test_api_key"
    assert mock_client.prefer_free is True


def test_fallback_models(mock_client):
    """測試 fallback 模型列表"""
    models = mock_client._get_fallback_models()
    assert len(models) > 0
    assert all(isinstance(m, Model) for m in models)
    assert all(m.is_free for m in models)


def test_model_dataclass():
    """測試 Model 資料結構"""
    model = Model(
        id="test-model",
        name="Test Model",
        context_length=8192,
        is_free=True,
        pricing={"prompt": "0", "completion": "0"}
    )
    
    assert model.id == "test-model"
    assert model.is_free is True
    assert model.context_length == 8192
