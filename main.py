from src.agent import generate_sql, schema_text
from src.database import execute_readonly

def main():
    print("\\n" + "=" * 58)
    print(" QUERYFORGE — LOCAL SQL ANALYTICS AGENT")
    print("=" * 58)
    print("Database schema:")
    print(schema_text())
    print("\\nAsk a business question. Type 'exit' to quit.\\n")

    while True:
        question = input("QueryForge> ").strip()
        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break
        if not question:
            continue

        sql, method = generate_sql(question)
        if not sql:
            print("\\nI don't have a verified SQL mapping for that question yet.")
            print("Try an exact question from the benchmark, or add a supported rule.")
            print(f"Method: {method}\\n")
            continue

        print(f"\\nSQL ({method}):")
        print(sql)
        result = execute_readonly(sql)

        if not result["success"]:
            print("Execution error:", result["error"], "\\n")
            continue

        print("\\nResult:")
        print(" | ".join(result["columns"]))
        print("-" * 58)
        for row in result["rows"][:50]:
            print(" | ".join(str(value) for value in row))
        if len(result["rows"]) > 50:
            print(f"... and {len(result['rows']) - 50} more rows")
        print(f"\\nRows returned: {len(result['rows'])}\\n")

if __name__ == "__main__":
    main()
