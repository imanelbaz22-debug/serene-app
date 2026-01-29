from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from app.routers import health, checkins, analytics, chat, journal, reports

app = FastAPI(title="Serene ML Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
api_app = FastAPI()
api_app.include_router(health.router, prefix="/health", tags=["health"])
api_app.include_router(checkins.router, prefix="/checkins", tags=["checkins"])
api_app.include_router(analytics.router)
api_app.include_router(chat.router)
api_app.include_router(journal.router)
api_app.include_router(reports.router)

app.mount("/api", api_app)

# Serve Frontend
frontend_path = os.getenv("FRONTEND_PATH", os.path.join(os.path.dirname(__file__), "../../frontend/dist"))

if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
    
    # Catch-all for React Router/SPA
    @app.get("/{full_path:path}")
    async def catch_all(full_path: str):
        index_file = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "Frontend not built yet. Run 'npm run build' in /frontend"}
else:
    @app.get("/")
    def read_root():
        return {"message": "Serene Backend is running. Frontend 'dist' not found. Visit /api/docs for API."}
