def determine_first_server(set2_games_home, set2_games_away):
    """
    Determine who served first in 2nd set based on game count.
    This is a fallback method when API data is not available.
    """
    total_games = set2_games_home + set2_games_away
    if total_games > 0:
        if total_games % 2 == 1:
            # Odd total: one player served one more time
            if set2_games_home > set2_games_away:
                return "p1"
            else:
                return "p2"
        else:
            # Even total: both served equal times, can't determine accurately
            # Return None to indicate uncertainty
            return None
    else:
        # No games yet, can't determine
        return None


def detect_break_from_stats(p1_bp_converted, p2_bp_converted, prev_p1_bp_converted, prev_p2_bp_converted,
                            sets_home, sets_away):
    """
    Detect if a break occurred by checking if break points converted increased.
    This is more reliable than inferring from game scores.
    
    Returns (p1_broke, p2_broke) tuple.
    """
    p1_broke = False
    p2_broke = False
    
    if prev_p1_bp_converted is None or prev_p2_bp_converted is None:
        return p1_broke, p2_broke
    
    # Check if break points converted increased (indicates a break occurred)
    p1_bp_increased = p1_bp_converted > prev_p1_bp_converted
    p2_bp_increased = p2_bp_converted > prev_p2_bp_converted
    
    # Check if a player is down a set
    p1_down_set = sets_home == 0 and sets_away == 1
    p2_down_set = sets_home == 1 and sets_away == 0
    
    # A break occurred if break points converted increased
    if p1_bp_increased and p1_down_set:
        p1_broke = True
    if p2_bp_increased and p2_down_set:
        p2_broke = True
    
    return p1_broke, p2_broke


def detect_break(set2_games_home, set2_games_away, prev_set2_games_home, prev_set2_games_away,
                 first_server, sets_home, sets_away):
    """
    Detect if a break occurred in the 2nd set.
    Returns (p1_broke, p2_broke) tuple.
    
    DEPRECATED: This method infers breaks from game scores, which is error-prone.
    Use detect_break_from_stats() instead for more reliable detection.
    
    Args:
        first_server: 'p1', 'p2', or None. If None, break detection cannot be performed accurately.
    """
    p1_broke = False
    p2_broke = False
    
    if prev_set2_games_home is None or prev_set2_games_away is None:
        return p1_broke, p2_broke
    
    # Need first_server to accurately detect breaks
    if first_server is None:
        return p1_broke, p2_broke
    
    # Calculate total games before and after
    prev_total = prev_set2_games_home + prev_set2_games_away
    curr_total = set2_games_home + set2_games_away
    
    # Only check if exactly one game was played (total increased by 1)
    if curr_total == prev_total + 1:
        game_number = curr_total  # The game that just finished
        
        # Determine who served this game
        if first_server == "p1":
            # P1 serves games 1,3,5,7... (odd numbers)
            # P2 serves games 2,4,6,8... (even numbers)
            serving_player = "p1" if game_number % 2 == 1 else "p2"
        else:  # first_server == "p2"
            # P2 serves games 1,3,5,7... (odd numbers)
            # P1 serves games 2,4,6,8... (even numbers)
            serving_player = "p2" if game_number % 2 == 1 else "p1"
        
        # Check which player's games increased
        p1_games_increased = set2_games_home > prev_set2_games_home
        p2_games_increased = set2_games_away > prev_set2_games_away
        
        # Check if a player is down a set
        p1_down_set = sets_home == 0 and sets_away == 1
        p2_down_set = sets_home == 1 and sets_away == 0
        
        # A break occurs when the receiving player (non-serving player) wins
        # IMPORTANT: If the serving player's games increased, that's a HOLD, not a break
        if serving_player == "p1":
            # P1 was serving
            if p1_games_increased:
                # P1 won while serving = P1 held serve (NOT a break)
                pass
            elif p2_games_increased and p2_down_set:
                # P2 won while P1 was serving = P2 broke P1
                p2_broke = True
        else:  # serving_player == "p2"
            # P2 was serving
            if p2_games_increased:
                # P2 won while serving = P2 held serve (NOT a break)
                pass
            elif p1_games_increased and p1_down_set:
                # P1 won while P2 was serving = P1 broke P2
                p1_broke = True
    
    return p1_broke, p2_broke


def should_send_break_alert(p1_broke, p2_broke, p1_down_set, p2_down_set,
                            set2_games_home, set2_games_away):
    """
    Determine if break alert should be sent.
    Alert if player who lost first set breaks serve AND is now tied or leading in 2nd set.
    """
    if p1_broke and p1_down_set:
        # P1 lost first set and broke serve - alert if P1 is now tied or leading in 2nd set
        if set2_games_home >= set2_games_away:
            return True
    elif p2_broke and p2_down_set:
        # P2 lost first set and broke serve - alert if P2 is now tied or leading in 2nd set
        if set2_games_away >= set2_games_home:
            return True
    return False
