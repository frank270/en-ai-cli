"""測試對話歷程記錄模組"""

import pytest
from pathlib import Path
from datetime import datetime

from en_ai_cli.services.history import HistoryLogger, MessageRole, Message


@pytest.fixture
def temp_sessions_dir(tmp_path):
    """建立臨時 sessions 目錄"""
    return tmp_path / "sessions"


@pytest.fixture
def history_logger(temp_sessions_dir):
    """建立測試用的歷程記錄器"""
    session_id = "test123"
    return HistoryLogger(temp_sessions_dir, session_id)


def test_add_user_message(history_logger):
    """測試新增用戶訊息"""
    history_logger.add_user_message("Hello, AI!")
    
    messages = history_logger.get_messages()
    assert len(messages) == 1
    assert messages[0].role == MessageRole.USER
    assert messages[0].content == "Hello, AI!"


def test_add_assistant_message(history_logger):
    """測試新增 AI 助手訊息"""
    history_logger.add_assistant_message("Hello, human!")
    
    messages = history_logger.get_messages()
    assert len(messages) == 1
    assert messages[0].role == MessageRole.ASSISTANT
    assert messages[0].content == "Hello, human!"


def test_add_system_message(history_logger):
    """測試新增系統訊息"""
    history_logger.add_system_message("Command executed successfully")
    
    messages = history_logger.get_messages()
    assert len(messages) == 1
    assert messages[0].role == MessageRole.SYSTEM
    assert messages[0].content == "Command executed successfully"


def test_get_messages_with_limit(history_logger):
    """測試取得訊息（帶限制）"""
    # 新增多個訊息
    for i in range(10):
        history_logger.add_user_message(f"Message {i}")
    
    # 取得最後 5 則
    messages = history_logger.get_messages(limit=5)
    
    assert len(messages) == 5
    assert messages[0].content == "Message 5"
    assert messages[-1].content == "Message 9"


def test_export_markdown(history_logger):
    """測試匯出 Markdown"""
    history_logger.add_user_message("列出檔案")
    history_logger.add_assistant_message("建議執行: ls -la")
    history_logger.add_system_message("指令執行成功")
    
    markdown = history_logger.export_markdown()
    
    assert "# AI 對話記錄" in markdown
    assert "Session ID" in markdown
    assert "**User**:" in markdown
    assert "列出檔案" in markdown
    assert "**Assistant**:" in markdown
    assert "建議執行: ls -la" in markdown
    assert "**System**:" in markdown
    assert "指令執行成功" in markdown


def test_clear_history(history_logger):
    """測試清除歷程"""
    history_logger.add_user_message("Message 1")
    history_logger.add_user_message("Message 2")
    
    history_logger.clear_history()
    
    messages = history_logger.get_messages()
    assert len(messages) == 0


def test_message_to_dict():
    """測試訊息轉換為字典"""
    message = Message(MessageRole.USER, "Test message")
    data = message.to_dict()
    
    assert data["role"] == "user"
    assert data["content"] == "Test message"
    assert "timestamp" in data


def test_message_from_dict():
    """測試從字典建立訊息"""
    data = {
        "role": "user",
        "content": "Test message",
        "timestamp": datetime.now().isoformat(),
        "metadata": {}
    }
    
    message = Message.from_dict(data)
    
    assert message.role == MessageRole.USER
    assert message.content == "Test message"


def test_jsonl_format(history_logger):
    """測試 JSONL 格式"""
    history_logger.add_user_message("Test")
    
    # 讀取 JSONL 檔案
    jsonl_file = history_logger.history_file
    assert jsonl_file.exists()
    
    lines = jsonl_file.read_text().strip().split("\n")
    assert len(lines) == 1
