import os
import pytest
from pathlib import Path
from en_ai_cli.core.executor import CommandExecutor

def test_executor_cd_interception(tmp_path):
    """測試 cd 指令是否能正確攔截並改變 Python 進程目錄"""
    executor = CommandExecutor()
    original_cwd = os.getcwd()
    
    # 建立目標目錄
    target_dir = tmp_path / "test_cd_dir"
    target_dir.mkdir()
    
    try:
        # 執行 cd 指令
        result = executor.execute(f"cd {target_dir}")
        assert result.success
        assert os.getcwd() == str(target_dir)
        assert "已成功切換目錄" in result.output
    finally:
        # 恢復原本目錄
        os.chdir(original_cwd)

def test_path_safety_analysis():
    """測試路徑安全分析邏輯"""
    executor = CommandExecutor()
    
    # 測試向上溯源
    risky, msgs = executor.analyze_path_safety("rm -rf ../secret")
    assert risky
    assert any("父目錄" in m for m in msgs)
    
    # 測試敏感路徑
    risky, msgs = executor.analyze_path_safety("ls /etc/passwd")
    assert risky
    assert any("/etc" in m for m in msgs)
    
    # 測試安全指令
    risky, msgs = executor.analyze_path_safety("ls -la ./src")
    assert not risky
    assert len(msgs) == 0

def test_sensitive_path_filtering():
    """測試敏感路徑過濾是否精確（避免誤判普通字串）"""
    executor = CommandExecutor()
    
    # 這應該是安全的，因為不是以敏感路徑開頭的檔案
    risky, msgs = executor.analyze_path_safety("cat my_etc_backup.txt")
    assert not risky
    
    # 這應該風險
    risky, msgs = executor.analyze_path_safety("rm /var/log/syslog")
    assert risky
