import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from app.models.schemas import ResearchOption

class SelectionService:
    def __init__(self, ttl_minutes: int = 30):
        """
        初始化选择服务

        Args:
            ttl_minutes: 会话存活时间（分钟）
        """
        self.user_sessions: Dict[str, dict] = {}
        self.ttl = timedelta(minutes=ttl_minutes)

    def create_session(self, research_options: List[ResearchOption]) -> str:
        """创建用户会话"""
        session_id = str(uuid.uuid4())
        self.user_sessions[session_id] = {
            'research_options': [opt.dict() for opt in research_options],
            'created_at': datetime.now()
        }
        self._cleanup_expired()
        return session_id

    def get_session(self, session_id: str) -> Optional[dict]:
        """获取会话数据"""
        if session_id in self.user_sessions:
            session = self.user_sessions[session_id]
            if datetime.now() - session['created_at'] < self.ttl:
                return session
            else:
                # 会话过期，删除
                del self.user_sessions[session_id]
        return None

    def validate_selection(self, session_id: str, selection_index: int) -> bool:
        """
        验证用户选择

        Args:
            session_id: 会话ID
            selection_index: 选择索引

        Returns:
            是否有效
        """
        session = self.get_session(session_id)
        if not session:
            return False

        research_options = session['research_options']
        return 0 <= selection_index < len(research_options)

    def get_research_options(self, session_id: str) -> Optional[List[ResearchOption]]:
        """获取会话中的调研选项"""
        session = self.get_session(session_id)
        if not session:
            return None

        return [ResearchOption(**opt) for opt in session['research_options']]

    def _cleanup_expired(self):
        """清理过期会话"""
        current_time = datetime.now()
        expired_keys = [
            key for key, session in self.user_sessions.items()
            if current_time - session['created_at'] >= self.ttl
        ]
        for key in expired_keys:
            del self.user_sessions[key]

    def cleanup_all(self):
        """清理所有会话（用于测试）"""
        self.user_sessions.clear()