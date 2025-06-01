from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import database

app = FastAPI()

# CORS（GitHub Pagesから呼び出すため）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
