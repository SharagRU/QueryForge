import sqlite3
def inspect_sqlite_schema(database_path):
    schema={}
    with sqlite3.connect(database_path) as con:
        tables=con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()
        for (table,) in tables:
            cols=con.execute('PRAGMA table_info("{}")'.format(table.replace('"','""'))).fetchall()
            schema[table]=[{"name":c[1],"type":c[2],"nullable":not bool(c[3]),"primary_key":bool(c[5])} for c in cols]
    return schema
def format_schema(schema):
    return "\\n".join("TABLE "+t+"\\n"+"\\n".join("  - "+c["name"]+" ("+(c["type"] or "unknown")+")" for c in cols) for t,cols in schema.items())
