"""測試 Session 管理模組"""

import pytest
from pathlib import Path
from datetime import datetime

from en_ai_cli.core.session import SessionManager, Session
from en_ai_cli.core.config import ConfigManager


@pytest.fixture
def temp_sessions_dir(tmp_path):
    """建立臨時 sessions 目錄"""
    return tmp_path / "sessions"


@pytest.fixture
def session_manager(temp_sessions_dir, monkeypatch):
    """建立測試用的 Session 管理器"""
    # Mock ConfigManager
    class MockConfig:
        def get(self, key, default=None):
            defaults = {
                "max_context_messages": 50,
                "context_warning_threshold": 0.8,
            }
            return defaults.get(key, default)
        
        def is_workspace_mode(self):
            return False
    
    # Mock Path.home()
    monkeypatch.setattr(Path, "home", lambda: temp_sessions_dir.parent)
    
    config = MockConfig()
    mgr = SessionManager(config)
    mgr.sessions_dir = temp_sessions_dir
    temp_sessions_dir.mkdir(parents=True, exist_ok=True)
    
    return mgr


def test_new_session(session_manager):
    """測試建立新 session"""
    session_id = session_manager.new_session()
    
    assert isinstance(session_id, str)
    assert len(session_id) == 8  # 短 UUID
    assert session_manager.current_session is not None
    assert session_manager.current_session.id == session_id


def test_load_session(session_manager):
    """測試載入 session"""
    # 建立 session
    session_id = session_manager.new_session()
    
    # 載入 session
    loaded_session = session_manager.load_session(session_id)
    
    assert loaded_session is not None
    assert loaded_session.id == session_id


def test_increment_message_count(session_manager):
    """測試增加訊息計數"""
    session_id = session_manager.new_session()
    
    # 增加計數
    count1 = session_manager.increment_message_count()
    assert count1 == 1
    
    count2 = session_manager.increment_message_count()
    assert count2 == 2


def test_should_warn_limit(session_manager):
    """測試警告閾值"""
    session_id = session_manager.new_session()
    
    # 未達閾值
    assert not session_manager.should_warn_limit()
    
    # 手動設置訊息數到閾值
    session_manager.current_session.message_count = 40  # 80% of 50
    session_manager._save_session(session_manager.current_session)
    
    assert session_manager.should_warn_limit()


def test_is_limit_reached(session_manager):
    """測試是否達到上限"""
    session_id = session_manager.new_session()
    
    # 未達上限
    assert not session_manager.is_limit_reached()
    
    # 設置到上限
    session_manager.current_session.message_count = 50
    session_manager._save_session(session_manager.current_session)
    
    assert session_manager.is_limit_reached()


def test_get_stats(session_manager):
    """測試取得統計資訊"""
    session_id = session_manager.new_session()
    session_manager.increment_message_count()
    session_manager.increment_message_count()
    
    stats = session_manager.get_stats()
    
    assert stats["session_id"] == session_id
    assert stats["message_count"] == 2
    assert stats["max_messages"] == 50
    assert stats["usage_percentage"] == 4.0


def test_list_sessions(session_manager):
    """測試列出所有 session"""
    # 建立多個 session
    id1 = session_manager.new_session()
    id2 = session_manager.new_session()
    id3 = session_manager.new_session()
    
    sessions = session_manager.list_sessions()
    
    assert len(sessions) >= 3
    session_ids = [s.id for s in sessions]
    assert id1 in session_ids
    assert id2 in session_ids
    assert id3 in session_ids


def test_delete_session(session_manager):
    """測試刪除 session"""
    session_id = session_manager.new_session()
    
    # 刪除 session
    result = session_manager.delete_session(session_id)
    
    assert result is True
    assert session_manager.load_session(session_id) is None
    assert session_manager.current_session is None
