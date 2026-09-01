import os
from contextlib import contextmanager

import pymysql
from flask import g, has_app_context
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


class HybridRow(dict):
    def __init__(self, dict_data):
        super().__init__(dict_data)
        self._values = list(dict_data.values())

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._values[key]
        return super().__getitem__(key)


class HybridCursor(pymysql.cursors.DictCursor):
    def fetchone(self):
        row = super().fetchone()
        return HybridRow(row) if row else row

    def fetchall(self):
        return [HybridRow(row) for row in super().fetchall()]


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)


class DBConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn
        self.closed = False

    def execute(self, query, params=None):
        cursor = self.conn.cursor()
        cursor.execute(query, params) if params is not None else cursor.execute(query)
        return cursor

    def commit(self):
        self.conn.commit()

    def close(self):
        if not self.closed:
            self.conn.close()
            self.closed = True

    def cursor(self):
        return self.conn.cursor()

    def rollback(self):
        self.conn.rollback()


def get_db_connection():
    db = pymysql.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DB', 'db_ais_systems'),
        cursorclass=HybridCursor,
        charset='utf8mb4',
        connect_timeout=5,
        read_timeout=15,
        write_timeout=15,
        autocommit=False,
    )
    return DBConnectionWrapper(db)


@contextmanager
def db_session():
    """Commit on success, rollback on failure, and always close."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_db():
    """Return the request-scoped connection, or a standalone connection outside Flask."""
    if has_app_context():
        if 'db' not in g or g.db.closed:
            g.db = get_db_connection()
        return g.db
    return get_db_connection()
