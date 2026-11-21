
import json
from pathlib import Path

from src.agent.sql_generator import generate_sql
from src.agent.sql_executor import run_query

ROOT = Path(__file__).resolve().parents[2]
TEST_FILE = ROOT / "data" / "benchmarks" / "test.json"

with open(TEST_FILE, "r", encoding="utf-8") as f:
    samples = json.load(f)

supported = 0
executed = 0
unsupported_questions = []

for sample in samples:
    question = sample["question"]
    generated = generate_sql(question)

    if not generated["supported"]:
        unsupported_questions.append(question)
        continue

    supported += 1
    result = run_query(generated["sql"])

    if result["success"]:
        executed += 1
    else:
        print("\nEXECUTION ERROR:", question)
        print(result["error"])

print("\n" + "=" * 65)
print("UNSUPPORTED TEST QUESTIONS")
print("=" * 65)

for i, question in enumerate(unsupported_questions, 1):
    print(f"{i:02}. {question}")

print("\n" + "=" * 65)
print(f"SUPPORTED: {supported}/60")
print(f"EXECUTED: {executed}/60")
print("=" * 65)
