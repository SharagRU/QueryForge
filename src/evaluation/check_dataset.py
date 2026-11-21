import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "benchmarks"

for split in ["train", "validation", "test"]:
    path = DATA_DIR / f"{split}.json"

    with open(path, "r", encoding="utf-8") as file:
        examples = json.load(file)

    print(f"\n{split.upper()}: {len(examples)} examples")

    if examples:
        first = examples[0]
        print("First question:", first["question"])
        print("Has reference SQL:", bool(first.get("reference_sql")))
        print("Has expected result:", "expected_result" in first)

print("\nDataset verification complete.")