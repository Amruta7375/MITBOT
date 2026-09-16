from db import get_db_conn

def get_settings():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT model,k,chunk_size FROM settings WHERE id=1")
    row = cur.fetchone()
    conn.close()
    if row:
        return {"model": row[0], "k": row[1], "chunk_size": row[2]}
    return {"model": "gemini-2.0-flash", "k": 3, "chunk_size": 500}

def set_settings(model: str, k: int, chunk_size: int):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("UPDATE settings SET model=?, k=?, chunk_size=? WHERE id=1", (model, k, chunk_size))
    conn.commit()
    conn.close()