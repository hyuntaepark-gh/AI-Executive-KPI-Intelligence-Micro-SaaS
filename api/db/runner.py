from typing import List, Dict, Any
from sqlalchemy import text
from api.db.session import SessionLocal

def run_sql(sql: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        result = db.execute(text(sql), params)
        rows = result.mappings().all()
        return [dict(r) for r in rows]
    finally:
        db.close()
