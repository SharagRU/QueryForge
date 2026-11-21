
import sqlite3
import random
from datetime import datetime, timedelta

from src.database.db import DB_PATH

random.seed(42)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("PRAGMA foreign_keys = ON")

cur.executescript("""
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT,
    city TEXT,
    segment TEXT
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    unit_price REAL
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date TEXT,
    status TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
    item_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    unit_price REAL,
    FOREIGN KEY(order_id) REFERENCES orders(order_id),
    FOREIGN KEY(product_id) REFERENCES products(product_id)
);
""")

cities = [
    "Bengaluru", "Mumbai", "Delhi",
    "Chennai", "Hyderabad", "Pune"
]

segments = ["Consumer", "Corporate", "Small Business"]

customers = [
    (i, f"Customer_{i}", random.choice(cities),
     random.choice(segments))
    for i in range(1, 501)
]

cur.executemany(
    "INSERT INTO customers VALUES (?, ?, ?, ?)",
    customers
)

products = [
    ("Laptop", "Electronics", 65000),
    ("Phone", "Electronics", 25000),
    ("Headphones", "Accessories", 3000),
    ("Keyboard", "Accessories", 1800),
    ("Monitor", "Electronics", 14000),
    ("Chair", "Furniture", 8000),
    ("Desk", "Furniture", 12000),
    ("Mouse", "Accessories", 900),
    ("Tablet", "Electronics", 32000),
    ("Printer", "Electronics", 11000)
]

cur.executemany("""
INSERT INTO products (product_name, category, unit_price)
VALUES (?, ?, ?)
""", products)

start_date = datetime(2024, 1, 1)
orders = []
items = []
item_id = 1

for order_id in range(1, 5001):
    customer_id = random.randint(1, 500)
    date = start_date + timedelta(days=random.randint(0, 1000))

    status = random.choices(
        ["completed", "cancelled", "refunded"],
        weights=[85, 10, 5]
    )[0]

    orders.append((
        order_id,
        customer_id,
        date.strftime("%Y-%m-%d"),
        status
    ))

    for _ in range(random.randint(1, 4)):
        product_id = random.randint(1, 10)
        quantity = random.randint(1, 5)
        price = products[product_id - 1][2]

        items.append((
            item_id,
            order_id,
            product_id,
            quantity,
            price
        ))

        item_id += 1

cur.executemany(
    "INSERT INTO orders VALUES (?, ?, ?, ?)",
    orders
)

cur.executemany(
    "INSERT INTO order_items VALUES (?, ?, ?, ?, ?)",
    items
)

conn.commit()

counts = {}
for table in ["customers", "products", "orders", "order_items"]:
    counts[table] = cur.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

conn.close()

print("\nQUERYFORGE DATABASE RESTORED")
print("Database:", DB_PATH)

for table, count in counts.items():
    print(f"{table}: {count:,} rows")
