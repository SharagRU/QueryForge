
import sqlite3
from pathlib import Path

# Store database in the project's data folder
ROOT_DIR = Path(__file__).resolve().parents[2]
DB_PATH = ROOT_DIR / "data" / "queryforge.db"


def get_connection(readonly=False):
    if readonly:
        connection = sqlite3.connect(
            f"file:{DB_PATH.as_posix()}?mode=ro",
            uri=True
        )
        connection.execute("PRAGMA query_only = ON")
    else:
        connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create the QueryForge business database."""

    schema = """
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        city TEXT NOT NULL,
        segment TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        unit_price REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );

    CREATE TABLE IF NOT EXISTS order_items (
        item_id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
    """

    with get_connection() as connection:
        connection.executescript(schema)

    print(f"Database initialized: {DB_PATH}")


def execute_sql(query):
    """Execute read-only SQL and return structured results."""

    try:
        with get_connection(readonly=True) as connection:
            cursor = connection.execute(query)

            if cursor.description is None:
                return {
                    "success": False,
                    "error": "Only SELECT queries are allowed."
                }

            columns = [column[0] for column in cursor.description]
            rows = [dict(row) for row in cursor.fetchall()]

            return {
                "success": True,
                "columns": columns,
                "result": rows,
                "row_count": len(rows)
            }

    except sqlite3.Error as error:
        return {
            "success": False,
            "error": str(error)
        }


if __name__ == "__main__":
    initialize_database()
