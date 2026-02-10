"""測試配置管理模組"""

import pytest
import json
from pathlib import Path
from en_ai_cli.core.config import ConfigManager, ConfigScope


@pytest.fixture
def temp_config_dir(tmp_path):
    """建立臨時配置目錄"""
    return tmp_path


@pytest.fixture
def config_manager(temp_config_dir, monkeypatch):
    """建立測試用的配置管理器"""
    # 修改 home 目錄為臨時目錄
    monkeypatch.setattr(Path, "home", lambda: temp_config_dir)
    return ConfigManager(workspace_path=temp_config_dir / "workspace")


def test_init_global_config(config_manager):
    """測試初始化全域配置"""
    config_manager.init_config(ConfigScope.GLOBAL)
    assert config_manager.global_path.exists()


def test_init_workspace_config(config_manager):
    """測試初始化 workspace 配置"""
    config_manager.init_config(ConfigScope.WORKSPACE)
    assert config_manager.workspace_path.exists()


def test_set_and_get_config(config_manager):
    """測試設定和取得配置"""
    config_manager.set("test_key", "test_value", ConfigScope.GLOBAL)
    value = config_manager.get("test_key")
    assert value == "test_value"


def test_workspace_priority(config_manager):
    """測試 workspace 配置優先於 global"""
    config_manager.set("key", "global_value", ConfigScope.GLOBAL)
    config_manager.set("key", "workspace_value", ConfigScope.WORKSPACE)
    
    value = config_manager.get("key")
    assert value == "workspace_value"


def test_fallback_to_global(config_manager):
    """測試 fallback 到 global 配置"""
    config_manager.set("key", "global_value", ConfigScope.GLOBAL)
    
    value = config_manager.get("key")
    assert value == "global_value"


def test_is_workspace_mode(config_manager):
    """測試判斷 workspace 模式"""
    assert not config_manager.is_workspace_mode()
    
    config_manager.init_config(ConfigScope.WORKSPACE)
    assert config_manager.is_workspace_mode()
