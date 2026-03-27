import os
import sqlite3
from urllib.parse import urlparse

def get_conn(dict_cursor: bool = False):
    database_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")

    # SQLite
    if database_url.startswith("sqlite"):
        db_path = database_url.replace("sqlite:///", "", 1)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row if dict_cursor else None
        return conn

    # PostgreSQL
    import psycopg2
    from psycopg2.extras import RealDictCursor

    if dict_cursor:
        return psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    return psycopg2.connect(database_url)
