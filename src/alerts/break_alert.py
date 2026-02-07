import datetime
from src.alerts.telegram import send_telegram_message
from src.api.polymarket import fetch_polymarket_odds
from src.processors.stats_extractor import extract_all_stats
from src.analysis.player_comparison import determine_better_player
from src.utils.helpers import safe_ratio, format_odds_decimal
from src.api.sofascore import fetch_match_stats
from src.detection.break_detector import detect_break, detect_break_from_stats, should_send_break_alert, determine_first_server
from src.api.sofascore import get_first_server_from_api


def create_break_alert_message(player1, player2, p1_ranking, p2_ranking, tour_type,
                               sets_home, sets_away, set2_games_home, set2_games_away,
                               match_id, starting_odds, odds_str, breaking_player,
                               p1_broke, stats_dict):
    """Create the break alert message."""
    # Calculate metrics (same as 1-1 alert)
    p1_bp_saved_pct = safe_ratio(stats_dict['p1_bp_saved'], stats_dict['p1_bp_faced']) if stats_dict['p1_bp_faced'] > 0 else 0
    p2_bp_saved_pct = safe_ratio(stats_dict['p2_bp_saved'], stats_dict['p2_bp_faced']) if stats_dict['p2_bp_faced'] > 0 else 0
    
    p1_service_pts_total = stats_dict['p1_service_points_won'] + stats_dict['p1_opp_pts_on_serve']
    p2_service_pts_total = stats_dict['p2_service_points_won'] + stats_dict['p2_opp_pts_on_serve']
    p1_service_pts_won_pct = safe_ratio(stats_dict['p1_service_points_won'], p1_service_pts_total) if p1_service_pts_total > 0 else 0
    p2_service_pts_won_pct = safe_ratio(stats_dict['p2_service_points_won'], p2_service_pts_total) if p2_service_pts_total > 0 else 0
    
    p1_return_pts_total = stats_dict['p1_receiver_points_won'] + stats_dict['p2_service_points_won']
    p2_return_pts_total = stats_dict['p2_receiver_points_won'] + stats_dict['p1_service_points_won']
    p1_return_pts_won_pct = safe_ratio(stats_dict['p1_receiver_points_won'], p1_return_pts_total) if p1_return_pts_total > 0 else 0
    p2_return_pts_won_pct = safe_ratio(stats_dict['p2_receiver_points_won'], p2_return_pts_total) if p2_return_pts_total > 0 else 0
    
    total_pts_played = stats_dict['p1_total_points'] + stats_dict['p2_total_points']
    p1_total_pts_won_pct = safe_ratio(stats_dict['p1_total_points'], total_pts_played) if total_pts_played > 0 else 0
    p2_total_pts_won_pct = safe_ratio(stats_dict['p2_total_points'], total_pts_played) if total_pts_played > 0 else 0
    
    # Determine better player
    p1_stats_dict = {
        'first_serve_pct': stats_dict['p1_first_serve_pct'],
        'second_serve_pct': stats_dict['p1_second_serve_pts_pct'],
        'opp_pts_on_serve': stats_dict['p1_opp_pts_on_serve'],
        'bp_saved_pct': p1_bp_saved_pct,
        'bp_converted': stats_dict['p1_bp_converted'],
        'total_points': stats_dict['p1_total_points'],
        'service_points_won': stats_dict['p1_service_points_won'],
        'receiver_points_won': stats_dict['p1_receiver_points_won'],
        'games_won': stats_dict['p1_games_won'],
        'aces': stats_dict['p1_aces'],
        'double_faults': stats_dict['p1_double_faults']
    }
    p2_stats_dict = {
        'first_serve_pct': stats_dict['p2_first_serve_pct'],
        'second_serve_pct': stats_dict['p2_second_serve_pts_pct'],
        'opp_pts_on_serve': stats_dict['p2_opp_pts_on_serve'],
        'bp_saved_pct': p2_bp_saved_pct,
        'bp_converted': stats_dict['p2_bp_converted'],
        'total_points': stats_dict['p2_total_points'],
        'service_points_won': stats_dict['p2_service_points_won'],
        'receiver_points_won': stats_dict['p2_receiver_points_won'],
        'games_won': stats_dict['p2_games_won'],
        'aces': stats_dict['p2_aces'],
        'double_faults': stats_dict['p2_double_faults']
    }
    better_player = determine_better_player(p1_stats_dict, p2_stats_dict)
    p1_emoji = "🟢" if better_player == 'p1' else ""
    p2_emoji = "🟢" if better_player == 'p2' else ""
    
    # Format message
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    p1_rank_str = f"#{p1_ranking}" if p1_ranking else "N/A"
    p2_rank_str = f"#{p2_ranking}" if p2_ranking else "N/A"
    sets_score = f"{sets_home}-{sets_away} sets"
    set2_score = f"{set2_games_home}-{set2_games_away} games"
    
    return f"""🔴 <b>BREAK ALERT - Player Down a Set Breaks Serve!</b>

<b>{player1}</b> {p1_rank_str} vs <b>{player2}</b> {p2_rank_str}
Tournament: {tour_type}
Score: {sets_score}, 2nd Set: {set2_score}
Match ID: {match_id}
Odds: {starting_odds} → {odds_str} (Starting → Live)

<b>Break Details:</b>
• {breaking_player} was down {sets_home if p1_broke else sets_away}-{sets_away if p1_broke else sets_home} sets
• Broke serve in 2nd set at {set2_score}

<b>Key Stats:</b>
• <b>P1 ({player1}) {p1_emoji}:</b>
  - Service points won: {int(p1_service_pts_won_pct*100)}% ({stats_dict['p1_service_points_won']}/{p1_service_pts_total})
  - Return points won: {int(p1_return_pts_won_pct*100)}% ({stats_dict['p1_receiver_points_won']}/{p1_return_pts_total})
  - Total points won: {int(p1_total_pts_won_pct*100)}% ({stats_dict['p1_total_points']}/{total_pts_played})
  - Break points saved: {int(p1_bp_saved_pct*100)}% ({stats_dict['p1_bp_saved']}/{stats_dict['p1_bp_faced']})
  - Break points converted: {stats_dict['p1_bp_converted']}
  - Games won: {stats_dict['p1_games_won']}

• <b>P2 ({player2}) {p2_emoji}:</b>
  - Service points won: {int(p2_service_pts_won_pct*100)}% ({stats_dict['p2_service_points_won']}/{p2_service_pts_total})
  - Return points won: {int(p2_return_pts_won_pct*100)}% ({stats_dict['p2_receiver_points_won']}/{p2_return_pts_total})
  - Total points won: {int(p2_total_pts_won_pct*100)}% ({stats_dict['p2_total_points']}/{total_pts_played})
  - Break points saved: {int(p2_bp_saved_pct*100)}% ({stats_dict['p2_bp_saved']}/{stats_dict['p2_bp_faced']})
  - Break points converted: {stats_dict['p2_bp_converted']}
  - Games won: {stats_dict['p2_games_won']}

Time: {timestamp}"""


def send_break_alert(match_id, player1, player2, p1_ranking, p2_ranking, tour_type,
                    sets_home, sets_away, set2_games_home, set2_games_away,
                    scraper, cache_manager):
    """Send break alert if conditions are met."""
    match_cache = cache_manager.telegram_sent_cache.get(match_id, {})
    if match_cache.get("break_alert_sent", False):
        return False
    
    # Fetch stats to get break points converted (more reliable than game score inference)
    stats = fetch_match_stats(scraper, match_id)
    if not stats:
        print(f"    ⚠ No statistics available for break detection")
        return False
    
    stats_dict = extract_all_stats(stats)
    p1_bp_converted = stats_dict['p1_bp_converted']
    p2_bp_converted = stats_dict['p2_bp_converted']
    
    # Get previous break points converted from cache
    prev_breaks = cache_manager.previous_breaks_cache.get(match_id, {})
    prev_p1_bp_converted = prev_breaks.get("prev_p1_bp_converted")
    prev_p2_bp_converted = prev_breaks.get("prev_p2_bp_converted")
    
    # Detect break using stats (more reliable)
    p1_broke, p2_broke = detect_break_from_stats(
        p1_bp_converted, p2_bp_converted,
        prev_p1_bp_converted, prev_p2_bp_converted,
        sets_home, sets_away
    )
    
    # Update break points cache for next check
    if match_id not in cache_manager.previous_breaks_cache:
        cache_manager.previous_breaks_cache[match_id] = {}
    cache_manager.previous_breaks_cache[match_id]["prev_p1_bp_converted"] = p1_bp_converted
    cache_manager.previous_breaks_cache[match_id]["prev_p2_bp_converted"] = p2_bp_converted
    
    # Check if should alert
    p1_down_set = sets_home == 0 and sets_away == 1
    p2_down_set = sets_home == 1 and sets_away == 0
    
    if not should_send_break_alert(p1_broke, p2_broke, p1_down_set, p2_down_set,
                                   set2_games_home, set2_games_away):
        return False
    
    breaking_player = player1 if p1_broke else player2
    print(f"    🎾 BREAK DETECTED: {breaking_player} broke serve in 2nd set!")
    print(f"    Break points converted: P1={p1_bp_converted} (prev={prev_p1_bp_converted}), P2={p2_bp_converted} (prev={prev_p2_bp_converted})")
    
    # Stats already fetched above
    
    # Fetch odds
    p1_prob, p2_prob = fetch_polymarket_odds(player1, player2, scraper)
    if p1_prob is not None and p2_prob is not None:
        p1_decimal, p2_decimal = format_odds_decimal(p1_prob, p2_prob)
        if p1_decimal is not None and p2_decimal is not None:
            odds_str = f"{p1_decimal:.2f}/{p2_decimal:.2f}"
            starting_odds = cache_manager.starting_odds_cache.get(match_id, odds_str)
        else:
            odds_str = "N/A"
            starting_odds = "N/A"
    else:
        odds_str = "N/A"
        starting_odds = "N/A"
    
    # Create and send message
    telegram_msg = create_break_alert_message(
        player1, player2, p1_ranking, p2_ranking, tour_type,
        sets_home, sets_away, set2_games_home, set2_games_away,
        match_id, starting_odds, odds_str, breaking_player,
        p1_broke, stats_dict
    )
    
    print(f"    Sending break alert with full stats...")
    if send_telegram_message(telegram_msg, scraper):
        if match_id not in cache_manager.telegram_sent_cache:
            cache_manager.telegram_sent_cache[match_id] = {}
        cache_manager.telegram_sent_cache[match_id]["break_alert_sent"] = True
        cache_manager.telegram_sent_cache[match_id]["last_sent_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return True
    return False

