from pathlib import Path
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"
STARTER_DIR = BASE_DIR / "starter-datasets"

for d in [DATA_DIR, UPLOAD_DIR, PROCESSED_DIR]:
    d.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    app_name: str = "FactMesh"
    database_path: str = str(DATA_DIR / "factmesh.db")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    similarity_threshold: float = 0.45
    numeric_tolerance: float = 0.02  # 2% tolerance for corroboration
    max_pages_per_large_doc: int = 100
    chunk_page_size: int = 3
    chunk_overlap: int = 1

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
