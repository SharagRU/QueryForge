
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

files = [
    ROOT / "data" / "benchmarks" / "train.json",
    ROOT / "data" / "benchmarks" / "validation.json",
]

patterns = [
    "cities by completed revenue",
    "customers by number of orders",
    "products by average quantity per order",
    "cities by average order value",
    "customers by completed revenue",
    "customer segments by revenue",
    "product categories by revenue",
    "customers by completed order count",
]

samples = []

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        samples.extend(json.load(f))

seen = set()

for pattern in patterns:
    print("\n" + "=" * 75)
    print("PATTERN:", pattern.upper())
    print("=" * 75)

    matches = [
        sample for sample in samples
        if pattern in sample["question"].lower()
    ]

    if not matches:
        print("No matching examples found.")
        continue

    for sample in matches:
        normalized = re.sub(
            r"\btop\s+\d+\b",
            "top N",
            sample["question"].lower()
        )

        if normalized in seen:
            continue

        seen.add(normalized)

        print("\nQUESTION:", sample["question"])
        print("REFERENCE SQL:\n", sample["reference_sql"])
