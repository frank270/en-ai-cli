"""Provider Manager 測試"""

import pytest
from unittest.mock import Mock, patch
from en_ai_cli.services.provider_manager import ProviderManager


@pytest.fixture
def base_config():
    """基礎配置"""
    return {
        "ollama_endpoint": "http://localhost:11434",
        "ollama_default_model": "qwen2.5-coder:3b",
        "openrouter_api_key": "test-key",
        "prefer_free_models": True,
    }


@pytest.fixture
def manager(base_config):
    """建立 ProviderManager 實例"""
    return ProviderManager(base_config)


def test_provider_initialization(manager):
    """測試 providers 初始化"""
    assert len(manager._providers) == 2
    assert "ollama" in manager._providers
    assert "openrouter" in manager._providers


def test_get_available_providers_ollama_only(base_config):
    """測試取得可用 providers（僅 Ollama）"""
    manager = ProviderManager(base_config)
    
    with patch.object(manager._providers["ollama"], "is_available", return_value=True), \
         patch.object(manager._providers["openrouter"], "is_available", return_value=False):
        
        available = manager.get_available_providers()
        assert available == ["ollama"]


def test_get_available_providers_both(base_config):
    """測試取得可用 providers（兩者都可用）"""
    manager = ProviderManager(base_config)
    
    with patch.object(manager._providers["ollama"], "is_available", return_value=True), \
         patch.object(manager._providers["openrouter"], "is_available", return_value=True):
        
        available = manager.get_available_providers()
        assert set(available) == {"ollama", "openrouter"}


def test_get_provider_status_exists(manager):
    """測試取得 provider 狀態（存在）"""
    with patch.object(manager._providers["ollama"], "is_available", return_value=True), \
         patch.object(manager._providers["ollama"], "validate_config", return_value=True), \
         patch.object(manager._providers["ollama"], "get_default_model", return_value="qwen2.5-coder:3b"):
        
        status = manager.get_provider_status("ollama")
        
        assert status["exists"] is True
        assert status["available"] is True
        assert status["config_valid"] is True
        assert status["default_model"] == "qwen2.5-coder:3b"


def test_get_provider_status_not_exists(manager):
    """測試取得 provider 狀態（不存在）"""
    status = manager.get_provider_status("unknown")
    
    assert status["exists"] is False
    assert status["available"] is False
    assert status["config_valid"] is False


def test_get_current_provider_preferred_available(base_config):
    """測試取得當前 provider（preferred 可用）"""
    config = base_config.copy()
    config["preferred_provider"] = "ollama"
    manager = ProviderManager(config)
    
    with patch.object(manager._providers["ollama"], "is_available", return_value=True):
        provider = manager.get_current_provider()
        assert provider.get_provider_name() == "ollama"


def test_get_current_provider_preferred_unavailable(base_config):
    """測試取得當前 provider（preferred 不可用）"""
    config = base_config.copy()
    config["preferred_provider"] = "ollama"
    manager = ProviderManager(config)
    
    with patch.object(manager._providers["ollama"], "is_available", return_value=False):
        with pytest.raises(RuntimeError, match="Provider 'ollama' 不可用"):
            manager.get_current_provider()


def test_get_current_provider_auto_detect_ollama(base_config):
    """測試自動偵測 provider（Ollama 可用）"""
    manager = ProviderManager(base_config)
    
    with patch.object(manager._providers["ollama"], "is_available", return_value=True):
        provider = manager.get_current_provider()
        assert provider.get_provider_name() == "ollama"


def test_get_current_provider_auto_detect_openrouter(base_config):
    """測試自動偵測 provider（僅 OpenRouter 可用）"""
    manager = ProviderManager(base_config)
    
    with patch.object(manager._providers["ollama"], "is_available", return_value=False), \
         patch.object(manager._providers["openrouter"], "is_available", return_value=True):
        
        provider = manager.get_current_provider()
        assert provider.get_provider_name() == "openrouter"


def test_get_current_provider_none_available(base_config):
    """測試取得當前 provider（無可用）"""
    manager = ProviderManager(base_config)
    
    with patch.object(manager._providers["ollama"], "is_available", return_value=False), \
         patch.object(manager._providers["openrouter"], "is_available", return_value=False):
        
        with pytest.raises(RuntimeError, match="沒有可用的 LLM provider"):
            manager.get_current_provider()


def test_switch_provider_success(base_config):
    """測試切換 provider（成功）"""
    manager = ProviderManager(base_config)
    
    with patch.object(manager._providers["openrouter"], "is_available", return_value=True):
        result = manager.switch_provider("openrouter")
        assert result is True
        assert manager.config["preferred_provider"] == "openrouter"


def test_switch_provider_not_exists(manager):
    """測試切換 provider（不存在）"""
    with pytest.raises(ValueError, match="未知的 provider"):
        manager.switch_provider("unknown")


def test_switch_provider_unavailable(base_config):
    """測試切換 provider（不可用）"""
    manager = ProviderManager(base_config)
    
    with patch.object(manager._providers["ollama"], "is_available", return_value=False):
        with pytest.raises(ValueError, match="Provider 'ollama' 不可用"):
            manager.switch_provider("ollama")


def test_list_all_providers(manager):
    """測試列出所有 providers"""
    with patch.object(manager._providers["ollama"], "is_available", return_value=True), \
         patch.object(manager._providers["ollama"], "validate_config", return_value=True), \
         patch.object(manager._providers["ollama"], "get_default_model", return_value="qwen2.5-coder:3b"), \
         patch.object(manager._providers["openrouter"], "is_available", return_value=False), \
         patch.object(manager._providers["openrouter"], "validate_config", return_value=True), \
         patch.object(manager._providers["openrouter"], "get_default_model", return_value=None):
        
        all_providers = manager.list_all_providers()
        
        assert "ollama" in all_providers
        assert "openrouter" in all_providers
        assert all_providers["ollama"]["available"] is True
        assert all_providers["openrouter"]["available"] is False


def test_get_provider(manager):
    """測試取得指定 provider"""
    provider = manager.get_provider("ollama")
    assert provider is not None
    assert provider.get_provider_name() == "ollama"
    
    provider = manager.get_provider("unknown")
    assert provider is None
