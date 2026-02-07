import json
from src.utils.helpers import normalize_name
import config


def fetch_polymarket_odds(player1, player2, scraper):
    """
    Fetch live odds from Polymarket for a tennis match.
    Returns tuple (p1_prob, p2_prob) as floats (0-1), or (None, None) if not found.
    """
    try:
        # Search Polymarket for the match
        query = f"{player1} {player2}"
        print(f"    Fetching Polymarket odds for: {query}...")
        
        resp = scraper.get(config.POLYMARKET_SEARCH_URL, params={"q": query}, timeout=10)
        if resp.status_code != 200:
            print(f"    ✗ Polymarket API error: {resp.status_code}")
            return None, None
        
        data = resp.json()
        
        # Check if we have events
        events = data.get("events", [])
        if not events:
            print(f"    ✗ No Polymarket event found for this match")
            return None, None
        
        # Find the event that contains both player names in the title
        # Use normalized names to handle special characters
        p1_lastname = normalize_name(player1)
        p2_lastname = normalize_name(player2)
        matching_event = None
        for event in events:
            title = event.get("title", "").lower()
            title_normalized = normalize_name(title)
            p1_lower = player1.lower()
            p2_lower = player2.lower()
            
            # Check if both player names appear in the title (using multiple strategies)
            p1_in_title = (p1_lower in title or p1_lastname in title or 
                          p1_lastname in title_normalized)
            p2_in_title = (p2_lower in title or p2_lastname in title or 
                          p2_lastname in title_normalized)
            
            if p1_in_title and p2_in_title:
                matching_event = event
                break
        
        if not matching_event:
            print(f"    ✗ No matching Polymarket event found (checked {len(events)} events)")
            return None, None
        
        # Get markets for this event
        markets = matching_event.get("markets", [])
        if not markets:
            print(f"    ✗ No markets found for this event")
            return None, None
        
        # Find the moneyline market (head-to-head) with player names as outcomes
        # Prioritize match winner markets over set-specific markets
        moneyline_market = None
        match_winner_market = None
        other_player_market = None
        
        for market in markets:
            outcomes = market.get("outcomes")
            
            # Parse outcomes if it's a string
            if isinstance(outcomes, str):
                try:
                    outcomes = json.loads(outcomes)
                except:
                    continue
            
            if not outcomes or len(outcomes) < 2:
                continue
            
            # Check if both player names appear in outcomes (case-insensitive)
            # Use normalized names to handle special characters and last names
            outcomes_lower = [str(o).lower() for o in outcomes]
            outcomes_normalized = [normalize_name(o) for o in outcomes]
            p1_lower = player1.lower()
            p2_lower = player2.lower()
            p1_lastname = normalize_name(player1)
            p2_lastname = normalize_name(player2)
            
            # Check if both players are in the outcomes using multiple matching strategies
            p1_found = False
            p2_found = False
            
            for o_lower, o_norm in zip(outcomes_lower, outcomes_normalized):
                # Check full name match
                if p1_lower in o_lower or o_lower in p1_lower:
                    p1_found = True
                # Check last name match
                elif p1_lastname in o_lower or o_lower in p1_lower or p1_lastname == o_norm or o_norm in p1_lastname:
                    p1_found = True
                
                if p2_lower in o_lower or o_lower in p2_lower:
                    p2_found = True
                elif p2_lastname in o_lower or o_lower in p2_lower or p2_lastname == o_norm or o_norm in p2_lastname:
                    p2_found = True
            
            if p1_found and p2_found:
                question = market.get("question", "").lower()
                
                # Prioritize match winner markets (not set-specific)
                if "match winner" in question or ("winner" in question and "set" not in question):
                    match_winner_market = market
                # Avoid set-specific markets
                elif "set" not in question:
                    other_player_market = market
        
        # Use match winner if found, otherwise use other non-set market
        if match_winner_market:
            moneyline_market = match_winner_market
            print(f"    Using match winner market: {match_winner_market.get('question', 'N/A')}")
        elif other_player_market:
            moneyline_market = other_player_market
            print(f"    Using non-set market: {other_player_market.get('question', 'N/A')}")
        
        if not moneyline_market:
            print(f"    ✗ No moneyline market found (checked {len(markets)} markets)")
            return None, None
        
        # Extract outcome prices (probabilities)
        prices = moneyline_market.get("outcomePrices")
        
        # Parse prices if it's a string
        if isinstance(prices, str):
            try:
                prices = json.loads(prices)
            except:
                print(f"    ✗ Could not parse outcomePrices")
                return None, None
        
        if not prices or len(prices) < 2:
            print(f"    ✗ Invalid outcomePrices format")
            return None, None
        
        # Get outcomes to map prices to players
        outcomes = moneyline_market.get("outcomes")
        if isinstance(outcomes, str):
            try:
                outcomes = json.loads(outcomes)
            except:
                outcomes = [str(outcomes)]
        
        # Normalize player names to get last names
        p1_lastname = normalize_name(player1)
        p2_lastname = normalize_name(player2)
        
        # Map prices to players by matching names
        p1_prob = None
        p2_prob = None
        
        for i, outcome in enumerate(outcomes):
            outcome_lower = str(outcome).lower()
            outcome_normalized = normalize_name(outcome)
            
            try:
                prob = float(prices[i])
            except (ValueError, IndexError):
                continue
            
            # Match outcome to player using multiple strategies
            # 1. Check if full player name is in outcome or vice versa
            # 2. Check if last names match
            # 3. Check if normalized last names match
            p1_match = (p1_lastname in outcome_lower or outcome_lower in player1.lower() or 
                       p1_lastname == outcome_normalized or outcome_normalized in p1_lastname or
                       p1_lastname in outcome_normalized)
            p2_match = (p2_lastname in outcome_lower or outcome_lower in player2.lower() or 
                       p2_lastname == outcome_normalized or outcome_normalized in p2_lastname or
                       p2_lastname in outcome_normalized)
            
            if p1_match:
                p1_prob = prob
            elif p2_match:
                p2_prob = prob
        
        # If we couldn't match by name, assume order matches (first outcome = first player)
        if p1_prob is None or p2_prob is None:
            try:
                p1_prob = float(prices[0])
                p2_prob = float(prices[1])
                print(f"    ⚠ Could not match outcomes to players by name, using order assumption")
            except (ValueError, IndexError):
                print(f"    ✗ Could not extract probabilities")
                return None, None
        
        print(f"    ✓ Found Polymarket odds: P1 {p1_prob*100:.1f}% vs P2 {p2_prob*100:.1f}%")
        return p1_prob, p2_prob
        
    except Exception as e:
        print(f"    ✗ Error fetching Polymarket odds: {e}")
        return None, None

