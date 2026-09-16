import sqlite3
import os
from datetime import datetime

SQLITE_FILE = "mitbot_db.sqlite"

def get_db_conn():
    conn = sqlite3.connect(SQLITE_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT,
            password_hash BLOB,
            role TEXT DEFAULT 'user',
            created_at TEXT
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            question TEXT,
            answer TEXT,
            is_bookmark INTEGER DEFAULT 0,
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pdfs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            filepath TEXT,
            user_id INTEGER,
            uploaded_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
   
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            model TEXT,
            k INTEGER,
            chunk_size INTEGER
        )
    """)
    
    cur.execute("SELECT COUNT(*) as c FROM settings")
    if cur.fetchone()["c"] == 0:
        cur.execute("INSERT INTO settings (id, model, k, chunk_size) VALUES (1, ?, ?, ?)",
                    ("gemini-2.0-flash", 3, 500))
    conn.commit()
    conn.close()

def migrate_db():
    conn = get_db_conn()
    cur = conn.cursor()
    
    cur.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cur.fetchall()]
    if 'email' not in columns:
        cur.execute("ALTER TABLE users ADD COLUMN email TEXT")
        
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_email ON users(email)")
        conn.commit()
    
    cur.execute("PRAGMA table_info(history)")
    columns = [row[1] for row in cur.fetchall()]
    if 'is_bookmark' not in columns:
        cur.execute("ALTER TABLE history ADD COLUMN is_bookmark INTEGER DEFAULT 0")
        conn.commit()
    
    cur.execute("PRAGMA table_info(pdfs)")
    columns = [row[1] for row in cur.fetchall()]
    if 'user_id' not in columns:
        cur.execute("ALTER TABLE pdfs ADD COLUMN user_id INTEGER")
       
        conn.commit()
    conn.close()

init_db()
migrate_db()