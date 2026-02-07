def determine_better_player(p1_stats, p2_stats):
    """
    Determine which player has better statistics overall.
    Returns 'p1', 'p2', or 'tie' based on key performance metrics.
    """
    p1_score = 0
    p2_score = 0
    
    # Compare each stat (higher is better, except for opp_pts_on_serve and double_faults)
    if p1_stats.get('first_serve_pct', 0) > p2_stats.get('first_serve_pct', 0):
        p1_score += 1
    elif p2_stats.get('first_serve_pct', 0) > p1_stats.get('first_serve_pct', 0):
        p2_score += 1
    
    if p1_stats.get('second_serve_pct', 0) > p2_stats.get('second_serve_pct', 0):
        p1_score += 1
    elif p2_stats.get('second_serve_pct', 0) > p1_stats.get('second_serve_pct', 0):
        p2_score += 1
    
    if p1_stats.get('opp_pts_on_serve', 999) < p2_stats.get('opp_pts_on_serve', 999):
        p1_score += 1
    elif p2_stats.get('opp_pts_on_serve', 999) < p1_stats.get('opp_pts_on_serve', 999):
        p2_score += 1
    
    if p1_stats.get('bp_saved_pct', 0) > p2_stats.get('bp_saved_pct', 0):
        p1_score += 1
    elif p2_stats.get('bp_saved_pct', 0) > p1_stats.get('bp_saved_pct', 0):
        p2_score += 1
    
    if p1_stats.get('bp_converted', 0) > p2_stats.get('bp_converted', 0):
        p1_score += 1
    elif p2_stats.get('bp_converted', 0) > p1_stats.get('bp_converted', 0):
        p2_score += 1
    
    if p1_stats.get('total_points', 0) > p2_stats.get('total_points', 0):
        p1_score += 1
    elif p2_stats.get('total_points', 0) > p1_stats.get('total_points', 0):
        p2_score += 1
    
    if p1_stats.get('service_points_won', 0) > p2_stats.get('service_points_won', 0):
        p1_score += 1
    elif p2_stats.get('service_points_won', 0) > p1_stats.get('service_points_won', 0):
        p2_score += 1
    
    if p1_stats.get('receiver_points_won', 0) > p2_stats.get('receiver_points_won', 0):
        p1_score += 1
    elif p2_stats.get('receiver_points_won', 0) > p1_stats.get('receiver_points_won', 0):
        p2_score += 1
    
    if p1_stats.get('games_won', 0) > p2_stats.get('games_won', 0):
        p1_score += 1
    elif p2_stats.get('games_won', 0) > p1_stats.get('games_won', 0):
        p2_score += 1
    
    if p1_stats.get('aces', 0) > p2_stats.get('aces', 0):
        p1_score += 1
    elif p2_stats.get('aces', 0) > p1_stats.get('aces', 0):
        p2_score += 1
    
    if p1_stats.get('double_faults', 999) < p2_stats.get('double_faults', 999):
        p1_score += 1
    elif p2_stats.get('double_faults', 999) < p1_stats.get('double_faults', 999):
        p2_score += 1
    
    # Determine winner
    if p1_score > p2_score:
        return 'p1'
    elif p2_score > p1_score:
        return 'p2'
    else:
        return 'tie'

