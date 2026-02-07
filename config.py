import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API URLs
SOFASCORE_LIVE_EVENTS_URL = "https://api.sofascore.com/api/v1/sport/tennis/events/live"
SOFASCORE_STATS_URL_TEMPLATE = "https://api.sofascore.com/api/v1/event/{match_id}/statistics"
POLYMARKET_SEARCH_URL = "https://gamma-api.polymarket.com/public-search"

# File paths
OUTPUT_CSV = "data/tennis_dawgs.csv"

# Telegram config
# Set these via environment variables: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Tournament filters
ALLOWED_TOURNAMENTS = ["ATP", "WTA", "Challenger", "UTR", "Unknown"]

# Polling
POLL_INTERVAL_SECONDS = 15

