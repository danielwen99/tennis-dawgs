import config


def detect_tournament_type(event):
    """Detect tournament type (ATP, WTA, Challenger, ITF, UTR) from event data."""
    tournament = event.get("tournament", {})
    category = event.get("category", {})
    tournament_category = tournament.get("category", {}) if tournament else {}
    
    # Try tournament.name first
    tournament_name = None
    if tournament and tournament.get("name"):
        tournament_name = tournament.get("name")
    elif category and category.get("name"):
        tournament_name = category.get("name")
    elif tournament_category and tournament_category.get("name"):
        tournament_name = tournament_category.get("name")
    elif event.get("league", {}).get("name"):
        tournament_name = event.get("league", {}).get("name")
    
    # Look for tournament type information in various fields
    search_text = ""
    if tournament_name:
        search_text += tournament_name.lower() + " "
    if tournament_category:
        search_text += str(tournament_category.get("slug", "")).lower() + " "
        search_text += str(tournament_category.get("name", "")).lower() + " "
    if tournament:
        search_text += str(tournament.get("slug", "")).lower() + " "
        search_text += str(tournament.get("uniqueTournament", {}).get("name", "")).lower() + " "
    if category:
        search_text += str(category.get("slug", "")).lower() + " "
    
    # Identify tournament type
    tour_type = "Unknown"
    if "challenger" in search_text:
        tour_type = "Challenger"
    elif "atp" in search_text:
        tour_type = "ATP"
    elif "wta" in search_text:
        tour_type = "WTA"
    elif "utr" in search_text:
        tour_type = "UTR"
    elif "itf" in search_text or "futures" in search_text:
        tour_type = "ITF"
    
    return tour_type, tournament_name


def is_allowed_tournament(tour_type):
    """Check if tournament type is in allowed list."""
    return tour_type in config.ALLOWED_TOURNAMENTS

