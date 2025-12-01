import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
EXPORT_DIR = Path(os.getenv("EXPORT_DIR", "./data/exports"))

# Create directories if they don't exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ocr_app.db")

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
USE_GPT_VISION = os.getenv("USE_GPT_VISION", "false").lower() == "true"

# OCR Settings
OCR_LANGUAGE = os.getenv("OCR_LANGUAGE", "ch")  # Chinese
