from src.utils.helpers import to_int


def extract_all_stats(stats):
    """
    Extract all statistics from SofaScore stats response.
    Returns a dictionary with all player statistics.
    """
    # Initialize variables
    p1_first_serve_pct = p2_first_serve_pct = None
    p1_second_serve_pts_pct = p2_second_serve_pts_pct = None
    p1_opp_pts_on_serve = p2_opp_pts_on_serve = None
    p1_bp_faced = p2_bp_faced = None
    p1_bp_saved = p2_bp_saved = None
    p1_aces = p2_aces = None
    p1_double_faults = p2_double_faults = None
    p1_total_points = p2_total_points = None
    p1_service_points_won = p2_service_points_won = None
    p1_receiver_points_won = p2_receiver_points_won = None
    p1_games_won = p2_games_won = None
    p1_first_serve_points = p2_first_serve_points = None
    p1_second_serve_points = p2_second_serve_points = None
    p1_bp_converted = p2_bp_converted = None
    
    # Extract stats
    for group in stats.get("groups", []):
        for item in group.get("statisticsItems", []):
            name = item.get("name") or item.get("title")
            if not name:
                continue
            stat_name = name.lower()
            
            if "first serve" in stat_name and "points" not in stat_name and p1_first_serve_pct is None:
                home_val = item.get("homeValue", 0)
                home_tot = item.get("homeTotal", 1)
                away_val = item.get("awayValue", 0)
                away_tot = item.get("awayTotal", 1)
                p1_first_serve_pct = int((home_val / home_tot) * 100) if home_tot > 0 else 0
                p2_first_serve_pct = int((away_val / away_tot) * 100) if away_tot > 0 else 0
            elif "second serve points" in stat_name and p1_second_serve_pts_pct is None:
                home_val = item.get("homeValue", 0)
                home_tot = item.get("homeTotal", 1)
                away_val = item.get("awayValue", 0)
                away_tot = item.get("awayTotal", 1)
                p1_second_serve_pts_pct = int((home_val / home_tot) * 100) if home_tot > 0 else 0
                p2_second_serve_pts_pct = int((away_val / away_tot) * 100) if away_tot > 0 else 0
            elif "receiver points won" in stat_name and p1_opp_pts_on_serve is None:
                p1_opp_pts_on_serve = int(item.get("awayValue") or item.get("away") or 0)
                p2_opp_pts_on_serve = int(item.get("homeValue") or item.get("home") or 0)
                p1_receiver_points_won = int(item.get("homeValue") or item.get("home") or 0)
                p2_receiver_points_won = int(item.get("awayValue") or item.get("away") or 0)
            elif "break points saved" in stat_name and p1_bp_faced is None:
                val_home = item.get("home")
                val_away = item.get("away")
                if isinstance(val_home, str) and "/" in val_home:
                    parts = val_home.split()
                    if parts:
                        nums = parts[0].split('/')
                        if len(nums) == 2:
                            try:
                                p1_bp_saved = int(nums[0])
                                p1_bp_faced = int(nums[1])
                            except:
                                pass
                    parts2 = val_away.split() if isinstance(val_away, str) else []
                    if parts2:
                        nums2 = parts2[0].split('/')
                        if len(nums2) == 2:
                            try:
                                p2_bp_saved = int(nums2[0])
                                p2_bp_faced = int(nums2[1])
                            except:
                                pass
            elif "aces" in stat_name and p1_aces is None:
                p1_aces = int(item.get("homeValue") or item.get("home") or 0)
                p2_aces = int(item.get("awayValue") or item.get("away") or 0)
            elif "double fault" in stat_name and p1_double_faults is None:
                p1_double_faults = int(item.get("homeValue") or item.get("home") or 0)
                p2_double_faults = int(item.get("awayValue") or item.get("away") or 0)
            elif stat_name == "total" and "points" in group.get("groupName", "").lower() and p1_total_points is None:
                p1_total_points = int(item.get("homeValue") or item.get("home") or 0)
                p2_total_points = int(item.get("awayValue") or item.get("away") or 0)
            elif "service points won" in stat_name and p1_service_points_won is None:
                p1_service_points_won = int(item.get("homeValue") or item.get("home") or 0)
                p2_service_points_won = int(item.get("awayValue") or item.get("away") or 0)
            elif "total won" in stat_name and "games" in group.get("groupName", "").lower() and p1_games_won is None:
                p1_games_won = int(item.get("homeValue") or item.get("home") or 0)
                p2_games_won = int(item.get("awayValue") or item.get("away") or 0)
            elif "first serve points" in stat_name and p1_first_serve_points is None:
                home_val = item.get("homeValue", 0)
                home_tot = item.get("homeTotal", 1)
                away_val = item.get("awayValue", 0)
                away_tot = item.get("awayTotal", 1)
                p1_first_serve_points = int(home_val) if home_tot else 0
                p2_first_serve_points = int(away_val) if away_tot else 0
            elif "second serve points" in stat_name and p1_second_serve_points is None:
                home_val = item.get("homeValue", 0)
                home_tot = item.get("homeTotal", 1)
                away_val = item.get("awayValue", 0)
                away_tot = item.get("awayTotal", 1)
                p1_second_serve_points = int(home_val) if home_tot else 0
                p2_second_serve_points = int(away_val) if away_tot else 0
            elif "break points converted" in stat_name and p1_bp_converted is None:
                p1_bp_converted = int(item.get("homeValue") or item.get("home") or 0)
                p2_bp_converted = int(item.get("awayValue") or item.get("away") or 0)
    
    # Convert all stats to int
    return {
        'p1_first_serve_pct': to_int(p1_first_serve_pct) if p1_first_serve_pct is not None else 0,
        'p2_first_serve_pct': to_int(p2_first_serve_pct) if p2_first_serve_pct is not None else 0,
        'p1_second_serve_pts_pct': to_int(p1_second_serve_pts_pct) if p1_second_serve_pts_pct is not None else 0,
        'p2_second_serve_pts_pct': to_int(p2_second_serve_pts_pct) if p2_second_serve_pts_pct is not None else 0,
        'p1_opp_pts_on_serve': to_int(p1_opp_pts_on_serve) if p1_opp_pts_on_serve is not None else 0,
        'p2_opp_pts_on_serve': to_int(p2_opp_pts_on_serve) if p2_opp_pts_on_serve is not None else 0,
        'p1_bp_faced': to_int(p1_bp_faced) if p1_bp_faced is not None else 0,
        'p2_bp_faced': to_int(p2_bp_faced) if p2_bp_faced is not None else 0,
        'p1_bp_saved': to_int(p1_bp_saved) if p1_bp_saved is not None else 0,
        'p2_bp_saved': to_int(p2_bp_saved) if p2_bp_saved is not None else 0,
        'p1_aces': to_int(p1_aces) if p1_aces is not None else 0,
        'p2_aces': to_int(p2_aces) if p2_aces is not None else 0,
        'p1_double_faults': to_int(p1_double_faults) if p1_double_faults is not None else 0,
        'p2_double_faults': to_int(p2_double_faults) if p2_double_faults is not None else 0,
        'p1_total_points': to_int(p1_total_points) if p1_total_points is not None else 0,
        'p2_total_points': to_int(p2_total_points) if p2_total_points is not None else 0,
        'p1_service_points_won': to_int(p1_service_points_won) if p1_service_points_won is not None else 0,
        'p2_service_points_won': to_int(p2_service_points_won) if p2_service_points_won is not None else 0,
        'p1_receiver_points_won': to_int(p1_receiver_points_won) if p1_receiver_points_won is not None else 0,
        'p2_receiver_points_won': to_int(p2_receiver_points_won) if p2_receiver_points_won is not None else 0,
        'p1_games_won': to_int(p1_games_won) if p1_games_won is not None else 0,
        'p2_games_won': to_int(p2_games_won) if p2_games_won is not None else 0,
        'p1_first_serve_points': to_int(p1_first_serve_points) if p1_first_serve_points is not None else 0,
        'p2_first_serve_points': to_int(p2_first_serve_points) if p2_first_serve_points is not None else 0,
        'p1_second_serve_points': to_int(p1_second_serve_points) if p1_second_serve_points is not None else 0,
        'p2_second_serve_points': to_int(p2_second_serve_points) if p2_second_serve_points is not None else 0,
        'p1_bp_converted': to_int(p1_bp_converted) if p1_bp_converted is not None else 0,
        'p2_bp_converted': to_int(p2_bp_converted) if p2_bp_converted is not None else 0,
    }

