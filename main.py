import cloudscraper
import time
import datetime
import config
from src.api.sofascore import fetch_live_events
from src.processors.match_processor import process_match
from src.storage.cache_manager import CacheManager
from src.storage.csv_logger import ensure_csv_header
from src.utils.constants import RESET

# Create a CloudScraper session
scraper = cloudscraper.create_scraper()

# Initialize cache manager
cache_manager = CacheManager()

# Ensure CSV header exists
ensure_csv_header()

print("Starting live match monitoring...")
print("=" * 60)

while True:
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Fetching live events from SofaScore API...")
        
        # Fetch all live tennis events
        events = fetch_live_events(scraper)
        print(f"  Found {len(events)} live event(s)")
        
        if len(events) == 0:
            print("  No live matches currently. Waiting...")
            time.sleep(config.POLL_INTERVAL_SECONDS)
            continue
        
        matches_checked = 0
        matches_qualified = 0
        
        # Process each event
        for event in events:
            matches_checked += 1
            if process_match(event, scraper, cache_manager, matches_checked):
                matches_qualified += 1
        
        # Cleanup old cache entries
        live_match_ids = {event.get("id") for event in events}
        cache_manager.cleanup_old_matches(live_match_ids)
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n  Summary: Checked {matches_checked} matches, {matches_qualified} qualified for stats check")
        print(f"  [{timestamp}] Waiting {config.POLL_INTERVAL_SECONDS} seconds before next poll...")
        print("=" * 60)
        
        # Wait before next poll
        time.sleep(config.POLL_INTERVAL_SECONDS)
        
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error in main loop: {e}")
        import traceback
        traceback.print_exc()
        time.sleep(config.POLL_INTERVAL_SECONDS)
        continue

