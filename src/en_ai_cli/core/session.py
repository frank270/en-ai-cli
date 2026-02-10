"""Session 管理器：追蹤和管理 AI 對話 Session"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

from en_ai_cli.core.config import ConfigManager


class Session:
    """Session 資料結構"""
    
    def __init__(
        self,
        session_id: str,
        created_at: datetime,
        message_count: int = 0,
        last_activity: Optional[datetime] = None,
    ):
        self.session_id = session_id
        self.created_at = created_at
        self.message_count = message_count
        self.last_activity = last_activity or created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "message_count": self.message_count,
            "last_activity": self.last_activity.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """從字典建立"""
        return cls(
            session_id=data["session_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            message_count=data.get("message_count", 0),
            last_activity=datetime.fromisoformat(data["last_activity"]),
        )


class SessionManager:
    """Session 管理器"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.max_messages = config.get("max_context_messages", 50)
        self.warning_threshold = config.get("context_warning_threshold", 0.8)
        
        # Session 資料存放路徑
        if config.is_workspace_mode():
            self.sessions_dir = Path.cwd() / ".en-ai" / "sessions"
        else:
            self.sessions_dir = Path.home() / ".en-ai" / "sessions"
        
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # 當前 session 檔案
        self.current_session_file = self.sessions_dir / "current.json"
        
        # 載入或建立 session
        self._current_session: Optional[Session] = None
    
    @property
    def current_session(self) -> Session:
        """取得當前 session（懶加載）"""
        if self._current_session is None:
            self._current_session = self._load_current_session()
        return self._current_session
    
    def _load_current_session(self) -> Session:
        """載入當前 session"""
        if self.current_session_file.exists():
            try:
                with open(self.current_session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return Session.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                # 檔案損壞，建立新 session
                pass
        
        # 建立新 session
        return self._create_new_session()
    
    def _create_new_session(self) -> Session:
        """建立新 session"""
        session_id = str(uuid.uuid4())[:8]  # 使用短 UUID
        session = Session(
            session_id=session_id,
            created_at=datetime.now(),
        )
        self._save_current_session(session)
        return session
    
    def _save_current_session(self, session: Session) -> None:
        """儲存當前 session"""
        with open(self.current_session_file, "w", encoding="utf-8") as f:
            json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
    
    def new_session(self) -> str:
        """
        建立新 session
        
        Returns:
            新 session 的 ID
        """
        self._current_session = self._create_new_session()
        return self._current_session.session_id
    
    def get_session_id(self) -> str:
        """取得當前 session ID"""
        return self.current_session.session_id
    
    def increment_message_count(self) -> int:
        """
        增加訊息計數
        
        Returns:
            更新後的訊息數量
        """
        session = self.current_session
        session.message_count += 1
        session.last_activity = datetime.now()
        self._save_current_session(session)
        return session.message_count
    
    def get_message_count(self) -> int:
        """取得當前 session 的訊息數量"""
        return self.current_session.message_count
    
    def should_warn_limit(self) -> bool:
        """
        判斷是否應該警告上限
        
        Returns:
            True 如果應該警告
        """
        count = self.get_message_count()
        threshold = int(self.max_messages * self.warning_threshold)
        return count >= threshold
    
    def is_at_limit(self) -> bool:
        """
        判斷是否已達上限
        
        Returns:
            True 如果已達上限
        """
        return self.get_message_count() >= self.max_messages
    
    def get_remaining_messages(self) -> int:
        """取得剩餘可用訊息數"""
        return max(0, self.max_messages - self.get_message_count())
    
    def get_usage_percentage(self) -> float:
        """取得使用百分比"""
        return (self.get_message_count() / self.max_messages) * 100
    
    def switch_session(self, session_id: str) -> bool:
        """
        切換到指定 session（預留功能）
        
        Args:
            session_id: Session ID
            
        Returns:
            True 如果切換成功
        """
        # TODO: 實作 session 切換邏輯
        # 需要從歷史中載入指定 session
        return False
    
    def list_sessions(self) -> List[Session]:
        """
        列出所有可用的 session（預留功能）
        
        Returns:
            Session 列表
        """
        # TODO: 實作 session 列表功能
        # 需要掃描 sessions 目錄並載入所有 session
        return [self.current_session]
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        取得當前 session 的詳細資訊
        
        Returns:
            Session 資訊字典
        """
        session = self.current_session
        return {
            "session_id": session.session_id,
            "created_at": session.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "message_count": session.message_count,
            "max_messages": self.max_messages,
            "remaining": self.get_remaining_messages(),
            "usage_percentage": f"{self.get_usage_percentage():.1f}%",
            "last_activity": session.last_activity.strftime("%Y-%m-%d %H:%M:%S"),
        }
