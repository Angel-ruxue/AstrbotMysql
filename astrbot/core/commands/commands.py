from datetime import datetime
from astrbot.core.db.factory import DatabaseFactory
db = DatabaseFactory.get_database()


class Command:
    def __init__(self, trigger, description, action):
        self.trigger = trigger.strip()
        self.description = description
        self.action = action

    @property
    def name(self):
        return self.trigger

    def execute(self):
        if self.action:
            return self.action()
        return "无可执行操作。"

def help_command():
    return "可用命令：菜单, 你好, 时间"

def hello_command():
    return "你好！很高兴为你服务。"

def time_command():
    return f"当前时间是：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


def integral_command(user_id: int) -> str:  # 返回类型应为str
    """查询用户积分信息"""
    # 获取数据库实例
    user_db = DatabaseFactory.get_database("user")

    # 获取用户信息
    user_info = user_db.get_user_info(user_id)

    if not user_info:
        return f"用户ID {user_id} 不存在"

    # 使用字典键访问替代属性访问
    return (
        f"用户ID: {user_info['uid']}\n"
        f"积分: {user_info['integral']}\n"
        f"金币: {user_info['property']}\n"
        f"荣誉值: {user_info['honor']}\n"
        f"战斗力: {user_info['fighting']}"
    )


def load_all_commands():
    return [
        Command("菜单", "显示此帮助信息", help_command),
        Command("查看积分", "查看自己积分", lambda: integral_command(1)),
        Command("你好", "打招呼", hello_command),
        Command("时间", "显示当前时间", time_command),
    ]
