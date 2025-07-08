from datetime import datetime
from typing import Callable, Optional
from astrbot.core.db.factory import DatabaseFactory
import json
import os
from typing import Optional

db = DatabaseFactory.get_database()


class Command:
    def __init__(self, trigger: str, description: str, action: Callable[[Optional[str]], str]):
        self.trigger = trigger.strip()
        self.description = description
        self.action = action  # 函数必须支持接收 text 参数

    def execute(self, text: Optional[str] = None) -> str:
        if callable(self.action):
            try:
                return self.action(text)
            except TypeError:
                return self.action()
        return "无可执行操作。"


# ===== 各命令函数 =====

def help_command(_: Optional[str] = None) -> str:
    return "可用命令：菜单, 你好, 时间, 接龙"


def hello_command(_: Optional[str] = None) -> str:
    return "你好！很高兴为你服务。"


def time_command(_: Optional[str] = None) -> str:
    return f"当前时间是：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


def integral_command(_: Optional[str] = None) -> str:
    """查询用户积分信息"""
    user_db = DatabaseFactory.get_database("user")
    user_info = user_db.get_user_info(1)  # 默认用户 ID 为 1，可替换

    if not user_info:
        return "用户ID 1 不存在"

    return (
        f"用户ID: {user_info['uid']}\n"
        f"积分: {user_info['integral']}\n"
        f"金币: {user_info['property']}\n"
        f"荣誉值: {user_info['honor']}\n"
        f"战斗力: {user_info['fighting']}"
    )

# 初始化成语列表，只加载一次
with open("chinese-xinhua/data/idiom.json", "r", encoding="utf-8") as f:
    idioms_data = json.load(f)

idiom_set = set(i["word"] for i in idioms_data)  # 成语快速查找用集合
idiom_map = {i["word"]: i for i in idioms_data}  # 成语详细信息


# 假设 idiom_set 和 idiom_map 是成语集合和详情字典
# 你需要维护一个 last_chengyu 变量，这里我们用全局变量演示
last_chengyu = None  # 你应该把它存储在更合理的位置，例如用户 session 中

def interface_command(text: Optional[str] = None) -> str:
    global last_chengyu

    if not text or text.strip() == "接龙":
        # 初始化接龙
        import random
        last_chengyu = random.choice(list(idiom_set))
        detail = idiom_map.get(last_chengyu, {})
        return (
            f"我们开始成语接龙吧，我先来一个：『{last_chengyu}』\n"
            f"拼音：{detail.get('pinyin', '')}\n"
            f"释义：{detail.get('explanation', '')}\n"
            f"轮到你了，请用 #{last_chengyu[-1]} 开头的成语接龙"
        )

    parts = text.strip().split()
    if len(parts) == 2:
        user_chengyu = parts[1]

        if user_chengyu not in idiom_set:
            return f"你接的是『{user_chengyu}』，但它似乎不是一个常见的成语 🤔，再试一次吧～"

        if not last_chengyu:
            return "还没开始接龙，请先输入 #接龙 来开始游戏～"

        if user_chengyu[0] != last_chengyu[-1]:
            return f"你接的是『{user_chengyu}』，但它应该以『{last_chengyu[-1]}』开头哦～再来一次吧！"

        # 合法接龙成功，更新 last_chengyu
        last_chengyu = user_chengyu
        detail = idiom_map.get(user_chengyu, {})
        return (
            f"你接的是『{user_chengyu}』，接得漂亮！\n"
            f"拼音：{detail.get('pinyin', '')}\n"
            f"释义：{detail.get('explanation', '')}\n"
            f"请继续用『{user_chengyu[-1]}』开头的成语接龙～"
        )

    return "格式错误，请使用：#接龙 或 #接龙 明察秋毫"



# ===== 注册命令表 =====
def load_all_commands():
    return [
        Command("菜单", "显示此帮助信息", help_command),
        Command("查看积分", "查看自己积分", integral_command),
        Command("你好", "打招呼", hello_command),
        Command("时间", "显示当前时间", time_command),
        Command("接龙", "成语接龙", interface_command),
    ]
