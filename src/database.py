from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "queryforge.db"

def execute_readonly(sql: str) -> dict:
    """Execute one read-only SQL statement against the local QueryForge DB."""
    if not DB_PATH.exists():
        return {"success": False, "error": f"Database not found: {DB_PATH}"}

    try:
        uri = DB_PATH.resolve().as_uri() + "?mode=ro"
        with sqlite3.connect(uri, uri=True) as conn:
            conn.execute("PRAGMA query_only = ON")
            cur = conn.cursor()
            cur.execute(sql)
            if cur.description is None:
                return {"success": False, "error": "Only SELECT queries are supported."}
            columns = [item[0] for item in cur.description]
            rows = cur.fetchall()
            return {"success": True, "columns": columns, "rows": rows}
    except Exception as exc:
        return {"success": False, "error": str(exc)}
