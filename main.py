import os
import asyncio
import sys
import mimetypes
from astrbot.core.initial_loader import InitialLoader
from astrbot.core.db.factory import DatabaseFactory
from astrbot.core import logger, LogManager, LogBroker
from astrbot.core.config.default import VERSION
from astrbot.core.utils.io import download_dashboard, get_dashboard_version
import logging

# 添加父路径到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logo_tmpl = r"""
     ___           _______.___________..______      .______     ______   .___________.
    /   \         /       |           ||   _  \     |   _  \   /  __  \  |           |
   /  ^  \       |   (----`---|  |----`|  |_)  |    |  |_)  | |  |  |  | `---|  |----`
  /  /_\  \       \   \       |  |     |      /     |   _  <  |  |  |  |     |  |
 /  _____  \  .----)   |      |  |     |  |\  \----.|  |_)  | |  `--'  |     |  |
/__/     \__\ |_______/       |__|     | _| `._____||______/   \______/      |__|

"""


def check_env():
    if not (sys.version_info.major == 3 and sys.version_info.minor >= 10):
        logger.error("请使用 Python3.10+ 运行本项目。")
        exit()

    os.makedirs("data/config", exist_ok=True)
    os.makedirs("data/plugins", exist_ok=True)
    os.makedirs("data/temp", exist_ok=True)

    # 解决MIME类型问题
    mimetypes.add_type("text/javascript", ".js")
    mimetypes.add_type("text/javascript", ".mjs")
    mimetypes.add_type("application/json", ".json")


async def check_dashboard_files():
    """下载管理面板文件"""
    v = await get_dashboard_version()
    if v is not None:
        if v == f"v{VERSION}":
            logger.info("管理面板文件已是最新。")
        else:
            logger.warning("检测到管理面板有更新。可以使用 /dashboard_update 命令更新。")
        return

    logger.info("开始下载管理面板文件...如多次失败，请手动下载并解压到data目录")
    try:
        await download_dashboard()
    except Exception as e:
        logger.critical(f"下载管理面板失败: {e}")
        return
    logger.info("管理面板下载完成。")


if __name__ == "__main__":
    check_env()

    # 临时降低日志级别以避免错误
    logger.setLevel(logging.INFO)
    if hasattr(logger, 'handlers') and logger.handlers:
        for handler in logger.handlers:
            handler.setLevel(logging.INFO)

    # 启动日志代理
    log_broker = LogBroker()
    LogManager.set_queue_handler(logger, log_broker)

    # 检查管理面板
    asyncio.run(check_dashboard_files())

    # 初始化MySQL数据库（从工厂获取）
    try:
        db = DatabaseFactory.get_database("astrbot")
        logger.info("MySQL数据库初始化成功", extra={"plugin_tag": "core"})
    except Exception as e:
        # 添加plugin_tag参数
        logger.critical(f"数据库初始化失败: {e}", extra={"plugin_tag": "database"})
        exit(1)

    # 打印Logo
    logger.info(logo_tmpl)

    # 启动核心生命周期（传入数据库和日志代理）
    core_lifecycle = InitialLoader(db, log_broker)
    asyncio.run(core_lifecycle.start())