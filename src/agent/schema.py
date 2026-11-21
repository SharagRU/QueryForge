
DATABASE_SCHEMA = """
TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT,
    city TEXT,
    segment TEXT
);

TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    unit_price REAL
);

TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date TEXT,
    status TEXT
);

TABLE order_items (
    item_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    unit_price REAL
);
"""

BUSINESS_RULES = """
1. Customer order count:
   COUNT(orders.order_id).

2. City order count:
   COUNT(orders.order_id).

3. Average order value (AOV):
   First calculate each order's total using
   SUM(quantity * unit_price), grouped by order_id.
   Then calculate the average of those order totals.
   Never use AVG(unit_price) as AOV.

4. Monthly completed revenue:
   Group by strftime('%Y-%m', orders.order_date).
   Sum quantity * unit_price.
   Only include completed orders.

5. Product units sold:
   SUM(order_items.quantity).
   Only include completed orders.

6. Product revenue:
   SUM(order_items.quantity * order_items.unit_price).
   Only include completed orders.
"""
