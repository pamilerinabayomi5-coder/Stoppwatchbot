import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_NAME = os.getenv("DATABASE_NAME", "stopwatch.db")
DATABASE_PATH = os.path.join(BASE_DIR, DATABASE_NAME)
TIMEZONE = os.getenv("TIMEZONE", "UTC")

if not BOT_TOKEN:
    raise ValueError("CRITICAL ERROR: BOT_TOKEN environment variable is not set.")

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(BASE_DIR, "bot.log"), encoding="utf-8")
    ]
)
logger = logging.getLogger("StopwatchBot")
