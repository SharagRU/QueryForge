
import json
from pathlib import Path

from src.database.db import execute_sql

ROOT = Path(__file__).resolve().parents[2]
TEST_FILE = ROOT / "data" / "benchmarks" / "test.json"

with open(TEST_FILE, "r", encoding="utf-8") as f:
    test_data = json.load(f)

print("=" * 65)
print("QUERYFORGE DATABASE BENCHMARK VERIFICATION")
print("=" * 65)

correct = 0
total = len(test_data)

for sample in test_data:
    sql = sample["reference_sql"]
    expected = sample["expected_result"]

    actual = execute_sql(sql)

    if not actual["success"]:
        print("\nFAILED:", sample["question"])
        print("Error:", actual["error"])
        continue

    actual_rows = [
        list(row.values()) for row in actual["result"]
    ]

    expected_rows = [
        list(row.values()) if isinstance(row, dict) else list(row)
        for row in expected
    ]

    if actual_rows == expected_rows:
        correct += 1
    else:
        print("\nMISMATCH:", sample["question"])
        print("Expected:", expected_rows[:2])
        print("Actual:", actual_rows[:2])

print("\n" + "=" * 65)
print(f"EXACT MATCHES: {correct}/{total}")
print(f"ACCURACY: {correct / total * 100:.2f}%")
print("=" * 65)
