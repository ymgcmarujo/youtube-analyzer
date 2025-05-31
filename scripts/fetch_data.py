import yt_dlp
import sqlite3
import json
from pathlib import Path
import subprocess

CHANNEL_URL = "https://www.youtube.com/@dozle/videos"
VIDEO_LIMIT = 1
DATA_DIR = "data"
CHAT_DIR = "chat"

Path(DATA_DIR).mkdir(exist_ok=True)
Path(CHAT_DIR).mkdir(exist_ok=True)

conn = sqlite3.connect(f"{DATA_DIR}/database.db")
cur = conn.cursor()

# 動画一覧を取得
def fetch_videos():
    with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True}) as ydl:
        info = ydl.extract_info(CHANNEL_URL, download=False)
        return info['entries'][:VIDEO_LIMIT]

# 動画情報を保存
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

# yt-dlpでチャットコメント（字幕）をダウンロード
def download_chat(video_id):
    cmd = [
        "yt-dlp",
        "--skip-download",
        "--write-subs",
        "--write-auto-sub",
        "--get-comments",  # ← 通常コメント取得
        "--sub-lang", "live_chat",
        "--sub-format", "json3",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "--add-header", f"Referer: https://www.youtube.com/watch?v={video_id}",
        "--add-header", "Accept-Language: ja,en-US;q=0.9,en;q=0.8",
        "--add-header", "Accept-Encoding: gzip, deflate, br",
        "--add-header", "DNT: 1",
        "--add-header", "Connection: keep-alive",
        "-o", f"{CHAT_DIR}/%(id)s.%(ext)s",
        f"https://www.youtube.com/watch?v={video_id}"
    ]

    subprocess.run(cmd, check=False)

#        "--proxy", "http://57.129.81.201:8080",  # ← 実在するプロキシを指定
# チャットファイル（.json3）をパースしてDBに格納
def save_chat_to_db(video_id):
    chat_file = Path(f"{CHAT_DIR}/{video_id}.live_chat.json3")
    if not chat_file.exists():
        print(f"No chat file for {video_id}")
        return
    with open(chat_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for event in data.get("events", []):
        timestamp_ms = int(event.get("tStartMs", 0))
        author = event.get("author", "")
        segments = event.get("segs", [])
        for seg in segments:
            text = seg.get("utf8", "").strip()
            if text:
                cur.execute("""
                    INSERT INTO comments (video_id, timestamp, text, author)
                    VALUES (?, ?, ?, ?)
                """, (
                    video_id,
                    timestamp_ms // 1000,
                    text,
                    author
                ))

# 実行処理
videos = fetch_videos()
for v in videos:
    save_video(v)
    download_chat(v["id"])
    save_chat_to_db(v["id"])

conn.commit()
conn.close()
print("✅ Chat data fetched and stored.")
