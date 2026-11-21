
import sqlparse


FORBIDDEN_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "REPLACE",
    "ATTACH",
    "DETACH",
    "PRAGMA",
    "VACUUM",
    "REINDEX"
}


def validate_sql(query: str):
    if not query or not query.strip():
        return False, "Empty SQL query."

    statements = [
        statement
        for statement in sqlparse.parse(query)
        if str(statement).strip()
    ]

    if len(statements) != 1:
        return False, "Only one SQL statement is allowed."

    statement = statements[0]
    first_keyword = statement.get_type()

    if first_keyword != "SELECT":
        return False, "Only SELECT queries are allowed."

    for token in statement.flatten():
        if token.ttype in sqlparse.tokens.Keyword:
            keyword = token.value.upper()

            if keyword in FORBIDDEN_KEYWORDS:
                return False, f"Forbidden SQL keyword: {keyword}"

    return True, "SQL validation successful."
