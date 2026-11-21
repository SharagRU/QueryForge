# QueryForge — VS Code Edition

A local Python version of the QueryForge SQL analytics demo. It uses SQLite, executes queries in read-only mode, and can retrieve verified SQL for exact benchmark questions.

## 1. Requirements
- Windows 10/11
- Python 3.10+
- VS Code

## 2. Setup (PowerShell terminal)
Open this folder in VS Code, then run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, run:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 3. Add your database
Copy your existing `queryforge.db` from Colab into this project's `data` folder:

`data/queryforge.db`

Do not run `init_db.py` if you already copied your real database. `init_db.py` only creates an empty database schema.

## 4. Add benchmark JSON files (optional)
Copy these files from Colab into `data/`:
- `train (1).json`
- `validation (1).json`
- `test (1).json`

The app searches these files for an exact question match and uses its reference SQL. This is a verified benchmark lookup baseline, not a generative model.

## 5. Run
```powershell
python main.py
```

Try:
- `How many orders are there in total?`
- `Top 18 products by units sold`

Use `exit` to quit.

## Current limitations
- No GPU or fine-tuning is required.
- Exact benchmark matches can use the stored reference SQL.
- A small set of transparent SQL patterns handles common questions.
- Unsupported questions are rejected rather than answered with invented SQL.
- The reported Colab V5 benchmark score is a preliminary result on a 300-question, 15-template dataset; it is not a guarantee of generalization to unseen query types.
