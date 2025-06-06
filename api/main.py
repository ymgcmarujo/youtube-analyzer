from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
#from api import database
import database
from pathlib import Path
import os
import requests

app = FastAPI()

# CORS（GitHub Pagesから呼び出すため）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "database.db"
GITHUB_DB_URL = "https://github.com/ymgcmarujo/youtube-analyzer/releases/download/v1/database.db"

def download_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    print("⬇️ Downloading database from GitHub Releases...")
    response = requests.get(GITHUB_DB_URL)
    if response.status_code == 200:
        with open(DB_PATH, "wb") as f:
            f.write(response.content)
        print("✅ Download complete.")
    else:
        print(f"❌ Failed to download DB: {response.status_code}")

@app.on_event("startup")
def startup_event():
    download_db()
    # DB接続確認（任意）
#    try:
#        conn = sqlite3.connect(DB_PATH)
#        conn.execute("SELECT sysdate FROM aster WHERE type='table';")
#        print("✅ DB connection OK.")
#        conn.close()
#    except Exception as e:
#        print(f"❌ DB error: {e}")

@app.get("/")
def root():
    return {"message": "YouTube分析API"}

@app.get("/videos")
def get_videos(video_id: str = None, page: int = 1, page_size: int = 20):
    if video_id:
        return database.get_video_meta(video_id)
    result = database.get_video_list(page, page_size)
    return {"videos": result["videos"], "total_count": result["total_count"]}

@app.get("/search")
def search_comments_api(keyword: str, video_id: str = None):
    return database.search_comments(keyword, video_id)


@app.get("/highlights")
def get_highlights(video_id: str):
    return database.get_top10_highlight_scenes(video_id)
