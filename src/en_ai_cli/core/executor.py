"""指令執行引擎：安全地執行系統指令"""

import subprocess
import shlex
from typing import Tuple, Optional
from dataclasses import dataclass

from en_ai_cli.core.platform import PlatformDetector, PlatformType


@dataclass
class ExecutionResult:
    """指令執行結果"""
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    command: str
    
    @property
    def output(self) -> str:
        """取得完整輸出（合併 stdout 和 stderr）"""
        output_parts = []
        if self.stdout:
            output_parts.append(self.stdout)
        if self.stderr:
            output_parts.append(f"[stderr]\n{self.stderr}")
        return "\n".join(output_parts) if output_parts else ""


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
    
    def execute(
        self,
        command: str,
        timeout: Optional[int] = 30,
        capture_output: bool = True,
    ) -> ExecutionResult:
        """
        執行指令
        
        Args:
            command: 要執行的指令
            timeout: 執行逾時時間（秒）
            capture_output: 是否捕獲輸出
            
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
                success=process.returncode == 0,
                exit_code=process.returncode,
                stdout=process.stdout if capture_output else "",
                stderr=process.stderr if capture_output else "",
                command=command,
            )
            
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"指令執行逾時（超過 {timeout} 秒）",
                command=command,
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"執行錯誤: {str(e)}",
                command=command,
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
                success=False,
                exit_code=-1,
                stdout="",
                stderr="指令不能為空",
                command=command,
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
