import sqlite3
import os
from contextlib import contextmanager

try:
    from flask import g, has_app_context
except ImportError:
    has_app_context = lambda: False

def get_db_path():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sukabumi_flasher.db')

def get_db_connection(timeout=30.0):
    """
    Membuat koneksi SQLite yang thread-safe, anti-locked (timeout 30s), dan berkonfigurasi WAL.
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, timeout=timeout)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.execute('PRAGMA synchronous=NORMAL;')
    conn.execute('PRAGMA busy_timeout=30000;')  # Tunggu maksimal 30 detik jika ada lock thread lain
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def db_session(timeout=30.0):
    """
    Context manager aman untuk thread background, worker, & Telegram bot.
    Otomatis commit jika sukses, rollback jika error, dan SELALU close koneksi setelah selesai.
    """
    conn = get_db_connection(timeout=timeout)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_db():
    """
    Hybrid database accessor:
    - Jika di dalam siklus request Flask: gunakan g.db (ditutup otomatis oleh teardown_appcontext)
    - Jika di luar request Flask (misal di engine/background worker): kembalikan koneksi langsung ber-timeout
    """
    if has_app_context():
        if 'db' not in g:
            g.db = get_db_connection()
        return g.db
    else:
        return get_db_connection()
