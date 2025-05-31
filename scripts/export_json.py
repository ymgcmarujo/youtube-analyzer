import sqlite3
import json
from pathlib import Path

conn = sqlite3.connect("data/database.db")
cur = conn.cursor()

Path("data").mkdir(exist_ok=True)

# 動画一覧
videos = []
for row in cur.execute("SELECT * FROM videos"):
    videos.append({
        "video_id": row[0],
        "title": row[1],
        "channel": row[2],
        "upload_date": row[3],
        "thumbnail": row[4]
    })

with open("data/videos.json", "w", encoding="utf-8") as f:
    json.dump(videos, f, indent=2, ensure_ascii=False)

# 各動画のコメントTop10
for video in videos:
    video_id = video["video_id"]
    cur.execute("""
        SELECT timestamp, text, author FROM comments
        WHERE video_id = ?
        ORDER BY LENGTH(text) DESC
        LIMIT 10
    """, (video_id,))
    comments = [{"timestamp": r[0], "text": r[1], "author": r[2]} for r in cur.fetchall()]

    with open(f"data/comments_{video_id}.json", "w", encoding="utf-8") as f:
        json.dump({
            "video_id": video_id,
            "top_comments": comments
        }, f, indent=2, ensure_ascii=False)

conn.close()
print("✅ JSON exported")