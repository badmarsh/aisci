import sqlite3
import os
from database import get_connection

def add_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim TEXT,
            status TEXT,
            nextGate TEXT,
            run TEXT,
            narrative TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tasks (
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            priority TEXT,
            assignee TEXT,
            date TEXT,
            citation TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_tables()
    print("Schema updated with Evidence and Tasks tables.")
