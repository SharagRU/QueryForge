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


## QueryForge upgrade: CSV schema-aware mode (experimental)

This update preserves the original fixed-schema, template-based mode and adds an optional CSV-upload path.

### Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Dynamic CSV mode
1. Upload a CSV using the sidebar uploader.
2. Enable **Use uploaded CSV + schema-aware AI mode** below the query box.
3. Set an OpenAI-compatible API key in the environment:
   - `GEMINI_API_KEY` (preferred) or `GEMINI_API_KEY`
   - Optional: `GEMINI_MODEL` and `GEMINI_MODEL`
4. Ask a question about the CSV's columns.

The uploaded CSV is converted to a temporary SQLite database. QueryForge introspects its table/column names and types and sends the schema plus question to the configured LLM for SQL generation. SQL passes the existing validation layer and executes through a read-only SQLite connection.

**Limitations/security:** This is an experimental prototype. It does not yet support multiple uploaded CSV tables in one dataset, production-grade user isolation, connection pooling, SQLGlot AST-level security, time/resource limits, or arbitrary remote database connectors. Keep uploaded data non-sensitive. The model may misinterpret column semantics; review generated SQL before trusting results. The API key is read from environment variables and should never be committed.


### Gemini configuration

The dynamic CSV/schema-aware mode defaults to `gemini-3.5-flash`. You can override it with `GEMINI_MODEL`. The generation request timeout defaults to 120 seconds (`GEMINI_TIMEOUT_SECONDS`), and temporary HTTP 503 overloads are retried up to two times.
