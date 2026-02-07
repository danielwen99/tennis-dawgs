import config
import json


def fetch_live_events(scraper):
    """Fetch all live tennis events from SofaScore API."""
    try:
        response = scraper.get(config.SOFASCORE_LIVE_EVENTS_URL)
        if response.status_code == 200:
            events_data = response.json()
            return events_data.get("events", [])
        else:
            print(f"  Response status: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching live events: {e}")
        return []


def fetch_match_stats(scraper, match_id):
    """Fetch statistics for a specific match."""
    try:
        stats_url = config.SOFASCORE_STATS_URL_TEMPLATE.format(match_id=match_id)
        stats_resp = scraper.get(stats_url)
        if stats_resp.status_code == 200:
            stats_data = stats_resp.json()
            if "statistics" in stats_data and stats_data["statistics"]:
                return stats_data["statistics"][0]
        return None
    except Exception as e:
        print(f"Error fetching stats for event {match_id}: {e}")
        return None


def fetch_event_details(scraper, match_id):
    """Fetch full event details which might include serve information."""
    try:
        url = f"https://api.sofascore.com/api/v1/event/{match_id}"
        response = scraper.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error fetching event details: {e}")
        return None


def get_first_server_from_api(scraper, match_id, set_number=1):
    """
    Get who served first in a set from SofaScore API.
    
    Args:
        scraper: CloudScraper session
        match_id: Match ID
        set_number: Set number (1, 2, 3, etc.)
    
    Returns:
        'p1' if home team served first, 'p2' if away team served first, None if not found
    """
    try:
        event_details = fetch_event_details(scraper, match_id)
        if not event_details:
            return None
        
        event = event_details.get("event", {})
        first_to_serve = event.get("firstToServe")
        
        if first_to_serve is None:
            return None
        
        # firstToServe: 1 = home team (p1), 2 = away team (p2)
        # In tennis, first server alternates each set:
        # Set 1: firstToServe determines who serves first
        # Set 2: opposite of set 1
        # Set 3: same as set 1 (if needed)
        
        if set_number == 1:
            # Set 1: use firstToServe directly
            return "p1" if first_to_serve == 1 else "p2"
        elif set_number == 2:
            # Set 2: opposite of set 1
            return "p2" if first_to_serve == 1 else "p1"
        else:
            # Set 3+: alternate (same as set 1)
            return "p1" if first_to_serve == 1 else "p2"
            
    except Exception as e:
        print(f"Error getting first server from API: {e}")
        return None

