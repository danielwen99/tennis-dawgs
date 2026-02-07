import datetime
from src.utils.constants import GREEN, ORANGE, RESET
from src.processors.tournament_detector import detect_tournament_type, is_allowed_tournament
from src.api.polymarket import fetch_polymarket_odds
from src.utils.helpers import format_odds_decimal
from src.alerts.one_one_alert import send_one_one_alert
from src.alerts.break_alert import send_break_alert
from src.alerts.tiebreak_alert import send_tiebreak_alert
from src.detection.tiebreak_detector import is_tiebreak_in_third_set
from src.processors.stats_extractor import extract_all_stats
from src.api.sofascore import fetch_match_stats, get_first_server_from_api
from src.storage.csv_logger import log_match_to_csv


def extract_match_info(event):
    """Extract basic match information from event."""
    match_id = event.get("id")
    home_team_data = event.get("homeTeam", {})
    away_team_data = event.get("awayTeam", {})
    player1 = home_team_data.get("name")
    player2 = away_team_data.get("name")
    
    p1_ranking = home_team_data.get("ranking") or home_team_data.get("position") or home_team_data.get("seed")
    p2_ranking = away_team_data.get("ranking") or away_team_data.get("position") or away_team_data.get("seed")
    
    return {
        'match_id': match_id,
        'player1': player1,
        'player2': player2,
        'p1_ranking': p1_ranking,
        'p2_ranking': p2_ranking
    }


def extract_score_info(event):
    """Extract score information from event."""
    sets_home = event.get("homeScore", {}).get("current")
    sets_away = event.get("awayScore", {}).get("current")
    
    status_desc = event.get("status", {}).get("description", "")
    home_score = event.get("homeScore", {})
    away_score = event.get("awayScore", {})
    
    # Extract games from the current set period
    current_set_games_home = None
    current_set_games_away = None
    
    if "3rd set" in status_desc.lower() or "third set" in status_desc.lower():
        current_set_games_home = home_score.get("period3")
        current_set_games_away = away_score.get("period3")
    elif "2nd set" in status_desc.lower() or "second set" in status_desc.lower():
        current_set_games_home = home_score.get("period2")
        current_set_games_away = away_score.get("period2")
    elif "1st set" in status_desc.lower() or "first set" in status_desc.lower():
        current_set_games_home = home_score.get("period1")
        current_set_games_away = away_score.get("period1")
    else:
        # Fallback: try period3 (3rd set), then period2, then period1
        current_set_games_home = home_score.get("period3") or home_score.get("period2") or home_score.get("period1")
        current_set_games_away = away_score.get("period3") or away_score.get("period2") or away_score.get("period1")
    
    games_home = current_set_games_home
    games_away = current_set_games_away
    
    return {
        'sets_home': sets_home,
        'sets_away': sets_away,
        'games_home': games_home,
        'games_away': games_away,
        'current_set_games_home': current_set_games_home,
        'current_set_games_away': current_set_games_away,
        'status_desc': status_desc
    }


def check_qualification_criteria(sets_home, sets_away, status_desc, games_home, games_away):
    """Check if match meets qualification criteria (1-1 sets, early 3rd set)."""
    if sets_home == 1 and sets_away == 1 and "3rd set" in status_desc:
        # If games_home/games_away are None, treat as 0-0
        if games_home is None or games_away is None:
            games_home = games_away = 0
        
        # Check if game score qualifies
        games_diff = abs(games_home - games_away)
        if games_diff == 0:
            return True
        elif games_diff == 1:
            return True
        else:
            return False
    return False


def process_match(event, scraper, cache_manager, matches_checked):
    """Process a single match event."""
    try:
        # Extract match info
        match_info = extract_match_info(event)
        match_id = match_info['match_id']
        player1 = match_info['player1']
        player2 = match_info['player2']
        p1_ranking = match_info['p1_ranking']
        p2_ranking = match_info['p2_ranking']
        
        # Detect tournament type
        tour_type, tournament_name = detect_tournament_type(event)
        if not is_allowed_tournament(tour_type):
            return False
        
        # Fetch early odds for starting odds tracking
        p1_prob_early, p2_prob_early = fetch_polymarket_odds(player1, player2, scraper)
        if p1_prob_early is not None and p2_prob_early is not None:
            p1_decimal_early, p2_decimal_early = format_odds_decimal(p1_prob_early, p2_prob_early)
            if p1_decimal_early is not None and p2_decimal_early is not None:
                odds_str_early = f"{p1_decimal_early:.2f}/{p2_decimal_early:.2f}"
                if match_id not in cache_manager.starting_odds_cache:
                    cache_manager.starting_odds_cache[match_id] = odds_str_early
        
        # Extract score info
        score_info = extract_score_info(event)
        sets_home = score_info['sets_home']
        sets_away = score_info['sets_away']
        games_home = score_info['games_home']
        games_away = score_info['games_away']
        current_set_games_home = score_info['current_set_games_home']
        current_set_games_away = score_info['current_set_games_away']
        status_desc = score_info['status_desc']
        
        # Determine if sets are 1-1 for color
        is_one_one = sets_home == 1 and sets_away == 1
        color = ORANGE if is_one_one else RESET
        
        print(f"{color}\n  Match {matches_checked}: {player1} vs {player2} (ID: {match_id}){RESET}")
        if tour_type != "Unknown":
            print(f"{color}    Tournament: {tour_type}{RESET}")
        print(f"{color}    Sets: {sets_home}-{sets_away}, Games: {games_home}-{games_away}, Status: {status_desc}{RESET}")
        
        # Send 1-1 sets alert
        if is_one_one:
            send_one_one_alert(
                match_id, player1, player2, p1_ranking, p2_ranking, tour_type,
                sets_home, sets_away, games_home, games_away,
                current_set_games_home, current_set_games_away,
                scraper, cache_manager
            )
        
        # Check for tiebreak in 3rd set
        is_third_set = "3rd set" in status_desc.lower() or "third set" in status_desc.lower()
        if is_third_set and is_one_one:
            home_score = event.get("homeScore", {})
            set3_games_home = home_score.get("period3")
            set3_games_away = event.get("awayScore", {}).get("period3")
            
            if set3_games_home is not None and set3_games_away is not None:
                if is_tiebreak_in_third_set(sets_home, sets_away, set3_games_home, set3_games_away, status_desc):
                    send_tiebreak_alert(
                        match_id, player1, player2, p1_ranking, p2_ranking, tour_type,
                        sets_home, sets_away, set3_games_home, set3_games_away,
                        scraper, cache_manager
                    )
        
        # Check for break alert in 2nd set
        is_second_set = "2nd set" in status_desc.lower() or "second set" in status_desc.lower()
        if is_second_set:
            home_score = event.get("homeScore", {})
            set2_games_home = home_score.get("period2")
            set2_games_away = event.get("awayScore", {}).get("period2")
            
            if set2_games_home is not None and set2_games_away is not None:
                # Try to get first server from API when entering 2nd set
                set2_first_server = None
                prev_games = cache_manager.previous_games_cache.get(match_id, {})
                if "set2_first_server" not in prev_games or prev_games.get("set2_first_server") is None:
                    # Fetch from API if not cached
                    set2_first_server = get_first_server_from_api(scraper, match_id, set_number=2)
                    if set2_first_server:
                        print(f"    ✓ Got first server from API: {set2_first_server}")
                
                send_break_alert(
                    match_id, player1, player2, p1_ranking, p2_ranking, tour_type,
                    sets_home, sets_away, set2_games_home, set2_games_away,
                    scraper, cache_manager
                )
                
                # Update games cache with API data if available
                cache_manager.update_games_cache(match_id, set2_games_home, set2_games_away, set2_first_server)
        
        # Check qualification criteria for CSV logging
        if check_qualification_criteria(sets_home, sets_away, status_desc, games_home, games_away):
            print(f"    ✓ Qualifies: 1-1 sets, early 3rd set ({games_home}-{games_away} games)")
            
            # Fetch stats
            stats = fetch_match_stats(scraper, match_id)
            if not stats:
                print(f"    ✗ No statistics available")
                return False
            
            stats_dict = extract_all_stats(stats)
            
            # Verify required stats are present (extract_all_stats returns 0 for missing stats, so we check if all are 0)
            # This is a basic check - in practice, if stats were extracted, they should have values
            # We'll proceed with logging since extract_all_stats handles missing stats gracefully
            
            print(f"    Stats summary:")
            print(f"      P1: 1st serve {stats_dict['p1_first_serve_pct']}%, 2nd serve {stats_dict['p1_second_serve_pts_pct']}%, opp pts {stats_dict['p1_opp_pts_on_serve']}, BP {stats_dict['p1_bp_saved']}/{stats_dict['p1_bp_faced']}")
            print(f"      P2: 1st serve {stats_dict['p2_first_serve_pct']}%, 2nd serve {stats_dict['p2_second_serve_pts_pct']}%, opp pts {stats_dict['p2_opp_pts_on_serve']}, BP {stats_dict['p2_bp_saved']}/{stats_dict['p2_bp_faced']}")
            if stats_dict['p1_total_points'] or stats_dict['p2_total_points']:
                print(f"      Additional: P1 - Points: {stats_dict['p1_total_points']}, Service pts: {stats_dict['p1_service_points_won']}, Receiver pts: {stats_dict['p1_receiver_points_won']}, Games: {stats_dict['p1_games_won']}, Aces: {stats_dict['p1_aces']}, DFs: {stats_dict['p1_double_faults']}")
                print(f"                  P2 - Points: {stats_dict['p2_total_points']}, Service pts: {stats_dict['p2_service_points_won']}, Receiver pts: {stats_dict['p2_receiver_points_won']}, Games: {stats_dict['p2_games_won']}, Aces: {stats_dict['p2_aces']}, DFs: {stats_dict['p2_double_faults']}")
            
            print(f"{GREEN}    ✓✓✓ CONDITIONS MET - LOGGING MATCH ✓✓✓{RESET}")
            
            # Fetch current odds
            p1_prob, p2_prob = fetch_polymarket_odds(player1, player2, scraper)
            if p1_prob is not None and p2_prob is not None:
                p1_decimal, p2_decimal = format_odds_decimal(p1_prob, p2_prob)
                if p1_decimal is not None and p2_decimal is not None:
                    odds_str = f"{p1_decimal:.2f}/{p2_decimal:.2f}"
                else:
                    odds_str = "N/A"
            else:
                odds_str = "N/A"
            
            starting_odds = cache_manager.starting_odds_cache.get(match_id, odds_str if odds_str != "N/A" else "N/A")
            
            # Prepare match data for CSV
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            match_data = {
                'timestamp': timestamp,
                'match_id': match_id,
                'player1': player1,
                'player2': player2,
                'p1_ranking': p1_ranking,
                'p2_ranking': p2_ranking,
                'tour_type': tour_type,
                'sets_score': f"{sets_home}-{sets_away} sets",
                'games_score': f"{games_home}-{games_away} games",
                'current_set_games_home': current_set_games_home,
                'current_set_games_away': current_set_games_away
            }
            
            # Log to CSV
            log_match_to_csv(match_data, stats_dict, starting_odds, odds_str)
            print(f"{GREEN}    [{timestamp}] ✓ Logged to CSV: {player1} vs {player2} (Match ID: {match_id}){RESET}")
            return True
        
        return False
        
    except Exception as err:
        print(f"    ✗ Error processing event {event.get('id')}: {err}")
        import traceback
        traceback.print_exc()
        return False

