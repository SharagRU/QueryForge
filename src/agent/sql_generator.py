
import re


ENTITY_MAP = {
    "customer segments": "segments",
    "segments": "segments",
    "product categories": "categories",
    "categories": "categories",
    "customers": "customers",
    "cities": "cities",
    "months": "months",
    "products": "products",
}

METRIC_MAP = {
    "average quantity per order": "avg_quantity",
    "average order value": "aov",
    "completed order count": "orders",
    "number of orders": "orders",
    "order count": "orders",
    "units sold": "units",
    "revenue": "revenue",
}

STATUS_MAP = {
    "completed": "completed",
    "refunded": "refunded",
    "cancelled": "cancelled",
}


def extract_limit(question):
    match = re.search(r"\btop\s+(\d+)\b", question.lower())
    return int(match.group(1)) if match else 10


def extract_entity(question):
    text = question.lower()

    for phrase, entity in sorted(
        ENTITY_MAP.items(),
        key=lambda item: len(item[0]),
        reverse=True
    ):
        if phrase in text:
            return entity

    return None


def extract_metric(question):
    text = question.lower()

    for phrase, metric in sorted(
        METRIC_MAP.items(),
        key=lambda item: len(item[0]),
        reverse=True
    ):
        if phrase in text:
            return metric

    return None


def extract_status(question):
    text = question.lower()

    for phrase, status in STATUS_MAP.items():
        if phrase in text:
            return status

    return None


def generate_sql(question):
    entity = extract_entity(question)
    metric = extract_metric(question)
    status = extract_status(question)
    limit = extract_limit(question)

    result = {
        "entity": entity,
        "metric": metric,
        "status": status,
        "limit": limit,
        "supported": False,
        "sql": None
    }

    if not entity or not metric:
        result["error"] = "Could not identify entity or metric."
        return result

    # 1. Product revenue
    if entity == "products" and metric == "revenue":
        if status not in ("completed", "refunded"):
            result["error"] = "Product revenue requires a supported status."
            return result

        sql = f"""
        SELECT p.product_name,
               SUM(oi.quantity * oi.unit_price) AS revenue
        FROM order_items oi
        JOIN orders o ON o.order_id = oi.order_id
        JOIN products p ON p.product_id = oi.product_id
        WHERE o.status = '{status}'
        GROUP BY p.product_id
        ORDER BY revenue DESC
        LIMIT {limit};
        """

    # 2. City order count
    elif entity == "cities" and metric == "orders":
        if status:
            sql = f"""
            SELECT c.city,
                   COUNT(o.order_id) AS order_count
            FROM customers c
            JOIN orders o ON o.customer_id = c.customer_id
            WHERE o.status = '{status}'
            GROUP BY c.city
            ORDER BY order_count DESC
            LIMIT {limit};
            """
        else:
            sql = f"""
            SELECT c.city,
                   COUNT(o.order_id) AS order_count
            FROM customers c
            JOIN orders o ON o.customer_id = c.customer_id
            GROUP BY c.city
            ORDER BY order_count DESC
            LIMIT {limit};
            """

    # 3. Product units sold
    elif entity == "products" and metric == "units":
        sql = f"""
        SELECT p.product_name,
               SUM(oi.quantity) AS units_sold
        FROM products p
        JOIN order_items oi ON oi.product_id = p.product_id
        JOIN orders o ON o.order_id = oi.order_id
        WHERE o.status = 'completed'
        GROUP BY p.product_id
        ORDER BY units_sold DESC
        LIMIT {limit};
        """

    # 4. Customer average order value
    elif entity == "customers" and metric == "aov":
        sql = f"""
        SELECT c.name,
               AVG(order_totals.total) AS avg_order_value
        FROM customers c
        JOIN orders o ON o.customer_id = c.customer_id
        JOIN (
            SELECT order_id,
                   SUM(quantity * unit_price) AS total
            FROM order_items
            GROUP BY order_id
        ) order_totals ON order_totals.order_id = o.order_id
        GROUP BY c.customer_id
        ORDER BY avg_order_value DESC
        LIMIT {limit};
        """

    # 5. Monthly completed revenue
    elif entity == "months" and metric == "revenue":
        sql = f"""
        SELECT strftime('%Y-%m', o.order_date) AS month,
               SUM(oi.quantity * oi.unit_price) AS revenue
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.order_id
        WHERE o.status = 'completed'
        GROUP BY month
        ORDER BY revenue DESC
        LIMIT {limit};
        """

    # 6. City completed revenue
    elif entity == "cities" and metric == "revenue":
        if status not in (None, "completed"):
            result["error"] = "City revenue currently supports completed orders only."
            return result

        sql = f"""
        SELECT c.city,
               SUM(oi.quantity * oi.unit_price) AS revenue
        FROM customers c
        JOIN orders o ON o.customer_id = c.customer_id
        JOIN order_items oi ON oi.order_id = o.order_id
        WHERE o.status = 'completed'
        GROUP BY c.city
        ORDER BY revenue DESC
        LIMIT {limit};
        """

    # 7. Customer order count
    elif entity == "customers" and metric == "orders":
        if status:
            sql = f"""
            SELECT c.name,
                   COUNT(o.order_id) AS completed_orders
            FROM customers c
            JOIN orders o ON o.customer_id = c.customer_id
            WHERE o.status = '{status}'
            GROUP BY c.customer_id
            ORDER BY completed_orders DESC
            LIMIT {limit};
            """
        else:
            sql = f"""
            SELECT c.name,
                   COUNT(o.order_id) AS order_count
            FROM customers c
            JOIN orders o ON o.customer_id = c.customer_id
            GROUP BY c.customer_id
            ORDER BY order_count DESC
            LIMIT {limit};
            """

    # 8. Product average quantity per order
    elif entity == "products" and metric == "avg_quantity":
        sql = f"""
        SELECT p.product_name,
               AVG(oi.quantity) AS avg_quantity
        FROM products p
        JOIN order_items oi ON oi.product_id = p.product_id
        JOIN orders o ON o.order_id = oi.order_id
        WHERE o.status = 'completed'
        GROUP BY p.product_id
        ORDER BY avg_quantity DESC
        LIMIT {limit};
        """

    # 9. City average order value
    elif entity == "cities" and metric == "aov":
        sql = f"""
        SELECT c.city,
               AVG(order_totals.total) AS avg_order_value
        FROM customers c
        JOIN orders o ON o.customer_id = c.customer_id
        JOIN (
            SELECT order_id,
                   SUM(quantity * unit_price) AS total
            FROM order_items
            GROUP BY order_id
        ) order_totals ON order_totals.order_id = o.order_id
        WHERE o.status = 'completed'
        GROUP BY c.city
        ORDER BY avg_order_value DESC
        LIMIT {limit};
        """

    # 10. Customer completed revenue
    elif entity == "customers" and metric == "revenue":
        if status not in (None, "completed"):
            result["error"] = "Customer revenue currently supports completed orders only."
            return result

        sql = f"""
        SELECT c.name,
               SUM(oi.quantity * oi.unit_price) AS revenue
        FROM customers c
        JOIN orders o ON o.customer_id = c.customer_id
        JOIN order_items oi ON oi.order_id = o.order_id
        WHERE o.status = 'completed'
        GROUP BY c.customer_id
        ORDER BY revenue DESC
        LIMIT {limit};
        """

    # 11. Customer segment revenue
    elif entity == "segments" and metric == "revenue":
        if status not in (None, "completed"):
            result["error"] = "Segment revenue currently supports completed orders only."
            return result

        sql = f"""
        SELECT c.segment,
               SUM(oi.quantity * oi.unit_price) AS revenue
        FROM customers c
        JOIN orders o ON o.customer_id = c.customer_id
        JOIN order_items oi ON oi.order_id = o.order_id
        WHERE o.status = 'completed'
        GROUP BY c.segment
        ORDER BY revenue DESC
        LIMIT {limit};
        """

    # 12. Product category revenue
    elif entity == "categories" and metric == "revenue":
        if status not in (None, "completed"):
            result["error"] = "Category revenue currently supports completed orders only."
            return result

        sql = f"""
        SELECT p.category,
               SUM(oi.quantity * oi.unit_price) AS revenue
        FROM products p
        JOIN order_items oi ON oi.product_id = p.product_id
        JOIN orders o ON o.order_id = oi.order_id
        WHERE o.status = 'completed'
        GROUP BY p.category
        ORDER BY revenue DESC
        LIMIT {limit};
        """

    else:
        result["error"] = (
            "This entity and metric combination is not implemented yet."
        )
        return result

    result["supported"] = True
    result["sql"] = sql.strip()

    return result


if __name__ == "__main__":
    questions = [
        "Top 5 products by completed revenue",
        "Top 10 cities by refunded order count",
        "Top 12 products by units sold",
        "Top 7 customers by average order value",
        "Top 8 months by completed revenue",
        "Top 6 cities by completed revenue",
        "Top 20 customers by number of orders",
        "Top 19 products by average quantity per order",
        "Top 18 cities by average order value",
        "Top 15 customers by completed revenue",
        "Top 16 customer segments by revenue",
        "Top 11 product categories by revenue",
        "Top 11 customers by completed order count"
    ]

    for question in questions:
        result = generate_sql(question)

        print("\n" + "=" * 65)
        print("QUESTION:", question)
        print("ENTITY:", result["entity"])
        print("METRIC:", result["metric"])
        print("STATUS:", result["status"])
        print("SUPPORTED:", result["supported"])
        print("SQL:\n", result["sql"] or result.get("error"))
