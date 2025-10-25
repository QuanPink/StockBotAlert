import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

# Check interval in seconds (default: 10)
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '10'))

# Database file (persistent volume)
DATABASE_FILE = "/data/alerts.db"

# Vietstock API
VIETSTOCK_API_URL = 'https://api.vietstock.vn/tvnew/history'
