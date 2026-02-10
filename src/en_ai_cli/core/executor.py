"""指令執行引擎：安全地執行系統指令"""

import subprocess
import shlex
from typing import Tuple, Optional
from dataclasses import dataclass

from en_ai_cli.core.platform import PlatformDetector, PlatformType


@dataclass
class ExecutionResult:
    """指令執行結果"""
    command: str
    exit_code: int
    output: str = ""
    error: str = ""
    
    # 向後相容的屬性
    @property
    def success(self) -> bool:
        """執行是否成功"""
        return self.exit_code == 0
    
    @property
    def stdout(self) -> str:
        """標準輸出（別名）"""
        return self.output
    
    @property
    def stderr(self) -> str:
        """標準錯誤（別名）"""
        return self.error
    
    def is_success(self) -> bool:
        """執行是否成功（方法形式）"""
        return self.exit_code == 0


class CommandExecutor:
    """指令執行引擎"""
    
    # 危險指令關鍵字（需要額外確認）
    DANGEROUS_COMMANDS = {
        "rm", "del", "rmdir", "format", "mkfs",
        "dd", "fdisk", "parted",
        "shutdown", "reboot", "poweroff",
        ">", ">>",  # 重定向（可能覆蓋檔案）
    }
    
    # 需要 sudo/管理員權限的指令前綴
    PRIVILEGE_COMMANDS = {"sudo", "su", "doas"}
    
    def __init__(self, platform: Optional[PlatformType] = None):
        """
        初始化指令執行引擎
        
        Args:
            platform: 平台類型（如果為 None，自動偵測）
        """
        self.platform = platform or PlatformDetector.detect()
    
    def is_dangerous(self, command: str) -> bool:
        """
        檢查指令是否危險
        
        Args:
            command: 指令字串
            
        Returns:
            True 如果指令可能很危險
        """
        command_lower = command.lower()
        return any(dangerous in command_lower for dangerous in self.DANGEROUS_COMMANDS)
    
    def requires_privilege(self, command: str) -> bool:
        """
        檢查指令是否需要特權
        
        Args:
            command: 指令字串
            
        Returns:
            True 如果需要 sudo 或管理員權限
        """
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return False
        
        first_cmd = cmd_parts[0].lower()
        return first_cmd in self.PRIVILEGE_COMMANDS
    
    def check_privilege(self, command: str) -> bool:
        """檢查指令是否需要特權（別名，向後相容）"""
        return self.requires_privilege(command)
    
    def execute(
        self,
        command: str,
        timeout: Optional[int] = 30,
        capture_output: bool = True,
        require_confirmation: bool = True,
    ) -> ExecutionResult:
        """
        執行指令
        
        Args:
            command: 要執行的指令
            timeout: 執行逾時時間（秒）
            capture_output: 是否捕獲輸出
            require_confirmation: 是否需要確認（保留參數，向後相容，實際確認由 UI 層處理）
            
        Returns:
            執行結果
        """
        try:
            # 根據平台設定 shell
            use_shell = True  # 在所有平台上使用 shell 模式以支援管道等功能
            
            # 執行指令
            process = subprocess.run(
                command,
                shell=use_shell,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",  # 處理編碼錯誤
            )
            
            return ExecutionResult(
                command=command,
                exit_code=process.returncode,
                output=process.stdout if capture_output else "",
                error=process.stderr if capture_output else "",
            )
            
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                command=command,
                exit_code=-1,
                output="",
                error=f"指令執行逾時（超過 {timeout} 秒）",
            )
            
        except Exception as e:
            return ExecutionResult(
                command=command,
                exit_code=-1,
                output="",
                error=f"執行錯誤: {str(e)}",
            )
    
    def execute_safe(
        self,
        command: str,
        timeout: Optional[int] = 30,
    ) -> ExecutionResult:
        """
        安全地執行指令（帶基本檢查）
        
        Args:
            command: 要執行的指令
            timeout: 執行逾時時間（秒）
            
        Returns:
            執行結果
        """
        # 檢查空指令
        if not command or not command.strip():
            return ExecutionResult(
                command=command,
                exit_code=-1,
                output="",
                error="指令不能為空",
            )
        
        # 檢查是否需要權限（僅警告，不阻止執行）
        if self.requires_privilege(command):
            # 這裡可以在實際執行前給出警告
            # 由 UI 層處理確認邏輯
            pass
        
        return self.execute(command, timeout=timeout)
    
    def adapt_command(self, command: str, target_platform: Optional[PlatformType] = None) -> str:
        """
        將指令轉換為目標平台格式
        
        Args:
            command: 原始指令
            target_platform: 目標平台（如果為 None，使用當前平台）
            
        Returns:
            轉換後的指令
        """
        target = target_platform or self.platform
        return PlatformDetector.adapt_command(command, target)
