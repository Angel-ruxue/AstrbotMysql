# astrbot/core/db/__init__.py
from .base import BaseDatabase
from .mysql import MySQLDatabase
from .factory import DatabaseFactory  # 导入类
from .po import Platform, Stats, LLMHistory, ATRIVision, Conversation

# 提供兼容函数，指向类方法
def get_database(db_name: str = None) -> MySQLDatabase:
    return DatabaseFactory.get_database(db_name)

__all__ = [
    "BaseDatabase",
    "MySQLDatabase",
    "get_database",  # 导出兼容函数
    "Platform",
    "Stats",
    "LLMHistory",
    "ATRIVision",
    "Conversation"
]