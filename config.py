import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ═══════════════════════════════════════════════════════════════
# TELEGRAM BOT TOKEN (From .env - Required)
# ═══════════════════════════════════════════════════════════════

BOT_TOKEN = os.getenv('BOT_TOKEN')

# Validate
if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN not found in .env file!")
    print()
    print("💡 Steps to fix:")
    print("   1. Create .env file:")
    print("      cp .env.example .env")
    print()
    print("   2. Edit .env and add:")
    print("      BOT_TOKEN=your_token_from_botfather")
    print()
    print("   3. Run bot again")
    print()
    exit(1)

# ═══════════════════════════════════════════════════════════════
# SETTINGS (From .env with defaults)
# ═══════════════════════════════════════════════════════════════

# Check interval in seconds (default: 10)
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '10'))

# Database file (default: alerts.db)
DATABASE_FILE = 'alerts.db'

# ═══════════════════════════════════════════════════════════════
# API CONFIGURATION
# ═══════════════════════════════════════════════════════════════

# Sử dụng VietStock API (miễn phí, không cần authentication)
VIETSTOCK_API_URL = 'https://api.vietstock.vn/tvnew/history'
