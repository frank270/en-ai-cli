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
    
    @property
    def id(self) -> str:
        """session_id 的別名（向後相容）"""
        return self.session_id
    
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
    def current_session(self) -> Optional[Session]:
        """取得當前 session（懶加載）"""
        if self._current_session is None:
            # 如果 current.json 不存在，返回 None（無活躍 session）
            if not self.current_session_file.exists():
                return None
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
        # 同時存為當前 session 和獨立檔案
        self._save_current_session(session)
        self._save_session_file(session)
        return session
    
    def _save_current_session(self, session: Session) -> None:
        """儲存當前 session"""
        with open(self.current_session_file, "w", encoding="utf-8") as f:
            json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
    
    def _save_session(self, session: Session) -> None:
        """儲存 session（通用方法，向後相容）"""
        self._save_current_session(session)
        self._save_session_file(session)
    
    def _save_session_file(self, session: Session) -> None:
        """儲存 session 到獨立檔案"""
        session_file = self.sessions_dir / f"{session.session_id}.json"
        with open(session_file, "w", encoding="utf-8") as f:
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
        # 同時更新兩個檔案
        self._save_current_session(session)
        self._save_session_file(session)
        return session.message_count
    
    def get_message_count(self) -> int:
        """取得當前 session 的訊息數量"""
        session = self.current_session
        return session.message_count if session else 0
    
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
    
    def is_limit_reached(self) -> bool:
        """判斷是否已達上限（別名，向後相容）"""
        return self.is_at_limit()
    
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
        列出所有可用的 session
        
        Returns:
            Session 列表
        """
        sessions = []
        
        # 掃描 sessions 目錄
        if not self.sessions_dir.exists():
            return sessions
        
        for session_file in self.sessions_dir.glob("*.json"):
            # 跳過 current.json
            if session_file.name == "current.json":
                continue
            
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    session = Session.from_dict(data)
                    sessions.append(session)
            except (json.JSONDecodeError, KeyError):
                continue
        
        # 按建立時間排序（最新在前）
        sessions.sort(key=lambda s: s.created_at, reverse=True)
        
        return sessions
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        取得當前 session 的詳細資訊
        
        Returns:
            Session 資訊字典
        """
        session = self.current_session
        if not session:
            return {}
        
        return {
            "session_id": session.session_id,
            "created_at": session.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "message_count": session.message_count,
            "max_messages": self.max_messages,
            "remaining": self.get_remaining_messages(),
            "usage_percentage": round(self.get_usage_percentage(), 1),  # 返回數字而非字串
            "last_activity": session.last_activity.strftime("%Y-%m-%d %H:%M:%S"),
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """取得統計資訊（別名，向後相容）"""
        return self.get_session_info()
    
    def load_session(self, session_id: str) -> Optional[Session]:
        """
        載入指定 session
        
        Args:
            session_id: Session ID
            
        Returns:
            Session 物件，如果不存在則返回 None
        """
        session_file = self.sessions_dir / f"{session_id}.json"
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return Session.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """
        刪除指定 session
        
        Args:
            session_id: Session ID
            
        Returns:
            True 如果刪除成功
        """
        session_file = self.sessions_dir / f"{session_id}.json"
        history_file = self.sessions_dir / f"{session_id}.jsonl"
        
        success = False
        
        # 刪除 session 檔案
        if session_file.exists():
            session_file.unlink()
            success = True
        
        # 刪除歷史檔案
        if history_file.exists():
            history_file.unlink()
        
        # 如果刪除的是當前 session，清除快取
        if self._current_session and self._current_session.session_id == session_id:
            self._current_session = None
            if self.current_session_file.exists():
                self.current_session_file.unlink()
        
        return success
