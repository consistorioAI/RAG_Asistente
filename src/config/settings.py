# src/config/settings.py
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
BOX_CLIENT_ID = os.getenv("BOX_CLIENT_ID")
BOX_CLIENT_SECRET = os.getenv("BOX_CLIENT_SECRET")
BOX_ENTERPRISE_ID = os.getenv("BOX_ENTERPRISE_ID")
