"""對話歷程記錄器：記錄和管理 AI 對話歷程"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from enum import Enum


class MessageRole(str, Enum):
    """訊息角色"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message:
    """訊息資料結構"""
    
    def __init__(
        self,
        role: MessageRole,
        content: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """從字典建立"""
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
        )
    
    def to_jsonl(self) -> str:
        """轉換為 JSONL 格式（單行 JSON）"""
        return json.dumps(self.to_dict(), ensure_ascii=False)


class HistoryLogger:
    """對話歷程記錄器"""
    
    def __init__(self, sessions_dir: Path, session_id: str):
        """
        初始化歷程記錄器
        
        Args:
            sessions_dir: Sessions 目錄路徑
            session_id: Session ID
        """
        self.sessions_dir = sessions_dir
        self.session_id = session_id
        self.history_file = sessions_dir / f"{session_id}.jsonl"
        
        # 確保目錄存在
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
    
    def add_message(
        self,
        role: MessageRole,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        新增訊息到歷程
        
        Args:
            role: 訊息角色
            content: 訊息內容
            metadata: 附加資料（如指令執行結果）
        """
        message = Message(role, content, metadata=metadata)
        
        # 追加到 JSONL 檔案
        with open(self.history_file, "a", encoding="utf-8") as f:
            f.write(message.to_jsonl() + "\n")
    
    def add_user_message(self, content: str) -> None:
        """新增用戶訊息"""
        self.add_message(MessageRole.USER, content)
    
    def add_assistant_message(self, content: str) -> None:
        """新增 AI 助手訊息"""
        self.add_message(MessageRole.ASSISTANT, content)
    
    def add_system_message(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """新增系統訊息（如指令執行結果）"""
        self.add_message(MessageRole.SYSTEM, content, metadata)
    
    def get_messages(
        self,
        limit: Optional[int] = None,
        role_filter: Optional[MessageRole] = None,
    ) -> List[Message]:
        """
        取得 session 的訊息
        
        Args:
            limit: 限制返回的訊息數量（從最新開始）
            role_filter: 僅返回特定角色的訊息
            
        Returns:
            訊息列表
        """
        if not self.history_file.exists():
            return []
        
        messages = []
        with open(self.history_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    message = Message.from_dict(data)
                    
                    # 角色過濾
                    if role_filter and message.role != role_filter:
                        continue
                    
                    messages.append(message)
                except (json.JSONDecodeError, KeyError):
                    continue
        
        # 限制數量（取最新的）
        if limit and len(messages) > limit:
            messages = messages[-limit:]
        
        return messages
    
    def get_context_messages(self, limit: int = 10) -> List[Dict[str, str]]:
        """
        取得用於 AI API 的上下文訊息
        
        Args:
            limit: 最多返回的訊息數量
            
        Returns:
            適合 OpenRouter API 的訊息格式列表
        """
        messages = self.get_messages(limit=limit)
        
        # 轉換為 API 格式（僅包含 user 和 assistant）
        context = []
        for msg in messages:
            if msg.role in (MessageRole.USER, MessageRole.ASSISTANT):
                context.append({
                    "role": msg.role.value,
                    "content": msg.content,
                })
        
        return context
    
    def export_markdown(self) -> str:
        """
        匯出為 Markdown 格式
        
        Returns:
            Markdown 格式的對話記錄
        """
        messages = self.get_messages()
        
        if not messages:
            return "# AI 對話記錄\n\n無對話記錄。\n"
        
        # 生成 Markdown
        lines = [
            "# AI 對話記錄",
            "",
            f"**Session ID**: {self.session_id}",
            f"**建立時間**: {messages[0].timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**最後活動**: {messages[-1].timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**訊息總數**: {len(messages)}",
            "",
            "---",
            "",
            "## 對話內容",
            "",
        ]
        
        # 按時間分組（每個時間點一組）
        current_time = None
        for msg in messages:
            timestamp = msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            
            # 新的時間點
            if timestamp != current_time:
                current_time = timestamp
                lines.append(f"### {timestamp}")
                lines.append("")
            
            # 訊息內容
            role_display = {
                MessageRole.USER: "User",
                MessageRole.ASSISTANT: "Assistant",
                MessageRole.SYSTEM: "System",
            }[msg.role]
            
            lines.append(f"**{role_display}**:")
            
            # 如果是系統訊息且有指令執行結果
            if msg.role == MessageRole.SYSTEM and msg.metadata:
                lines.append(msg.content)
                if "command" in msg.metadata:
                    lines.append(f"```bash")
                    lines.append(msg.metadata["command"])
                    lines.append("```")
                if "output" in msg.metadata:
                    lines.append("```")
                    lines.append(msg.metadata["output"][:500])  # 限制輸出長度
                    if len(msg.metadata["output"]) > 500:
                        lines.append("... (輸出已截斷)")
                    lines.append("```")
            else:
                lines.append(msg.content)
            
            lines.append("")
        
        return "\n".join(lines)
    
    def save_markdown(self, output_path: Path) -> None:
        """
        儲存為 Markdown 檔案
        
        Args:
            output_path: 輸出檔案路徑
        """
        markdown = self.export_markdown()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    
    def clear(self) -> None:
        """清空歷程記錄"""
        if self.history_file.exists():
            self.history_file.unlink()
    
    def get_message_count(self) -> int:
        """取得訊息數量"""
        return len(self.get_messages())
