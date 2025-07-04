# astrbot/core/db/po.py
from typing import List, Dict, Any


# astrbot/core/db/po.py
class UserInfo:
    def __init__(
        self,
        id: int,
        uid: int,
        integral: int = 0,
        property: int = 0,
        honor: int = 0,
        fighting: int = 0,
        create_time: int = 0,
        update_time: int = 0,
        delete_time: int = 0,
    ):
        self.id = id
        self.uid = uid
        self.integral = integral
        self.property = property  # 注意: 避免使用Python关键字作为属性名
        self.honor = honor
        self.fighting = fighting
        self.create_time = create_time
        self.update_time = update_time
        self.delete_time = delete_time

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "uid": self.uid,
            "integral": self.integral,
            "property": self.property,
            "honor": self.honor,
            "fighting": self.fighting,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "delete_time": self.delete_time,
        }
class Platform:
    def __init__(self, name: str, count: int, timestamp: int):
        self.name = name
        self.count = count
        self.timestamp = timestamp


class Stats:
    def __init__(self, platform: List[Platform], plugin: List[Any], command: List[Any]):
        self.platform = platform
        self.plugin = plugin
        self.command = command


class LLMHistory:
    def __init__(self, provider_type: str, session_id: str, content: str):
        self.provider_type = provider_type
        self.session_id = session_id
        self.content = content


class ATRIVision:
    def __init__(
        self, 
        id: str, 
        url_or_path: str, 
        caption: str, 
        is_meme: bool, 
        keywords: str, 
        platform_name: str, 
        session_id: str, 
        sender_nickname: str, 
        timestamp: int
    ):
        self.id = id
        self.url_or_path = url_or_path
        self.caption = caption
        self.is_meme = is_meme
        self.keywords = keywords.split(",") if keywords else []
        self.platform_name = platform_name
        self.session_id = session_id
        self.sender_nickname = sender_nickname
        self.timestamp = timestamp


class Conversation:
    def __init__(
        self, 
        user_id: str, 
        cid: str, 
        history: str, 
        created_at: int, 
        updated_at: int, 
        title: str = None, 
        persona_id: str = None
    ):
        self.user_id = user_id
        self.cid = cid
        self.history = history
        self.created_at = created_at
        self.updated_at = updated_at
        self.title = title
        self.persona_id = persona_id