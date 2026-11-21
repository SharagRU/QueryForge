
from src.agent.sql_validator import validate_sql

test_cases = [
    ("SELECT * FROM customers;", True),
    ("SELECT city, COUNT(*) FROM customers GROUP BY city;", True),
    ("DROP TABLE customers;", False),
    ("DELETE FROM orders;", False),
    ("UPDATE customers SET city = 'Delhi';", False),
    ("SELECT * FROM orders; DROP TABLE orders;", False),
    ("", False),
]

print("=" * 60)
print("QUERYFORGE SQL VALIDATOR TEST")
print("=" * 60)

passed = 0

for query, expected in test_cases:
    valid, message = validate_sql(query)
    success = valid == expected

    print(f"\nQuery: {query or '[EMPTY]'}")
    print(f"Expected: {expected} | Actual: {valid}")
    print(f"Result: {'PASS' if success else 'FAIL'}")
    print(f"Message: {message}")

    passed += success

print("\n" + "=" * 60)
print(f"TESTS PASSED: {passed}/{len(test_cases)}")
print("=" * 60)
