from .mysql import MySQLDatabase
import yaml
import os
import logging
from typing import Dict, Optional

logger = logging.getLogger("astrbot.database")

# 短级别名称映射
SHORT_LEVELS = {
    logging.DEBUG: 'DBUG',
    logging.INFO: 'INFO',
    logging.WARNING: 'WARN',
    logging.ERROR: 'ERR ',
    logging.CRITICAL: 'CRIT',
}

class LogFieldFilter:
    def filter(self, record):
        record.short_levelname = SHORT_LEVELS.get(record.levelno, record.levelname[:4])
        return True

if not any(isinstance(f, LogFieldFilter) for f in logger.filters):
    logger.addFilter(LogFieldFilter())

class DatabaseFactory:
    """数据库工厂，支持连接多个MySQL数据库"""
    _instances: Dict[str, MySQLDatabase] = {}
    _config: Dict = {}

    @classmethod
    def initialize(cls, config_path: str = None):
        print("当前工作目录:", os.getcwd())
        """初始化工厂，加载配置"""
        try:
            if config_path is None:
                # 默认从与当前文件同目录的 database.yaml 加载
                from pathlib import Path
                config_path = Path(__file__).parent / "database.yaml"

            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
                mysql_config = config.get('database', {}).get('mysql', {})

                required_keys = {"host", "port", "user", "password", "databases"}
                if not required_keys.issubset(mysql_config.keys()):
                    raise ValueError("配置文件缺少必要字段: host, port, user, password, databases")

                if not isinstance(mysql_config["databases"], list) or not mysql_config["databases"]:
                    raise ValueError("配置文件中的 databases 字段必须是非空列表")

                cls._config["mysql"] = mysql_config

            logger.info(
                f"数据库配置加载完成: {cls._config}",
                extra={"plugin_tag": "database"}
            )

        except Exception as e:
            logger.critical(
                f"数据库配置加载失败: {str(e)}",
                extra={"plugin_tag": "database"},
                exc_info=True
            )
            raise RuntimeError("数据库配置加载失败") from e

    @classmethod
    def get_database(cls, db_name: Optional[str] = None) -> MySQLDatabase:
        """获取指定名称的数据库实例"""
        if not cls._config:
            cls.initialize()

        if db_name is None:
            db_name = cls._config["mysql"]["databases"][0]
            logger.info(
                f"使用默认数据库: {db_name}",
                extra={"plugin_tag": "database"}
            )

        if db_name in cls._instances:
            return cls._instances[db_name]

        if db_name not in cls._config["mysql"]["databases"]:
            raise ValueError(
                f"数据库 '{db_name}' 未在配置中定义，可用数据库: {cls._config['mysql']['databases']}"
            )

        mysql_config = cls._config["mysql"]

        logger.info(
            f"创建数据库连接 - "
            f"名称: {db_name}, "
            f"主机: {mysql_config['host']}, "
            f"端口: {mysql_config['port']}, "
            f"用户: {mysql_config['user']}",
            extra={"plugin_tag": "database"}
        )

        try:
            db = MySQLDatabase(
                host=mysql_config["host"],
                port=mysql_config["port"],
                user=mysql_config["user"],
                password=mysql_config["password"],
                database=db_name
            )

            cls._instances[db_name] = db
            logger.info(
                f"成功创建数据库实例: {db_name}",
                extra={"plugin_tag": "database"}
            )
            return db
        except Exception as e:
            logger.critical(
                f"创建数据库实例失败: {db_name}, 错误: {str(e)}",
                extra={"plugin_tag": "database"},
                exc_info=True
            )
            raise RuntimeError(f"无法连接到数据库 '{db_name}'") from e

    @classmethod
    def get_main_database(cls) -> MySQLDatabase:
        """获取主数据库实例（默认第一个）"""
        return cls.get_database()

    @classmethod
    def get_all_databases(cls) -> Dict[str, MySQLDatabase]:
        """获取所有配置的数据库实例"""
        for db_name in cls._config["mysql"]["databases"]:
            cls.get_database(db_name)
        return cls._instances