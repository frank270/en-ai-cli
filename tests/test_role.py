import pytest
from pathlib import Path
import json
from en_ai_cli.core.config import ConfigManager, ConfigScope, DEFAULT_ROLES
from en_ai_cli.core.session import Session, SessionManager

def test_config_default_roles():
    """測試預設角色是否正確載入"""
    config = ConfigManager()
    roles = config.get_roles()
    assert "default" in roles
    assert "shell" in roles
    assert "code" in roles
    assert roles["shell"]["system_prompt"].startswith("你是一位終端機與命令列專家")

def test_config_active_role_logic(tmp_path):
    """測試活躍角色切換邏輯"""
    config = ConfigManager(workspace_path=tmp_path)
    
    # 預設應為 default
    assert config.get_active_role_name() == "default"
    
    # 切換角色
    config.set("active_role", "code", ConfigScope.WORKSPACE)
    assert config.get_active_role_name() == "code"
    assert "世界級的軟體工程師" in config.get_active_role_prompt()

def test_config_custom_roles(tmp_path):
    """測試自定義角色"""
    config = ConfigManager(workspace_path=tmp_path)
    custom_roles = {
        "translator": {"system_prompt": "你是一個翻譯官"}
    }
    config.set("roles", custom_roles, ConfigScope.WORKSPACE)
    
    roles = config.get_roles()
    assert "translator" in roles
    assert roles["translator"]["system_prompt"] == "你是一個翻譯官"
    # 確保預設角色還在
    assert "shell" in roles

def test_session_role_persistence():
    """測試 Session 中的角色持久化"""
    from datetime import datetime
    
    # 測試正常建立
    s = Session(session_id="test-123", created_at=datetime.now(), role="shell")
    assert s.role == "shell"
    
    # 測試序列化
    data = s.to_dict()
    assert data["role"] == "shell"
    
    # 測試反序列化
    s2 = Session.from_dict(data)
    assert s2.role == "shell"

def test_session_backward_compatibility():
    """測試 Session 向後相容性（無 role 欄位時）"""
    from datetime import datetime
    old_data = {
        "session_id": "old-session",
        "created_at": datetime.now().isoformat(),
        "message_count": 5,
        "last_activity": datetime.now().isoformat()
    }
    # 應該預設為 default 而非崩潰
    s = Session.from_dict(old_data)
    assert s.role == "default"

def test_session_manager_role_assignment(tmp_path):
    """測試 SessionManager 建立 Session 時是否正確分配 Role"""
    config = ConfigManager(workspace_path=tmp_path)
    config.set("active_role", "shell", ConfigScope.WORKSPACE)
    
    mgr = SessionManager(config)
    # mock sessions_dir to tmp_path
    mgr.sessions_dir = tmp_path / "sessions"
    mgr.sessions_dir.mkdir(parents=True)
    mgr.current_session_file = mgr.sessions_dir / "current.json"
    
    new_session = mgr._create_new_session()
    assert new_session.role == "shell"
