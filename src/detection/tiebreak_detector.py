def is_tiebreak_in_third_set(sets_home, sets_away, set3_games_home, set3_games_away, status_desc):
    """
    Detect if a tiebreak is happening in the 3rd set.
    A tiebreak occurs when the score reaches 6-6 in games.
    
    Returns True if tiebreak is detected, False otherwise.
    """
    # Must be in 3rd set
    if "3rd set" not in status_desc.lower() and "third set" not in status_desc.lower():
        return False
    
    # Must be 1-1 in sets (deciding set)
    if sets_home != 1 or sets_away != 1:
        return False
    
    # Check if games are at 6-6 (tiebreak condition)
    if set3_games_home is not None and set3_games_away is not None:
        if set3_games_home == 6 and set3_games_away == 6:
            return True
    
    return False

