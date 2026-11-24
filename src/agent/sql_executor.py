from src.agent.sql_validator import validate_sql
from src.database.db import execute_sql
def run_query(query,database_path=None):
    ok,msg=validate_sql(query)
    if not ok: return {"success":False,"stage":"validation","error":msg}
    result=execute_sql(query,database_path=database_path)
    if not result["success"]: return {"success":False,"stage":"execution","error":result["error"]}
    return {"success":True,"stage":"completed","columns":result["columns"],"result":result["result"],"row_count":result["row_count"]}
