# src/config/settings.py

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEAVIATE_URL = os.getenv("WEAVIATE_URL")

USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "true").lower() == "true"

ONEDRIVE_PATH = Path(os.getenv("ONEDRIVE_PATH", BASE_DIR / "onedrive"))
DATA_RAW_PATH = Path(os.getenv("DATA_RAW_PATH", BASE_DIR / "data" / "raw"))
DATA_CHUNKS_PATH = Path(os.getenv("DATA_CHUNKS_PATH", BASE_DIR / "data" / "chunks"))
DATA_INDEX_PATH = Path(os.getenv("DATA_INDEX_PATH", BASE_DIR / "data" / "index"))

USE_MOCK_MODE = os.getenv("USE_MOCK_MODE", "false").lower() == "false"
