
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRAIN_FILE = ROOT / "data" / "benchmarks" / "train.json"

with open(TRAIN_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

print("TOTAL TRAINING EXAMPLES:", len(data))
print("\nQUESTION PATTERNS:\n")

for i, sample in enumerate(data, 1):
    print(f"{i:03}. [{sample['difficulty']}] {sample['question']}")
