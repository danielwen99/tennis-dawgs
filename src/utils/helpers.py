def safe_ratio(numerator, denominator):
    """Safe division with error handling."""
    try:
        return float(numerator) / float(denominator) if denominator else 0
    except:
        return 0


def format_odds_decimal(p1_prob, p2_prob):
    """
    Convert probabilities to decimal odds format.
    Returns tuple (p1_decimal, p2_decimal) or (None, None) if invalid.
    Decimal odds = 1 / probability
    """
    if p1_prob is None or p2_prob is None or p1_prob <= 0 or p2_prob <= 0:
        return None, None
    
    try:
        p1_decimal = 1.0 / float(p1_prob)
        p2_decimal = 1.0 / float(p2_prob)
        return p1_decimal, p2_decimal
    except:
        return None, None


def normalize_name(name):
    """Normalize name by removing special characters and extracting last name."""
    name = str(name).lower()
    # Remove special characters (í -> i, š -> s, etc.)
    replacements = {
        'í': 'i', 'š': 's', 'č': 'c', 'ř': 'r', 'ž': 'z',
        'á': 'a', 'é': 'e', 'ó': 'o', 'ú': 'u', 'ý': 'y',
        'ñ': 'n', 'ü': 'u', 'ö': 'o', 'ä': 'a'
    }
    for old, new in replacements.items():
        name = name.replace(old, new)
    # Get last name (last word)
    parts = name.split()
    return parts[-1] if parts else name


def to_int(val):
    """Convert value to int, handling None, strings, and percentages."""
    if val is None:
        return 0
    if isinstance(val, str):
        return int(val.replace('%', '').strip() or 0)
    elif isinstance(val, (int, float)):
        return int(val)
    else:
        return 0

