"""Ollama Provider 測試"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from en_ai_cli.services.ollama import OllamaProvider
from en_ai_cli.services.llm_provider import ChatMessage


@pytest.fixture
def config():
    """測試配置"""
    return {
        "ollama_endpoint": "http://localhost:11434",
        "ollama_default_model": "qwen2.5-coder:3b",
    }


@pytest.fixture
def provider(config):
    """建立 OllamaProvider 實例"""
    return OllamaProvider(config)


def test_provider_name(provider):
    """測試 provider 名稱"""
    assert provider.get_provider_name() == "ollama"


def test_is_available_success(provider):
    """測試 Ollama 可用性檢查（成功）"""
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        assert provider.is_available() is True
        mock_get.assert_called_once()


def test_is_available_failure(provider):
    """測試 Ollama 可用性檢查（失敗）"""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = Exception("Connection failed")
        
        assert provider.is_available() is False


def test_list_models_success(provider):
    """測試取得模型列表（成功）"""
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {
                    "name": "llama3.2:latest",
                    "size": 4_000_000_000,
                },
                {
                    "name": "qwen2.5-coder:3b",
                    "size": 3_000_000_000,
                },
            ]
        }
        mock_get.return_value = mock_response
        
        models = provider.list_models()
        
        assert len(models) == 2
        assert models[0].id == "llama3.2:latest"
        assert models[0].is_free is True
        assert models[1].id == "qwen2.5-coder:3b"


def test_list_models_failure(provider):
    """測試取得模型列表（失敗）"""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = Exception("API Error")
        
        with pytest.raises(Exception, match="無法取得 Ollama 模型列表"):
            provider.list_models()


def test_chat_completion_success(provider):
    """測試聊天完成（成功）"""
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {
                "content": "Hello! How can I help you?"
            },
            "prompt_eval_count": 10,
            "eval_count": 20,
            "done_reason": "stop"
        }
        mock_post.return_value = mock_response
        
        messages = [ChatMessage(role="user", content="Hello")]
        response = provider.chat_completion(messages)
        
        assert response.content == "Hello! How can I help you?"
        assert response.model == "qwen2.5-coder:3b"
        assert response.usage["total_tokens"] == 30


def test_chat_completion_with_custom_model(provider):
    """測試使用自定義模型的聊天完成"""
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "Response"},
            "prompt_eval_count": 5,
            "eval_count": 10,
        }
        mock_post.return_value = mock_response
        
        messages = [ChatMessage(role="user", content="Test")]
        response = provider.chat_completion(messages, model="llama3.2:latest")
        
        assert response.model == "llama3.2:latest"


def test_chat_completion_failure(provider):
    """測試聊天完成（失敗）"""
    with patch("requests.post") as mock_post:
        mock_post.side_effect = Exception("Request failed")
        
        messages = [ChatMessage(role="user", content="Hello")]
        
        with pytest.raises(Exception, match="Ollama 請求失敗"):
            provider.chat_completion(messages)


def test_get_default_model(provider):
    """測試取得預設模型"""
    assert provider.get_default_model() == "qwen2.5-coder:3b"


def test_validate_config_valid(provider):
    """測試配置驗證（有效）"""
    assert provider.validate_config() is True


def test_validate_config_invalid():
    """測試配置驗證（無效）"""
    # 空 endpoint
    invalid_config = {"ollama_endpoint": ""}
    provider = OllamaProvider(invalid_config)
    assert provider.validate_config() is False
    
    # 無效 URL
    invalid_config = {"ollama_endpoint": "invalid-url"}
    provider = OllamaProvider(invalid_config)
    assert provider.validate_config() is False


def test_get_version_success(provider):
    """測試取得版本（成功）"""
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"version": "0.1.0"}
        mock_get.return_value = mock_response
        
        version = provider.get_version()
        assert version == "0.1.0"


def test_get_version_failure(provider):
    """測試取得版本（失敗）"""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = Exception("Failed")
        
        version = provider.get_version()
        assert version is None
