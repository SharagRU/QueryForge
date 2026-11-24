import sqlparse
FORBIDDEN_KEYWORDS={"INSERT","UPDATE","DELETE","DROP","ALTER","CREATE","REPLACE","ATTACH","DETACH","PRAGMA","VACUUM","REINDEX","EXEC","EXECUTE"}
def validate_sql(query):
    if not query or not query.strip(): return False,"Empty SQL query."
    statements=[s for s in sqlparse.parse(query) if str(s).strip()]
    if len(statements)!=1: return False,"Only one SQL statement is allowed."
    statement=statements[0]
    first=statement.value.lstrip().upper()
    if not (first.startswith("SELECT") or first.startswith("WITH")): return False,"Only SELECT or read-only CTE queries are allowed."
    for token in statement.flatten():
        if token.ttype in sqlparse.tokens.Keyword and token.value.upper() in FORBIDDEN_KEYWORDS:
            return False,"Forbidden SQL keyword: "+token.value.upper()
    return True,"SQL validation successful."
