class CacheManager:
    """Manages all caches for the application."""
    
    def __init__(self):
        self.starting_odds_cache = {}
        self.telegram_sent_cache = {}
        self.previous_games_cache = {}
        self.previous_breaks_cache = {}  # Track break points converted to detect actual breaks
    
    def cleanup_old_matches(self, live_match_ids):
        """Remove cache entries for matches that are no longer live."""
        # Cleanup telegram cache
        old_match_ids = set(self.telegram_sent_cache.keys()) - live_match_ids
        if old_match_ids:
            for old_id in old_match_ids:
                del self.telegram_sent_cache[old_id]
            print(f"  Cleaned up {len(old_match_ids)} old match(es) from Telegram cache")
        
        # Cleanup previous games cache
        old_games_match_ids = set(self.previous_games_cache.keys()) - live_match_ids
        if old_games_match_ids:
            for old_id in old_games_match_ids:
                del self.previous_games_cache[old_id]
            print(f"  Cleaned up {len(old_games_match_ids)} old match(es) from games cache")
        
        # Cleanup previous breaks cache
        old_breaks_match_ids = set(self.previous_breaks_cache.keys()) - live_match_ids
        if old_breaks_match_ids:
            for old_id in old_breaks_match_ids:
                del self.previous_breaks_cache[old_id]
    
    def update_games_cache(self, match_id, set2_games_home, set2_games_away, set2_first_server=None):
        """
        Update the games cache for a match.
        
        Args:
            match_id: Match ID
            set2_games_home: Games won by home team in set 2
            set2_games_away: Games won by away team in set 2
            set2_first_server: Who served first in set 2 ('p1' or 'p2'), from API if available
        """
        if match_id not in self.previous_games_cache:
            self.previous_games_cache[match_id] = {}
        self.previous_games_cache[match_id]["prev_set2_games_home"] = set2_games_home
        self.previous_games_cache[match_id]["prev_set2_games_away"] = set2_games_away
        
        # Store first server if provided (from API), otherwise try to infer
        if set2_first_server:
            self.previous_games_cache[match_id]["set2_first_server"] = set2_first_server
        elif "set2_first_server" not in self.previous_games_cache[match_id]:
            # Fallback: try to determine from game count (less accurate)
            from src.detection.break_detector import determine_first_server
            inferred = determine_first_server(set2_games_home, set2_games_away)
            if inferred:
                self.previous_games_cache[match_id]["set2_first_server"] = inferred
            else:
                # Can't determine, will need to wait for API data or more games
                self.previous_games_cache[match_id]["set2_first_server"] = None

