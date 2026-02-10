"""雙層配置管理系統：支援 workspace 和 global 層級"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from enum import Enum


class ConfigScope(str, Enum):
    """配置作用域"""
    WORKSPACE = "workspace"
    GLOBAL = "global"


class ConfigManager:
    """配置管理器：處理雙層配置（workspace 優先，fallback 到 global）"""

    def __init__(self, workspace_path: Optional[Path] = None):
        """
        初始化配置管理器
        
        Args:
            workspace_path: Workspace 路徑，如果為 None 則使用當前目錄
        """
        self.global_path = Path.home() / ".en-ai" / "config.json"
        self.workspace_path = (workspace_path or Path.cwd()) / ".en-ai" / "config.json"
        
        # 確保目錄存在
        self.global_path.parent.mkdir(parents=True, exist_ok=True)

    def get(self, key: str, default: Any = None) -> Any:
        """
        取得配置值（優先 workspace，fallback 到 global）
        
        Args:
            key: 配置鍵名
            default: 預設值
            
        Returns:
            配置值
        """
        # 優先讀取 workspace 配置
        if self.workspace_path.exists():
            workspace_config = self._load_config(self.workspace_path)
            if key in workspace_config:
                return workspace_config[key]
        
        # Fallback 到 global 配置
        if self.global_path.exists():
            global_config = self._load_config(self.global_path)
            return global_config.get(key, default)
        
        return default

    def set(self, key: str, value: Any, scope: ConfigScope = ConfigScope.WORKSPACE) -> None:
        """
        設定配置值
        
        Args:
            key: 配置鍵名
            value: 配置值
            scope: 作用域（workspace 或 global）
        """
        config_path = self.workspace_path if scope == ConfigScope.WORKSPACE else self.global_path
        
        # 確保目錄存在
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 讀取現有配置
        config = self._load_config(config_path) if config_path.exists() else {}
        
        # 更新配置
        config[key] = value
        
        # 寫入檔案
        self._save_config(config_path, config)

    def list_all(self) -> Dict[str, Dict[str, Any]]:
        """
        列出所有配置（分別顯示 workspace 和 global）
        
        Returns:
            包含 workspace 和 global 配置的字典
        """
        result = {
            "workspace": {},
            "global": {}
        }
        
        if self.workspace_path.exists():
            result["workspace"] = self._load_config(self.workspace_path)
        
        if self.global_path.exists():
            result["global"] = self._load_config(self.global_path)
        
        return result

    def is_workspace_mode(self) -> bool:
        """
        判斷當前是否在 workspace 模式（是否存在 workspace 配置）
        
        Returns:
            True 如果存在 workspace 配置
        """
        return self.workspace_path.exists()

    def init_config(self, scope: ConfigScope, initial_config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化配置檔案
        
        Args:
            scope: 作用域
            initial_config: 初始配置值（可選）
        """
        config_path = self.workspace_path if scope == ConfigScope.WORKSPACE else self.global_path
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not config_path.exists():
            default_config = initial_config or self._get_default_config()
            self._save_config(config_path, default_config)

    def _load_config(self, path: Path) -> Dict[str, Any]:
        """載入配置檔案"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_config(self, path: Path, config: Dict[str, Any]) -> None:
        """儲存配置檔案"""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def _get_default_config(self) -> Dict[str, Any]:
        """取得預設配置"""
        return {
            # Provider 設定
            "preferred_provider": "ollama",  # 預設優先使用 ollama
            
            # Ollama 設定
            "ollama_endpoint": "http://localhost:11434",
            "ollama_default_model": "qwen2.5-coder:3b",
            
            # OpenRouter 設定
            "prefer_free_models": True,
            "fallback_to_paid": False,
            
            # 一般設定
            "color_mode": True,
            "auto_save_history": True,
            "max_context_messages": 50,
            "model_cache_ttl": 3600,
        }
