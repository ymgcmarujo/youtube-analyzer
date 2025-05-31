import sqlite3

conn = sqlite3.connect("data/database.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS videos (
    video_id TEXT PRIMARY KEY,
    title TEXT,
    channel TEXT,
    upload_date TEXT,
    thumbnail TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT,
    timestamp INTEGER,
    text TEXT,
    author TEXT
)
""")

conn.commit()
conn.close()
print("✅ DB initialized")