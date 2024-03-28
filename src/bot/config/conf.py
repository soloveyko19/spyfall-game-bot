from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

WORKDIR = Path(__file__).parent.parent

# Tokens
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPL_API_TOKEN = os.getenv("DEEPL_API_TOKEN")

# Postgres
POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")

# Redis
REDIS_HOST = os.getenv("REDIS_HOST")

# Logs
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
