
from src.database.db import get_connection, DB_PATH


def inspect_database():
    with get_connection(readonly=True) as connection:

        tables = ["customers", "products", "orders", "order_items"]

        print("\n" + "=" * 55)
        print("          QUERYFORGE DATABASE INSPECTOR")
        print("=" * 55)

        for table in tables:
            count = connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            print(f"\nTABLE: {table}")
            print(f"Rows: {count}")

            columns = connection.execute(
                f"PRAGMA table_info({table})"
            ).fetchall()

            for column in columns:
                print(f"  - {column['name']}: {column['type']}")

        print("\nDatabase:", DB_PATH)
        print("=" * 55)


if __name__ == "__main__":
    inspect_database()
