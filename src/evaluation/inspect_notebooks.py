import json
from pathlib import Path

files = [
    Path.home() / "Downloads" / "QueryForge.ipynb",
    Path.home() / "Downloads" / "Copy_of_QueryForge.ipynb",
]

keywords = [
    "CREATE TABLE",
    "sqlite3",
    "random.seed",
    "np.random.seed",
    "INSERT INTO",
    "customers",
    "order_items",
    "synthetic",
    "backup",
]

for notebook_path in files:
    print("\n" + "=" * 75)
    print("NOTEBOOK:", notebook_path.name)
    print("=" * 75)

    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    for index, cell in enumerate(notebook.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue

        source = "".join(cell.get("source", []))
        matches = [word for word in keywords if word.lower() in source.lower()]

        if matches:
            print(f"\n--- CELL {index} | MATCHES: {', '.join(matches)} ---")
            print(source[:3500])