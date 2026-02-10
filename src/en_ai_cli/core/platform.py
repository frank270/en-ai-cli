"""跨平台環境偵測與指令轉換"""

import os
import platform
import subprocess
from enum import Enum
from typing import Optional


class PlatformType(str, Enum):
    """平台類型"""
    UNIX = "unix"           # Linux, macOS, Unix-like
    POWERSHELL = "powershell"  # Windows PowerShell
    CMD = "cmd"             # Windows Command Prompt


class PlatformDetector:
    """平台偵測器：自動判斷當前執行環境"""

    @staticmethod
    def detect() -> PlatformType:
        """
        偵測當前平台類型
        
        Returns:
            平台類型（unix, powershell, cmd）
        """
        system = platform.system()
        
        # Unix-like 系統（Linux, macOS, BSD 等）
        if system in ("Linux", "Darwin", "FreeBSD", "OpenBSD"):
            return PlatformType.UNIX
        
        # Windows 系統
        if system == "Windows":
            # 檢查是否在 PowerShell 環境中
            if PlatformDetector._is_powershell():
                return PlatformType.POWERSHELL
            else:
                return PlatformType.CMD
        
        # 預設為 Unix（大多數情況下較安全）
        return PlatformType.UNIX

    @staticmethod
    def _is_powershell() -> bool:
        """檢查是否在 PowerShell 環境中"""
        # 檢查環境變數
        ps_version = os.environ.get("PSModulePath")
        if ps_version:
            return True
        
        # 檢查 SHELL 環境變數
        shell = os.environ.get("SHELL", "")
        if "pwsh" in shell.lower() or "powershell" in shell.lower():
            return True
        
        return False

    @staticmethod
    def get_shell_name() -> str:
        """
        取得當前 shell 名稱
        
        Returns:
            Shell 名稱（fish, bash, zsh, powershell, cmd 等）
        """
        # Unix-like 系統
        if platform.system() in ("Linux", "Darwin"):
            shell_path = os.environ.get("SHELL", "")
            if shell_path:
                return os.path.basename(shell_path)
        
        # Windows 系統
        if PlatformDetector._is_powershell():
            return "powershell"
        
        return "cmd" if platform.system() == "Windows" else "sh"

    @staticmethod
    def adapt_command(command: str, target_platform: Optional[PlatformType] = None) -> str:
        """
        將指令轉換為目標平台格式
        
        Args:
            command: 原始指令
            target_platform: 目標平台（如果為 None，使用當前平台）
            
        Returns:
            轉換後的指令
        """
        if target_platform is None:
            target_platform = PlatformDetector.detect()
        
        # 簡單的指令轉換對照表
        conversions = {
            PlatformType.UNIX: {
                "dir": "ls -la",
                "cls": "clear",
                "type": "cat",
                "del": "rm",
                "copy": "cp",
                "move": "mv",
            },
            PlatformType.POWERSHELL: {
                "ls": "Get-ChildItem",
                "cat": "Get-Content",
                "rm": "Remove-Item",
                "cp": "Copy-Item",
                "mv": "Move-Item",
                "clear": "Clear-Host",
            },
            PlatformType.CMD: {
                "ls": "dir",
                "cat": "type",
                "rm": "del",
                "cp": "copy",
                "mv": "move",
                "clear": "cls",
            }
        }
        
        # 取得第一個單詞（指令名稱）
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return command
        
        cmd_name = cmd_parts[0].lower()
        
        # 查找轉換
        conversion_map = conversions.get(target_platform, {})
        if cmd_name in conversion_map:
            return conversion_map[cmd_name] + " " + " ".join(cmd_parts[1:])
        
        return command

    @staticmethod
    def get_path_separator() -> str:
        """
        取得路徑分隔符
        
        Returns:
            路徑分隔符（Unix: ':', Windows: ';'）
        """
        return ";" if platform.system() == "Windows" else ":"

    @staticmethod
    def normalize_path(path: str) -> str:
        """
        正規化路徑格式
        
        Args:
            path: 原始路徑
            
        Returns:
            正規化後的路徑
        """
        return os.path.normpath(path)
