import uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from factmesh.config import settings
from factmesh.api.routes import router as api_router
from factmesh.storage import db
from factmesh.pipeline import pipeline

app = FastAPI(
    title="FactMesh",
    description="General-purpose Cross-Document Fact Knowledge Layer",
    version="1.0.0"
)

# Mount API routes
app.include_router(api_router)

# Mount UI static files
UI_DIR = Path(__file__).resolve().parent / "factmesh" / "ui"
STATIC_DIR = UI_DIR / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_ui():
    index_file = UI_DIR / "index.html"
    return FileResponse(str(index_file))

@app.on_event("startup")
def startup_event():
    # If database is freshly initialized, automatically load the Delhivery dataset as a starter showcase
    docs = db.get_documents()
    if not docs:
        print("[FactMesh] Initializing starter showcase with Delhivery logistics dataset...")
        try:
            pipeline.load_starter_dataset("delhivery")
            print("[FactMesh] Starter dataset loaded successfully.")
        except Exception as e:
            print(f"[FactMesh] Note: Starter dataset auto-load skipped ({e})")

if __name__ == "__main__":
    print("==================================================")
    print("  FactMesh: Cross-Document Fact Knowledge Layer   ")
    print("  Serving at: http://localhost:8000               ")
    print("==================================================")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
