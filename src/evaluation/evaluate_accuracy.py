
import json
import math
from pathlib import Path

from src.agent.pipeline import ask_database

ROOT = Path(__file__).resolve().parents[2]
TEST_FILE = ROOT / "data" / "benchmarks" / "test.json"


def values_equal(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-6)

    return a == b


def results_equal(actual, expected):
    if len(actual) != len(expected):
        return False

    for actual_row, expected_row in zip(actual, expected):
        if len(actual_row) != len(expected_row):
            return False

        for actual_value, expected_value in zip(actual_row, expected_row):
            if not values_equal(actual_value, expected_value):
                return False

    return True


with open(TEST_FILE, "r", encoding="utf-8") as f:
    samples = json.load(f)

total = len(samples)
supported = 0
executed = 0
correct = 0

failures = []

for sample in samples:
    question = sample["question"]
    expected = sample["expected_result"]

    response = ask_database(question)

    if response["stage"] == "generation":
        failures.append((question, "UNSUPPORTED"))
        continue

    supported += 1

    if not response["success"]:
        failures.append((question, "EXECUTION FAILED"))
        continue

    executed += 1

    actual = response["result"]

    # Convert database dictionaries into ordered value lists.
    actual_values = [
        list(row.values()) for row in actual
    ]

    if results_equal(actual_values, expected):
        correct += 1
    else:
        failures.append((question, "INCORRECT RESULT"))


print("\n" + "=" * 65)
print("QUERYFORGE — BENCHMARK ACCURACY")
print("=" * 65)

print("Total questions:", total)
print("Supported:", supported)
print("Executed:", executed)
print("Correct results:", correct)

print("Coverage:", f"{supported / total * 100:.2f}%")
print("Execution rate:", f"{executed / total * 100:.2f}%")
print("Result accuracy:", f"{correct / total * 100:.2f}%")

if executed:
    print(
        "Conditional accuracy:",
        f"{correct / executed * 100:.2f}%"
    )

print("\nFAILURES:", len(failures))

for i, (question, reason) in enumerate(failures, 1):
    print(f"{i:02}. [{reason}] {question}")

print("=" * 65)
