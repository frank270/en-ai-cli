"""測試平台偵測模組"""

import pytest
from en_ai_cli.core.platform import PlatformDetector, PlatformType


def test_detect_platform():
    """測試平台偵測"""
    platform = PlatformDetector.detect()
    assert platform in [PlatformType.UNIX, PlatformType.POWERSHELL, PlatformType.CMD]


def test_get_shell_name():
    """測試取得 shell 名稱"""
    shell = PlatformDetector.get_shell_name()
    assert isinstance(shell, str)
    assert len(shell) > 0


def test_adapt_command_unix():
    """測試 Unix 指令轉換"""
    cmd = PlatformDetector.adapt_command("dir", PlatformType.UNIX)
    assert "ls" in cmd


def test_adapt_command_cmd():
    """測試 CMD 指令轉換"""
    cmd = PlatformDetector.adapt_command("ls", PlatformType.CMD)
    assert "dir" in cmd


def test_get_path_separator():
    """測試取得路徑分隔符"""
    sep = PlatformDetector.get_path_separator()
    assert sep in [":", ";"]


def test_normalize_path():
    """測試路徑正規化"""
    path = PlatformDetector.normalize_path("path/to/file")
    assert isinstance(path, str)
