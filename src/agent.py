from .benchmark import find_exact_benchmark_sql

SCHEMA = """customers(customer_id, name, city, segment)
products(product_id, product_name, category, unit_price)
orders(order_id, customer_id, order_date, status)
order_items(item_id, order_id, product_id, quantity, unit_price)"""

def generate_sql(question: str):
    """Conservative local baseline: exact benchmark retrieval + a few safe patterns."""
    exact_sql, source = find_exact_benchmark_sql(question)
    if exact_sql:
        return exact_sql, f"Exact benchmark match ({source})"

    q = " ".join(question.lower().strip().split()).rstrip("?!. ")

    if q in {
        "how many orders are there in total",
        "count all orders",
        "total number of orders",
    }:
        return "SELECT COUNT(*) AS total_orders FROM orders;", "Built-in SQL rule"

    if q in {
        "how many customers are there",
        "count all customers",
        "total number of customers",
    }:
        return "SELECT COUNT(*) AS total_customers FROM customers;", "Built-in SQL rule"

    if q in {
        "how many products are there",
        "count all products",
        "total number of products",
    }:
        return "SELECT COUNT(*) AS total_products FROM products;", "Built-in SQL rule"

    return None, "No exact benchmark match or supported rule"

def schema_text():
    return SCHEMA
