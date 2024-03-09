from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

WORKDIR = Path(__file__).parent.parent
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEEPL_API_TOKEN = os.getenv("DEEPL_API_TOKEN")
