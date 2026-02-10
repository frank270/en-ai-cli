"""測試指令執行引擎"""

import pytest
from pathlib import Path

from en_ai_cli.core.executor import CommandExecutor
from en_ai_cli.core.platform import PlatformDetector


@pytest.fixture
def executor():
    """建立指令執行器"""
    return CommandExecutor()


def test_execute_safe_command(executor):
    """測試執行安全指令"""
    # 執行簡單的安全指令
    platform = PlatformDetector.detect()
    
    if platform.value == "unix":
        result = executor.execute("echo test", require_confirmation=False)
    else:
        result = executor.execute("echo test", require_confirmation=False)
    
    assert result.exit_code == 0
    assert "test" in result.output.lower()


def test_check_privilege():
    """測試檢查特權指令"""
    executor = CommandExecutor()
    
    # sudo 指令需要特權
    assert executor.check_privilege("sudo ls") is True
    
    # 普通指令不需要特權
    assert executor.check_privilege("ls -la") is False


def test_is_dangerous_command():
    """測試檢查危險指令"""
    executor = CommandExecutor()
    
    # 危險指令
    assert executor.is_dangerous("rm -rf /") is True
    assert executor.is_dangerous("format c:") is True
    
    # 安全指令
    assert executor.is_dangerous("ls") is False
    assert executor.is_dangerous("echo hello") is False


def test_execution_result():
    """測試執行結果資料結構"""
    from en_ai_cli.core.executor import ExecutionResult
    
    result = ExecutionResult(
        command="echo test",
        exit_code=0,
        output="test",
        error=""
    )
    
    assert result.command == "echo test"
    assert result.exit_code == 0
    assert result.output == "test"
    assert result.is_success() is True
