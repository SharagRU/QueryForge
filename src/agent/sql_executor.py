
from src.agent.sql_validator import validate_sql
from src.database.db import execute_sql


def run_query(query: str):
    # Layer 1: Validate SQL
    valid, message = validate_sql(query)

    if not valid:
        return {
            "success": False,
            "stage": "validation",
            "error": message
        }

    # Layer 2: Execute using the existing read-only database connection
    result = execute_sql(query)

    if not result["success"]:
        return {
            "success": False,
            "stage": "execution",
            "error": result["error"]
        }

    return {
        "success": True,
        "stage": "completed",
        "columns": result["columns"],
        "result": result["result"],
        "row_count": result["row_count"]
    }
