import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "database.db"

KEYWORDS = ["すご", "神", "草", "えぐ", "やば", "www", "上手", "最高", "感動", "泣"]

def get_connection():
    return sqlite3.connect(DB_PATH)
def get_video_list(page: int = 1, page_size: int = 20):
    offset = (page - 1) * page_size

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM videos
    """)
    total_count = cursor.fetchone()[0]
    print(total_count)
    cursor.execute("""
        SELECT video_id, title, published_at, uploader, video_type
        FROM videos
        ORDER BY published_at DESC
        LIMIT ? OFFSET ?
    """, (page_size, offset))

    rows = cursor.fetchall()
    conn.close()

    videos = [
        {
            "video_id": row[0],
            "title": row[1],
            "published_at": row[2],
            "uploader": row[3],
            "video_type": row[4]
        }
        for row in rows
    ]

    return {
        "videos": videos,
        "total_count": total_count
    }


def get_top10_highlight_scenes(video_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, content FROM comments WHERE video_id = ?
    """, (video_id,))
    all_comments = cursor.fetchall()
    conn.close()

    comment_count_map = {}
    keyword_count_map = {}
    comment_bucket = {}

    for timestamp, content in all_comments:
        comment_bucket.setdefault(timestamp, []).append({
            "t": timestamp,
            "c": content
        })
        comment_count_map[timestamp] = comment_count_map.get(timestamp, 0) + 1
        if any(kw in content for kw in KEYWORDS):
            keyword_count_map[timestamp] = keyword_count_map.get(timestamp, 0) + 1

    top_comment_counts = sorted(comment_count_map.items(), key=lambda x: x[1], reverse=True)[:10]
    top_keyword_counts = sorted(keyword_count_map.items(), key=lambda x: x[1], reverse=True)[:10]
    for ts, count in top_comment_counts:
        print(comment_bucket.get(ts, []))

    return {
        "top_comment_count": [
            {
                "t": ts,
                "n": count,
                "comments": comment_bucket.get(ts, [])
            } for ts, count in top_comment_counts
        ],
        "top_keywords_count": [
            {
                "t": ts,
                "n": count,
                "comments": comment_bucket.get(ts, [])
            } for ts, count in top_keyword_counts
        ]
    }
def search_comments(keyword: str, video_id: str = None):
    conn = get_connection()
    cursor = conn.cursor()

    if video_id:
        cursor.execute("""
            SELECT video_id, timestamp, content
            FROM comments
            WHERE video_id = ? AND content LIKE ?
            ORDER BY timestamp ASC
        """, (video_id, f"%{keyword}%"))
    else:
        cursor.execute("""
            SELECT video_id, timestamp, content
            FROM comments
            WHERE content LIKE ?
            ORDER BY timestamp ASC
        """, (f"%{keyword}%",))

    rows = cursor.fetchall()
    conn.close()
    print(rows)
    return [
        {"video_id": row[0], "timestamp": row[1], "content": row[2]}
        for row in rows
    ]
def get_video_meta(video_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT video_id, title, published_at, uploader, video_type
        FROM videos WHERE video_id = ?
    """, (video_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "video_id": row[0],
            "title": row[1],
            "published_at": row[2],
            "uploader": row[3],
            "video_type": row[4],
        }
    else:
        return None
