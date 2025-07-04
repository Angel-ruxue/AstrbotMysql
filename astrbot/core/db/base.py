# astrbot/core/db/base.py
from abc import ABC, abstractmethod
from typing import Tuple, List, Dict, Any
from .po import Platform, Stats, LLMHistory, ATRIVision, Conversation


class BaseDatabase(ABC):
    """数据库抽象基类，定义所有数据库实现必须遵循的接口"""

    @abstractmethod
    def insert_platform_metrics(self, metrics: dict):
        """插入平台指标数据"""
        pass

    @abstractmethod
    def insert_plugin_metrics(self, metrics: dict):
        """插入插件指标数据"""
        pass

    @abstractmethod
    def insert_command_metrics(self, metrics: dict):
        """插入命令指标数据"""
        pass

    @abstractmethod
    def insert_llm_metrics(self, metrics: dict):
        """插入LLM指标数据"""
        pass

    @abstractmethod
    def update_llm_history(self, session_id: str, content: str, provider_type: str):
        """更新或插入LLM历史记录"""
        pass

    @abstractmethod
    def get_llm_history(self, session_id: str = None, provider_type: str = None) -> Tuple:
        """获取LLM历史记录"""
        pass

    @abstractmethod
    def get_base_stats(self, offset_sec: int = 86400) -> Stats:
        """获取基础统计数据"""
        pass

    @abstractmethod
    def get_total_message_count(self) -> int:
        """获取总消息数"""
        pass

    @abstractmethod
    def get_grouped_base_stats(self, offset_sec: int = 86400) -> Stats:
        """获取分组的基础统计数据"""
        pass

    @abstractmethod
    def get_conversation_by_user_id(self, user_id: str, cid: str) -> Conversation:
        """获取用户对话"""
        pass

    @abstractmethod
    def new_conversation(self, user_id: str, cid: str):
        """创建新对话"""
        pass

    @abstractmethod
    def get_conversations(self, user_id: str) -> Tuple:
        """获取用户所有对话"""
        pass

    @abstractmethod
    def update_conversation(self, user_id: str, cid: str, history: str):
        """更新对话历史"""
        pass

    @abstractmethod
    def update_conversation_title(self, user_id: str, cid: str, title: str):
        """更新对话标题"""
        pass

    @abstractmethod
    def update_conversation_persona_id(self, user_id: str, cid: str, persona_id: str):
        """更新对话人设ID"""
        pass

    @abstractmethod
    def delete_conversation(self, user_id: str, cid: str):
        """删除对话"""
        pass

    @abstractmethod
    def insert_atri_vision_data(self, vision: ATRIVision):
        """插入ATRI Vision数据"""
        pass

    @abstractmethod
    def get_atri_vision_data(self) -> List[ATRIVision]:
        """获取所有ATRI Vision数据"""
        pass

    @abstractmethod
    def get_atri_vision_data_by_path_or_id(self, url_or_path: str, id: str) -> ATRIVision:
        """通过路径或ID获取ATRI Vision数据"""
        pass