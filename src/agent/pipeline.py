from src.agent.sql_generator import generate_sql
from src.agent.sql_executor import run_query
def ask_database(question: str,database_path=None,dynamic=False):
    if dynamic and database_path:
        from src.agent.dynamic_sql import generate_dynamic_sql
        gen=generate_dynamic_sql(question,database_path)
        if not gen.get("success"): return {"success":False,"stage":"generation","error":gen.get("error"),"generated_sql":gen.get("sql")}
        sql=gen["sql"]; method=gen.get("generation_method","schema_aware_llm")
    else:
        gen=generate_sql(question)
        if not gen["supported"]: return {"success":False,"stage":"generation","error":gen.get("error","Unsupported question")}
        sql=gen["sql"]; method="template_based"
    ex=run_query(sql,database_path=database_path)
    return {"success":ex["success"],"question":question,"generated_sql":sql,"generation_method":method,"stage":ex["stage"],
            "columns":ex.get("columns",[]),"result":ex.get("result",[]),"row_count":ex.get("row_count",0),"error":ex.get("error")}
