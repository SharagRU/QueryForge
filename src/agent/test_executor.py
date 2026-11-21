
from src.agent.sql_executor import run_query

tests = [
    "SELECT COUNT(*) AS total FROM customers;",
    "SELECT product_name, unit_price FROM products ORDER BY unit_price DESC LIMIT 3;",
    "DROP TABLE customers;",
    "SELECT * FROM orders; DROP TABLE orders;"
]

for query in tests:
    print("\n" + "=" * 60)
    print("QUERY:", query)

    result = run_query(query)
    print("RESULT:", result)
