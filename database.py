import sqlite3
from pathlib import Path

DB_PATH = "data.db"

def init_db():
    if not Path(DB_PATH).exists():
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS status (
                    id INTEGER PRIMARY KEY,
                    text TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    url TEXT
                )
            ''')
            cursor.execute("INSERT INTO status (id, text) VALUES (?, ?)", (1, "Idle"))
            conn.commit()

def set_status(text):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE status SET text = ? WHERE id = 1", (text,))
        conn.commit()

def get_status():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT text FROM status WHERE id = 1")
        return cursor.fetchone()[0]

def add_link(title, url):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO links (title, url) VALUES (?, ?)", (title, url))
        conn.commit()

def get_all_links():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title, url FROM links")
        return cursor.fetchall()

def remove_duplicate_links():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM links 
            WHERE rowid NOT IN (
                SELECT MIN(rowid)
                FROM links
                GROUP BY title, url
            )
        """)
        conn.commit()
