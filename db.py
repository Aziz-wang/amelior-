import sqlite3

def init_db():
    conn = sqlite3.connect("quickdrop.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS deliveries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client TEXT,
        pickup TEXT,
        destination TEXT,
        price INTEGER,
        status TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS tracking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        delivery_id INTEGER,
        lat TEXT,
        lng TEXT,
        updated_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        delivery_id INTEGER,
        method TEXT,
        amount INTEGER,
        txid TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()
