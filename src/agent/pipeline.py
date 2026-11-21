
from src.agent.sql_generator import generate_sql
from src.agent.sql_executor import run_query


def ask_database(question: str):
    # Step 1: Generate SQL
    generated = generate_sql(question)

    if not generated["supported"]:
        return {
            "success": False,
            "stage": "generation",
            "error": generated.get("error", "Unsupported question.")
        }

    # Step 2: Validate and execute SQL
    execution = run_query(generated["sql"])

    return {
        "success": execution["success"],
        "question": question,
        "generated_sql": generated["sql"],
        "stage": execution["stage"],
        "columns": execution.get("columns", []),
        "result": execution.get("result", []),
        "row_count": execution.get("row_count", 0),
        "error": execution.get("error")
    }


if __name__ == "__main__":
    questions = [
        "Top 5 products by completed revenue",
        "Top 10 cities by refunded order count",
        "Top 12 products by units sold",
        "Top 7 customers by average order value",
        "Top 8 months by completed revenue"
    ]

    for question in questions:
        response = ask_database(question)

        print("\n" + "=" * 70)
        print("QUESTION:", question)
        print("SUCCESS:", response["success"])
        print("SQL:\n", response["generated_sql"] if response["success"] else response["error"])
        print("ROWS:", response["row_count"])
        print("RESULT:", response["result"][:5])
