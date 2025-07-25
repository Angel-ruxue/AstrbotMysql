from datetime import datetime
from typing import Callable, Optional
from astrbot.core.db.factory import DatabaseFactory
import json
import pypinyin
import time

db = DatabaseFactory.get_database()


class Command:
    def __init__(self, trigger: str, description: str,
                 action: Callable[[Optional[str], Optional[str], Optional[str]], str]):
        self.trigger = trigger.strip()
        self.description = description
        self.action = action  # 函数支持接收 text, sender_qq, username

    def execute(self, text: Optional[str] = None, sender_qq: Optional[str] = None,
                username: Optional[str] = None) -> str:
        if callable(self.action):
            try:
                return self.action(text, sender_qq, username)
            except TypeError:
                try:
                    return self.action(text, sender_qq)  # 兼容只需要QQ号的命令
                except TypeError:
                    return self.action(text)  # 兼容旧命令
        return "无可执行操作。"


# ===== 各命令函数 =====

def help_command(_: Optional[str] = None, __: Optional[str] = None, ___: Optional[str] = None) -> str:
    return "可用命令：菜单, 你好, 时间, 接龙, 帮我接龙, 查看积分"


def hello_command(_: Optional[str] = None, sender_qq: Optional[str] = None, username: Optional[str] = None) -> str:
    name = username if username else sender_qq
    return f"你好，{name}！很高兴为你服务。"


def time_command(_: Optional[str] = None, __: Optional[str] = None, ___: Optional[str] = None) -> str:
    return f"当前时间是：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
def get_or_create_user(user_db, sender_qq: str, username: Optional[str] = None) -> int:
    import time

    # 先查UID
    uid = user_db.get_users(sender_qq)
    if uid:
        return uid

    # 不存在则创建新用户及用户信息
    now = int(time.time())
    try:
        uid = user_db.create_users({
            "qq_number": sender_qq,
            "user": sender_qq,
            "password": sender_qq,
            "name": username or f"user_{sender_qq}",
            "email": "",  # 不留空字符串
            "wechat_number": "",  # 不留空字符串
            "qqfc_number": 0,  # 默认整型
            "create_time": now,
            "update_time": now,
            "delete_time": 0,
        })
        if not uid:
            raise Exception("create_users failed to return valid uid")

        user_db.create_user_info({
            "uid": uid,
            "integral": 0,
            "property": 0,
            "honor": 0,
            "fighting": 0,
            "create_time": now,
            "update_time": now,
            "delete_time": 0,
        })
    except Exception as e:
        raise RuntimeError(f"创建新用户失败：{e}")

    return uid


def integral_command(_: Optional[str] = None, sender_qq: Optional[str] = None, username: Optional[str] = None) -> str:
    if not sender_qq:
        return "无法获取用户ID"

    user_db = DatabaseFactory.get_database("user")

    try:
        uid = get_or_create_user(user_db, sender_qq, username)
    except Exception as err:
        return str(err)

    # 第二步：再用 UID 查用户信息
    user_info = user_db.get_user_info(uid)
    if not user_info:
        return f"用户 {username or sender_qq} 不存在"

    return (
        f"用户：{username or sender_qq}\n"
        f"积分: {user_info['integral']}\n"
        f"金币: {user_info['property']}\n"
        f"荣誉值: {user_info['honor']}\n"
        f"战斗力: {user_info['fighting']}"
    )



# 初始化成语列表
with open("chinese-xinhua/data/idiom.json", "r", encoding="utf-8") as f:
    idioms_data = json.load(f)

idiom_set = set(i["word"] for i in idioms_data)
idiom_map = {i["word"]: i for i in idioms_data}

last_chengyu = None


def get_pinyin_first(word: str) -> str:
    return pypinyin.lazy_pinyin(word)[0] if word else ""


def get_pinyin_last(word: str) -> str:
    return pypinyin.lazy_pinyin(word)[-1] if word else ""

# 全局变量
last_chengyu = None
used_chengyu_set = set()  # 记录已使用成语

def interface_command(text: Optional[str] = None, sender_qq: Optional[str] = None, username: Optional[str] = None) -> str:
    global last_chengyu, used_chengyu_set

    if not text or text.strip() == "接龙":
        import random
        available = [c for c in idiom_set if len(c) == 4 and c not in used_chengyu_set]
        if not available:
            return "当前没有可用的四字成语可以开始游戏了～"
        last_chengyu = random.choice(available)
        used_chengyu_set = {last_chengyu}  # 初始化记录
        detail = idiom_map.get(last_chengyu, {})
        return (
            f"我们开始成语接龙吧，我先来一个：『{last_chengyu}』\n"
            f"拼音：{detail.get('pinyin', '')}\n"
            f"释义：{detail.get('explanation', '')}\n"
            f"轮到你了，请用拼音为 #{get_pinyin_last(last_chengyu)} 的字开头的四字成语接龙"
        )

    parts = text.strip().split()
    if len(parts) == 2:
        user_chengyu = parts[1]

        if len(user_chengyu) != 4:
            return f"你接的是『{user_chengyu}』，但它不是一个标准的四字成语，请重新输入～"

        if user_chengyu not in idiom_set:
            return f"你接的是『{user_chengyu}』，但它似乎不是一个常见的成语 🤔，再试一次吧～"

        if not last_chengyu:
            return "还没开始接龙，请先输入 #接龙 来开始游戏～"

        if user_chengyu in used_chengyu_set:
            return f"『{user_chengyu}』已经被用过啦，换一个成语试试吧～"

        last_py = get_pinyin_last(last_chengyu)
        user_py = get_pinyin_first(user_chengyu)

        if last_py != user_py:
            return (
                f"你接的是『{user_chengyu}』，但它的首字拼音是『{user_py}』，"
                f"应该以拼音为『{last_py}』的字开头哦～再来一次吧！"
            )

        # 查 uid
        user_db = DatabaseFactory.get_database("user")
        try:
            uid = get_or_create_user(user_db, sender_qq, username)
        except Exception as err:
            return str(err)

        # 成功接龙，更新全局状态
        last_chengyu = user_chengyu
        used_chengyu_set.add(user_chengyu)

        # 调用更新积分金币的方法
        try:
            user_db.add_user_info(uid, integral=1, property=10)
        except Exception as e:
            # 可以记录日志，或者忽略
            pass

        detail = idiom_map.get(user_chengyu, {})
        return (
            f"你接的是『{user_chengyu}』，接得漂亮！\n"
            f"拼音：{detail.get('pinyin', '')}\n"
            f"释义：{detail.get('explanation', '')}\n"
            f"{username or sender_qq}，成功接龙积分+1，金币+10！\n"
            f"请继续用拼音为『{get_pinyin_last(user_chengyu)}』的字开头的四字成语接龙～"
        )

    return "格式错误，请使用：# 接龙 或 # 接龙 明察秋毫"




def interface_help_command(_: Optional[str] = None, __: Optional[str] = None, ___: Optional[str] = None) -> str:
    global last_chengyu

    if not last_chengyu:
        return "游戏还没开始，请先输入 <font color=\"#FF0000\">#接龙</font> 来开始成语接龙～"

    last_py = get_pinyin_last(last_chengyu)

    for candidate in idiom_set:
        if get_pinyin_first(candidate) == last_py and candidate != last_chengyu:
            last_chengyu = candidate
            detail = idiom_map.get(candidate, {})
            return (
                f"我来帮你接一个：『{candidate}』\n"
                f"拼音：{detail.get('pinyin', '')}\n"
                f"释义：{detail.get('explanation', '')}\n"
                f"轮到你了，请接拼音为『{get_pinyin_last(candidate)}』的成语～"
            )

    last_chengyu = None
    return "我也接不上啦，游戏结束啦！要不要重新开始？输入 #接龙 吧～"


# ===== 注册命令表 =====
def load_all_commands():
    return [
        Command("菜单", "显示此帮助信息", help_command),
        Command("查看积分", "查看自己积分", integral_command),
        Command("你好", "打招呼", hello_command),
        Command("时间", "显示当前时间", time_command),
        Command("接龙", "开始成语接龙游戏", interface_command),
        Command("帮我接龙", "成语接龙", interface_help_command),
    ]