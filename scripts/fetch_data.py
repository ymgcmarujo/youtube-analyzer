import yt_dlp
from chat_downloader import ChatDownloader
import sqlite3

CHANNEL_URL = "https://www.youtube.com/c/GoogleDevelopers/videos"
VIDEO_LIMIT = 1

conn = sqlite3.connect("data/database.db")
cur = conn.cursor()

def fetch_videos():
    with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True}) as ydl:
        info = ydl.extract_info(CHANNEL_URL, download=False)
        return info['entries'][:VIDEO_LIMIT]

def save_video(v):
    cur.execute("""
        INSERT OR IGNORE INTO videos (video_id, title, channel, upload_date, thumbnail)
        VALUES (?, ?, ?, ?, ?)
    """, (
        v['id'],
        v['title'],
        v['uploader'],
        v.get('upload_date', ''),
        f"https://img.youtube.com/vi/{v['id']}/hqdefault.jpg"
    ))

def fetch_comments(video_id):
    comments = []
    try:
        chat = ChatDownloader().get_chat(f"https://www.youtube.com/watch?v={video_id}")
        for message in chat:
            comments.append({
                "timestamp": int(message.get("time_in_seconds", 0)),
                "text": message.get("message", ""),
                "author": message.get("author", {}).get("name", "")
            })
    except Exception as e:
        print(f"❌ Error fetching comments for {video_id}: {e}")
    return comments

def save_comments(video_id, comments):
    for c in comments:
        cur.execute("""
            INSERT INTO comments (video_id, timestamp, text, author)
            VALUES (?, ?, ?, ?)
        """, (video_id, c["timestamp"], c["text"], c["author"]))

# 実行
for v in fetch_videos():
    save_video(v)
    comments = fetch_comments(v['id'])
    save_comments(v['id'], comments)

conn.commit()
conn.close()
print("✅ Fetch complete")