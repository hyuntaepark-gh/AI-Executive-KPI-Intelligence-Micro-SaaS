import os
from urllib.parse import urlparse

def get_conn():
    database_url = os.getenv("DATABASE_URL")

    # SQLite
    if database_url.startswith("sqlite"):
        import sqlite3
        path = database_url.replace("sqlite:///", "")
        return sqlite3.connect(path)

    # Postgres
    import psycopg2
    return psycopg2.connect(database_url)
