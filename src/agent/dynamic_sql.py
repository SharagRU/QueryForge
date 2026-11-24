import os
import re
import time
import requests

from .schema_inspector import inspect_sqlite_schema, format_schema
from .sql_validator import validate_sql


def _extract_sql(text):
    text = (text or "").strip()
    match = re.fullmatch(r"```(?:sql)?\s*(.*?)\s*```", text, flags=re.IGNORECASE | re.DOTALL)
    if match:
        text = match.group(1).strip()
    return text


def generate_dynamic_sql(question, database_path):
    """Generate schema-aware SQLite SQL using the Gemini Developer API."""
    key = os.getenv("GEMINI_API_KEY") or os.getenv("QF_LLM_API_KEY")
    if not key:
        return {"success": False, "error": "Gemini API key missing. Set GEMINI_API_KEY in your environment."}

    # Use the model that was verified with a successful generateContent request.
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash").strip()
    try:
        timeout_seconds = max(30, int(os.getenv("GEMINI_TIMEOUT_SECONDS", "120")))
    except ValueError:
        timeout_seconds = 120

    schema = inspect_sqlite_schema(database_path)
    if not schema:
        return {"success": False, "error": "No user tables were found in the uploaded database."}

    prompt = f"""You generate SQLite queries for a business analytics application.
Use ONLY the tables and columns in the schema below.
Return exactly one read-only SQL query and no Markdown or explanation.
The query must begin with SELECT or WITH. Never generate INSERT, UPDATE, DELETE,
DROP, ALTER, CREATE, PRAGMA, ATTACH, DETACH, or multiple statements.
If the question cannot be answered from this schema, return exactly:
-- UNSUPPORTED: followed by a short explanation.

DATABASE SCHEMA:
{format_schema(schema)}

QUESTION: {question}
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {"x-goog-api-key": key, "Content-Type": "application/json"}
    payload = {
        "systemInstruction": {
            "parts": [{"text": "You are a careful SQLite SQL generator. Follow the user's schema and return read-only SQL only."}]
        },
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.0}
    }

    # Retry only temporary 503 overloads; do not retry auth, quota, or bad-request errors.
    for attempt in range(3):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout_seconds)
            if response.status_code == 503:
                if attempt < 2:
                    time.sleep(2 ** (attempt + 1))
                    continue
                return {"success": False, "error": f"Gemini model '{model}' is temporarily unavailable (503) after 3 attempts. Please retry later or choose another available model."}
            if response.status_code == 404:
                return {"success": False, "error": f"Gemini model '{model}' was not found or is unavailable for generation (404). Set GEMINI_MODEL to a model available to your API project."}
            if response.status_code == 400:
                return {"success": False, "error": "Gemini rejected the generation request (400): " + response.text[:800]}
            if response.status_code in (401, 403):
                return {"success": False, "error": "Gemini API authentication/permission failed. Check the API key and project access."}
            if response.status_code == 429:
                return {"success": False, "error": "Gemini rate limit or quota reached (429). Check Google AI Studio usage limits and retry after the quota window."}
            response.raise_for_status()
            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return {"success": False, "error": f"Gemini model '{model}' returned no SQL candidate. Try rephrasing the question."}
            parts = candidates[0].get("content", {}).get("parts", [])
            generated_text = "\n".join(part.get("text", "") for part in parts if part.get("text"))
            sql = _extract_sql(generated_text)
            if not sql:
                return {"success": False, "error": f"Gemini model '{model}' returned an empty response."}
            if sql.upper().startswith("-- UNSUPPORTED"):
                return {"success": False, "error": sql.split(":", 1)[-1].strip() or "This question is not supported by the uploaded schema."}

            valid, message = validate_sql(sql)
            if not valid:
                return {"success": False, "error": "Generated SQL rejected: " + message, "sql": sql}

            return {
                "success": True,
                "sql": sql,
                "schema": schema,
                "generation_method": f"gemini_schema_aware:{model}"
            }
        except requests.Timeout:
            return {"success": False, "error": f"Gemini model '{model}' did not respond within {timeout_seconds} seconds. The API request timed out; try a shorter question or retry later."}
        except requests.RequestException as exc:
            return {"success": False, "error": f"Gemini API request failed for model '{model}': {exc}"}
        except (KeyError, TypeError, ValueError) as exc:
            return {"success": False, "error": f"Could not read Gemini response: {exc}"}

    return {"success": False, "error": f"Gemini model '{model}' is temporarily unavailable."}
