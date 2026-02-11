import os
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CFG = dict(
    host=os.getenv("DB_HOST", "postgres"),
    database=os.getenv("DB_NAME", "analytics"),
    user=os.getenv("DB_USER", "admin"),
    password=os.getenv("DB_PASSWORD", "admin123"),
)

def get_conn(dict_cursor: bool = False):
    if dict_cursor:
        return psycopg2.connect(**DB_CFG, cursor_factory=RealDictCursor)
    return psycopg2.connect(**DB_CFG)
