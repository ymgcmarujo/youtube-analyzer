// const API_BASE = "https://your-render-service.onrender.com";
const API_BASE = "http://127.0.0.1:8000"

// === APIラッパー ===

async function fetchVideos(page = 1) {
  const res = await fetch(`${API_BASE}/videos?page=${page}`);
  return await res.json();
}

async function fetchHighlights(videoId) {
  const res = await fetch(`${API_BASE}/highlights?video_id=${videoId}`);
  return await res.json();
}

// ほかにもAPIを追加する場合はここに集約