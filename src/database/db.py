import sqlite3
from pathlib import Path
ROOT_DIR=Path(__file__).resolve().parents[2]
DB_PATH=ROOT_DIR/"data"/"queryforge.db"
def get_connection(readonly=False,database_path=None):
    target=Path(database_path) if database_path else DB_PATH
    if readonly:
        con=sqlite3.connect("file:"+target.as_posix()+"?mode=ro",uri=True)
        con.execute("PRAGMA query_only=ON")
    else: con=sqlite3.connect(target)
    con.row_factory=sqlite3.Row
    return con
def initialize_database():
    schema='''CREATE TABLE IF NOT EXISTS customers(customer_id INTEGER PRIMARY KEY,name TEXT NOT NULL,city TEXT NOT NULL,segment TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS products(product_id INTEGER PRIMARY KEY,product_name TEXT NOT NULL,category TEXT NOT NULL,unit_price REAL NOT NULL);
    CREATE TABLE IF NOT EXISTS orders(order_id INTEGER PRIMARY KEY,customer_id INTEGER NOT NULL,order_date TEXT NOT NULL,status TEXT NOT NULL,FOREIGN KEY(customer_id) REFERENCES customers(customer_id));
    CREATE TABLE IF NOT EXISTS order_items(item_id INTEGER PRIMARY KEY,order_id INTEGER NOT NULL,product_id INTEGER NOT NULL,quantity INTEGER NOT NULL,unit_price REAL NOT NULL,FOREIGN KEY(order_id) REFERENCES orders(order_id),FOREIGN KEY(product_id) REFERENCES products(product_id));'''
    with get_connection() as con: con.executescript(schema)
    print(f"Database initialized: {DB_PATH}")
def execute_sql(query,database_path=None):
    try:
        with get_connection(readonly=True,database_path=database_path) as con:
            cur=con.execute(query)
            if cur.description is None: return {"success":False,"error":"Only SELECT queries allowed"}
            cols=[d[0] for d in cur.description]; rows=[dict(r) for r in cur.fetchall()]
            return {"success":True,"columns":cols,"result":rows,"row_count":len(rows)}
    except sqlite3.Error as e: return {"success":False,"error":str(e)}
