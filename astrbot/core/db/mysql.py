import mysql.connector
import time
from typing import Tuple, List, Dict, Any
from .base import BaseDatabase
from .po import Platform, Stats, LLMHistory, ATRIVision, Conversation, UserInfo


class MySQLDatabase(BaseDatabase):
    def __init__(self, host: str, user: str, password: str, database: str, port: int = 3306) -> None:
        super().__init__()
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.conn = self._connect()
        self._initialize_tables()  # 初始化数据库表结构

    def _connect(self):
        """建立MySQL数据库连接"""
        try:
            return mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                connection_timeout=30
            )
        except mysql.connector.Error as e:
            raise ConnectionError(f"MySQL连接失败: {str(e)}")

    def _execute(self, query: str, params: tuple = None, commit: bool = False) -> Any:
        """执行SQL语句，支持参数化查询和事务提交"""
        cursor = self.conn.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(query, params or ())
            if commit:
                self.conn.commit()
                return cursor.rowcount
            return cursor
        except mysql.connector.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"SQL执行失败: {str(e)}") from e
        finally:
            cursor.close()

    def _initialize_tables(self):
        """初始化MySQL表结构，包含SQLite中所有表的迁移"""
        tables = [
            # 平台指标表（保留SQLite原表结构）
            """
                CREATE TABLE IF NOT EXISTS platform (
                name VARCHAR(32) NOT NULL,
                count INT NOT NULL,
                timestamp BIGINT NOT NULL,
                PRIMARY KEY (name, timestamp)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            """,
            # 其他表结构...（保持不变）
        ]
        for table in tables:
            self._execute(table, commit=True)

    # ------------------------- 指标数据操作 -------------------------
    def insert_platform_metrics(self, metrics: dict) -> None:
        """插入平台指标数据"""
        try:
            timestamp = int(time.time())
            for name, count in metrics.items():
                self._execute(
                    "INSERT INTO platform (name, count, timestamp) VALUES (%s, %s, %s)",
                    (name, count, timestamp),
                    commit=True
                )
        except Exception as e:
            print(f"插入平台指标失败: {str(e)}")

    def get_platform_metric(self):
        """查询平台指标中 count 的最大值"""
        try:
            cursor = self._execute(
                "SELECT name, count, timestamp FROM platform ORDER BY count DESC LIMIT 1"
            )
            row = cursor.fetchone()
            if row:
                return row  # 通常是一个字典，如 {'name': ..., 'count': ..., 'timestamp': ...}
            else:
                return None
        except Exception as e:
            print(f"查询平台指标失败: {str(e)}")
            return None

    def insert_plugin_metrics(self, metrics: dict) -> None:
        """插入插件指标数据"""
        cursor = None
        try:
            timestamp = int(time.time())
            for name, count in metrics.items():
                cursor = self._execute(
                    "INSERT INTO plugin (name, count, timestamp) VALUES (%s, %s, %s)",
                    (name, count, timestamp),
                    commit=True
                )
        except Exception as e:
            print(f"插入插件指标失败: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def insert_command_metrics(self, metrics: dict) -> None:
        """插入命令指标数据"""
        cursor = None
        try:
            timestamp = int(time.time())
            for name, count in metrics.items():
                cursor = self._execute(
                    "INSERT INTO command (name, count, timestamp) VALUES (%s, %s, %s)",
                    (name, count, timestamp),
                    commit=True
                )
        except Exception as e:
            print(f"插入命令指标失败: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def insert_llm_metrics(self, metrics: dict) -> None:
        """插入LLM指标数据"""
        cursor = None
        try:
            timestamp = int(time.time())
            for name, count in metrics.items():
                cursor = self._execute(
                    "INSERT INTO llm (name, count, timestamp) VALUES (%s, %s, %s)",
                    (name, count, timestamp),
                    commit=True
                )
        except Exception as e:
            print(f"插入LLM指标失败: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    # ------------------------- LLM历史操作 -------------------------
    def update_llm_history(self, session_id: str, content: str, provider_type: str) -> None:
        """更新或插入LLM历史记录（使用REPLACE实现UPSERT）"""
        cursor = None
        try:
            cursor = self._execute(
                "REPLACE INTO llm_history (provider_type, session_id, content) VALUES (%s, %s, %s)",
                (provider_type, session_id, content),
                commit=True
            )
        except Exception as e:
            print(f"更新LLM历史失败: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def get_llm_history(self, session_id: str = None, provider_type: str = None) -> List[LLMHistory]:
        """查询LLM历史记录"""
        cursor = None
        try:
            query = "SELECT * FROM llm_history"
            params = []
            conditions = []

            if session_id:
                conditions.append("session_id = %s")
                params.append(session_id)
            if provider_type:
                conditions.append("provider_type = %s")
                params.append(provider_type)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            cursor = self._execute(query, tuple(params))
            return [LLMHistory(**row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"查询LLM历史失败: {str(e)}")
            return []
        finally:
            if cursor:
                cursor.close()

    # ------------------------- 统计数据操作 -------------------------
    def get_base_stats(self, offset_sec: int = 86400) -> Stats:
        """获取指定时间范围内的基础统计数据"""
        cursor = None
        try:
            timestamp = int(time.time()) - offset_sec
            cursor = self._execute(
                "SELECT * FROM platform WHERE timestamp >= %s",
                (timestamp,)
            )
            platform = [Platform(**row) for row in cursor.fetchall()]
            return Stats(platform, [], [])
        except Exception as e:
            print(f"获取基础统计数据失败: {str(e)}")
            return Stats([], [], [])
        finally:
            if cursor:
                cursor.close()

    def get_total_message_count(self) -> int:
        """获取总消息数量"""
        cursor = None
        try:
            cursor = self._execute("SELECT SUM(count) FROM platform")
            result = cursor.fetchone()
            return result["SUM(count)"] if result else 0
        except Exception as e:
            print(f"获取总消息数失败: {str(e)}")
            return 0
        finally:
            if cursor:
                cursor.close()

    def get_grouped_base_stats(self, offset_sec: int = 86400) -> Stats:
        """获取分组聚合的基础统计数据"""
        cursor = None
        try:
            timestamp = int(time.time()) - offset_sec
            cursor = self._execute(
                "SELECT name, SUM(count) as total, MAX(timestamp) as latest "
                "FROM platform WHERE timestamp >= %s GROUP BY name",
                (timestamp,)
            )
            platform = [Platform(**row) for row in cursor.fetchall()]
            return Stats(platform, [], [])
        except Exception as e:
            print(f"获取分组统计数据失败: {str(e)}")
            return Stats([], [], [])
        finally:
            if cursor:
                cursor.close()

    # ------------------------- 对话数据操作 -------------------------
    def get_conversation_by_user_id(self, user_id: str, cid: str) -> Conversation:
        """根据用户ID和对话ID查询对话"""
        cursor = None
        try:
            cursor = self._execute(
                "SELECT * FROM webchat_conversation WHERE user_id = %s AND cid = %s",
                (user_id, cid)
            )
            result = cursor.fetchone()
            return Conversation(**result) if result else None
        except Exception as e:
            print(f"查询对话失败: {str(e)}")
            return None
        finally:
            if cursor:
                cursor.close()

    def new_conversation(self, user_id: str, cid: str) -> None:
        """创建新对话"""
        cursor = None
        try:
            timestamp = int(time.time())
            # 执行插入操作（有 commit=True，返回 rowcount，无需关闭游标）
            self._execute(
                "INSERT INTO webchat_conversation "
                "(user_id, cid, history, created_at, updated_at) "
                "VALUES (%s, %s, '[]', %s, %s)",
                (user_id, cid, timestamp, timestamp),
                commit=True
            )
        except Exception as e:
            print(f"创建对话失败: {str(e)}")
        finally:
            # 仅在 cursor 被赋值为游标对象时才关闭
            if cursor and hasattr(cursor, 'close'):
                cursor.close()

    def get_conversations(self, user_id: str) -> List[Conversation]:

        """获取用户的所有对话，按更新时间降序排列"""
        cursor = None
        try:
            cursor = self._execute(
                "SELECT cid, created_at, updated_at, title, persona_id "
                "FROM webchat_conversation WHERE user_id = %s ORDER BY updated_at DESC",
                (user_id,)
            )
            return [
                Conversation(
                    user_id=user_id,
                    cid=row["cid"],
                    history="[]",
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    title=row["title"],
                    persona_id=row["persona_id"]
                )
                for row in cursor.fetchall()
            ]
        except Exception as e:
            print(f"获取对话列表失败: {str(e)}")
            return []
        finally:
            if cursor:
                cursor.close()

    def update_conversation(self, user_id: str, cid: str, history: str) -> None:
        """更新对话内容和时间"""
        try:
            timestamp = int(time.time())
            self._execute(
                "UPDATE webchat_conversation "
                "SET history = %s, updated_at = %s "
                "WHERE user_id = %s AND cid = %s",
                (history, timestamp, user_id, cid),
                commit=True
            )
        except Exception as e:
            print(f"更新对话失败: {str(e)}")

    def update_conversation_title(self, user_id: str, cid: str, title: str) -> None:
        """更新对话标题"""
        cursor = None
        try:
            cursor = self._execute(
                "UPDATE webchat_conversation SET title = %s WHERE user_id = %s AND cid = %s",
                (title, user_id, cid),
                commit=True
            )
        except Exception as e:
            print(f"更新对话标题失败: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def update_conversation_persona_id(self, user_id: str, cid: str, persona_id: str) -> None:
        """更新对话角色ID"""
        cursor = None
        try:
            cursor = self._execute(
                "UPDATE webchat_conversation SET persona_id = %s WHERE user_id = %s AND cid = %s",
                (persona_id, user_id, cid),
                commit=True
            )
        except Exception as e:
            print(f"更新对话角色ID失败: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def delete_conversation(self, user_id: str, cid: str) -> None:
        try:
            self._execute(
                "DELETE FROM webchat_conversation WHERE user_id = %s AND cid = %s",
                (user_id, cid),
                commit=True
            )
        except Exception as e:
            print(f"删除对话失败: {str(e)}")

    # ------------------------- ATRI Vision数据操作 -------------------------
    def insert_atri_vision_data(self, vision: ATRIVision) -> None:
        """插入ATRI Vision数据"""
        cursor = None
        try:
            timestamp = int(time.time())
            keywords = ",".join(vision.keywords) if vision.keywords else ""
            cursor = self._execute(
                "INSERT INTO atri_vision "
                "(id, url_or_path, caption, is_meme, keywords, platform_name, session_id, sender_nickname, timestamp) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    vision.id,
                    vision.url_or_path,
                    vision.caption,
                    vision.is_meme,
                    keywords,
                    vision.platform_name,
                    vision.session_id,
                    vision.sender_nickname,
                    timestamp
                ),
                commit=True
            )
        except Exception as e:
            print(f"插入ATRI Vision数据失败: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def get_atri_vision_data(self) -> List[ATRIVision]:
        """获取所有ATRI Vision数据"""
        cursor = None
        try:
            cursor = self._execute("SELECT * FROM atri_vision")
            return [ATRIVision(**row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"获取ATRI Vision数据失败: {str(e)}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_atri_vision_data_by_path_or_id(self, url_or_path: str, id: str) -> ATRIVision:
        """根据路径或ID查询ATRI Vision数据"""
        cursor = None
        try:
            cursor = self._execute(
                "SELECT * FROM atri_vision WHERE url_or_path = %s OR id = %s",
                (url_or_path, id)
            )
            result = cursor.fetchone()
            return ATRIVision(**result) if result else None
        except Exception as e:
            print(f"查询ATRI Vision数据失败: {str(e)}")
            return None
        finally:
            if cursor:
                cursor.close()

    # ------------------------- 对话分页查询操作 -------------------------
    def get_all_conversations(
        self, page: int = 1, page_size: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """获取所有对话，支持分页，按更新时间降序排序"""
        cursor = None
        try:
            # 获取总记录数
            cursor = self._execute("SELECT COUNT(*) FROM webchat_conversation")
            total_count = cursor.fetchone()["COUNT(*)"]

            # 计算偏移量
            offset = (page - 1) * page_size

            # 获取分页数据
            cursor = self._execute(
                "SELECT user_id, cid, created_at, updated_at, title, persona_id "
                "FROM webchat_conversation "
                "ORDER BY updated_at DESC "
                "LIMIT %s OFFSET %s",
                (page_size, offset)
            )
            rows = cursor.fetchall()

            conversations = []
            for row in rows:
                user_id = row["user_id"] or ""
                cid = str(row["cid"]) if row["cid"] else "unknown"
                display_cid = cid[:8] if len(cid) >= 8 else cid
                conversations.append(
                    {
                        "user_id": user_id,
                        "cid": cid,
                        "title": row["title"] or f"对话 {display_cid}",
                        "persona_id": row["persona_id"] or "",
                        "created_at": row["created_at"] or 0,
                        "updated_at": row["updated_at"] or 0,
                    }
                )
            return conversations, total_count
        except Exception as e:
            print(f"查询对话列表失败: {str(e)}")
            return [], 0
        finally:
            if cursor:
                cursor.close()

    def get_filtered_conversations(
            self,
            page: int = 1,
            page_size: int = 20,
            platforms: List[str] = None,
            message_types: List[str] = None,
            search_query: str = None,
            exclude_ids: List[str] = None,
            exclude_platforms: List[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """获取筛选后的对话列表，支持多条件过滤"""
        cursor = None
        try:
            where_clauses = []
            params = []

            # 平台筛选（user_id格式为platform:user）
            if platforms and len(platforms) > 0:
                platform_conditions = [f"user_id LIKE '{platform}:%'" for platform in platforms]
                where_clauses.append("(" + " OR ".join(platform_conditions) + ")")

            # 消息类型筛选
            if message_types and len(message_types) > 0:
                msg_type_conditions = [f"user_id LIKE '%:{msg_type}:%'" for msg_type in message_types]
                where_clauses.append("(" + " OR ".join(msg_type_conditions) + ")")

            # 搜索关键词（支持标题/用户ID/对话ID/历史内容）
            if search_query:
                escaped_query = search_query.encode("unicode_escape").decode("utf-8")
                like_pattern = f"%{escaped_query}%"
                where_clauses.append("(title LIKE %s OR user_id LIKE %s OR cid LIKE %s OR history LIKE %s)")
                params.extend([like_pattern] * 4)

            # 排除特定用户ID
            if exclude_ids and len(exclude_ids) > 0:
                exclude_conditions = [f"user_id NOT LIKE '{exclude_id}%'" for exclude_id in exclude_ids]
                where_clauses.append("(" + " AND ".join(exclude_conditions) + ")")

            # 排除特定平台
            if exclude_platforms and len(exclude_platforms) > 0:
                exclude_platform_conditions = [f"user_id NOT LIKE '{platform}:%'" for platform in exclude_platforms]
                where_clauses.append("(" + " AND ".join(exclude_platform_conditions) + ")")

            # 构建完整查询
            where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
            count_sql = f"SELECT COUNT(*) FROM webchat_conversation{where_sql}"
            offset = (page - 1) * page_size
            data_sql = f"""
                SELECT user_id, cid, created_at, updated_at, title, persona_id
                FROM webchat_conversation
                {where_sql}
                ORDER BY updated_at DESC
                LIMIT %s OFFSET %s
            """

            # 执行计数查询
            cursor = self._execute(count_sql, tuple(params))
            result = cursor.fetchone()
            total_count = result["COUNT(*)"] if result else 0

            # 执行数据查询
            query_params = params + [page_size, offset]
            cursor = self._execute(data_sql, tuple(query_params))
            rows = cursor.fetchall()

            conversations = []
            for row in rows:
                user_id = row["user_id"] or ""
                cid = str(row["cid"]) if row["cid"] else "unknown"
                display_cid = cid[:8] if len(cid) >= 8 else cid
                conversations.append(
                    {
                        "user_id": user_id,
                        "cid": cid,
                        "title": row["title"] or f"对话 {display_cid}",
                        "persona_id": row["persona_id"] or "",
                        "created_at": row["created_at"] or 0,
                        "updated_at": row["updated_at"] or 0,
                    }
                )
            return conversations, total_count

        except Exception as e:
            print(f"筛选对话列表失败: {str(e)}")
            return [], 0

        finally:
            if cursor:
                cursor.close()



# ------------------------- 对话分页查询操作 -------------------------


    # 方案2：完全省略类型提示（适用于 Python 2 或不使用类型提示的环境）
    def get_user_info(self, user_id):
        """获取用户信息"""
        cursor = None
        try:
            cursor = self._execute(
                "SELECT uid, integral, property, honor, fighting, create_time, update_time, delete_time "
                "FROM userinfo WHERE uid = %s AND delete_time = 0",
                (user_id,)
            )
            result = cursor.fetchone()
            if result:
                # 确保所有字段存在且类型正确（处理可能的NULL值）
                result['uid'] = int(result.get('uid', 0))
                result['integral'] = int(result.get('integral', 0))
                result['property'] = int(result.get('property', 0))
                result['honor'] = int(result.get('honor', 0))
                result['fighting'] = int(result.get('fighting', 0))
                result['create_time'] = int(result.get('create_time', 0))
                result['update_time'] = int(result.get('update_time', 0))
                result['delete_time'] = int(result.get('delete_time', 0))
            return result or {}
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            return {}
        finally:
            if cursor:
                cursor.close()

    def get_users(self, qq_number: int) -> int | None:
        cursor = None
        try:
            cursor = self._execute(
                "SELECT id FROM users WHERE qq_number = %s AND delete_time = 0 LIMIT 1",
                (qq_number,)
            )
            result = cursor.fetchone()
            if result:
                return int(result.get('id', 0))
            return None
        except Exception as e:
            print(f"查询用户ID失败: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def create_users(self, user_data: dict) -> int:
        sql = """
        INSERT INTO users
        (qq_number, user, create_time, update_time, delete_time, name, password, email, wechat_number, qqfc_number)
        VALUES
        (%(qq_number)s, %(user)s, %(create_time)s, %(update_time)s, %(delete_time)s, %(name)s, %(password)s, %(email)s, %(wechat_number)s, %(qqfc_number)s)
        """

        print("[SQL DEBUG] Running SQL:", sql)
        print("[SQL DEBUG] With params:", user_data)
        with self.conn.cursor() as cursor:
            cursor.execute(sql, user_data)
            self.conn.commit()
            return cursor.lastrowid

    def create_user_info(self, info_data: dict) -> None:
        sql = """
        INSERT INTO userinfo
        (uid, integral, property, honor, fighting, create_time, update_time, delete_time)
        VALUES
        (%(uid)s, %(integral)s, %(property)s, %(honor)s, %(fighting)s, %(create_time)s, %(update_time)s, %(delete_time)s)
        """
        with self.conn.cursor() as cursor:
            cursor.execute(sql, info_data)
            self.conn.commit()

    def add_user_info(self, uid: int, integral=0, property=0, honor=0, fighting=0) -> None:
        sql = """
        UPDATE userinfo
        SET
            integral = integral + %(integral)s,
            property = property + %(property)s,
            honor = honor + %(honor)s,
            fighting = fighting + %(fighting)s,
            update_time = %(update_time)s
        WHERE uid = %(uid)s
        """
        params = {
            "uid": uid,
            "integral": integral,
            "property": property,
            "honor": honor,
            "fighting": fighting,
            "update_time": int(time.time())
        }
        with self.conn.cursor() as cursor:
            cursor.execute(sql, params)
            self.conn.commit()
