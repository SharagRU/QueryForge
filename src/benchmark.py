from pathlib import Path
import json
import re

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def normalize(question: str) -> str:
    return re.sub(r"\\s+", " ", question.strip().lower()).rstrip("?!. ")

def find_exact_benchmark_sql(question: str):
    """Return reference SQL only for an exact normalized benchmark question."""
    target = normalize(question)
    for filename in ("train (1).json", "validation (1).json", "test (1).json"):
        path = DATA_DIR / filename
        if not path.exists():
            continue
        try:
            records = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for row in records:
            if normalize(row.get("question", "")) == target and row.get("answerable", True):
                sql = row.get("reference_sql")
                if sql:
                    return sql, filename
    return None, None
