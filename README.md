# Tennis Dawgs 

## Project Structure

```
tennis dawgs/
├── main.py                 # Main entry point
├── config.py              # Configuration (API URLs, Telegram settings, etc.)
├── data/                  # Data directory
│   └── tennis_dawgs.csv   # Match data CSV
└── src/                   # Source code
    ├── api/               # API integrations
    │   ├── polymarket.py # Polymarket odds fetching
    │   └── sofascore.py  # SofaScore match data
    ├── alerts/            # Alert system
    │   ├── telegram.py   # Telegram messaging
    │   ├── one_one_alert.py  # 1-1 sets alert
    │   ├── break_alert.py    # Break serve alert
    │   └── tiebreak_alert.py # Tiebreak alert
    ├── analysis/          # Data analysis
    │   └── player_comparison.py  # Player statistics comparison
    ├── detection/         # Event detection
    │   ├── break_detector.py     # Break serve detection logic
    │   └── tiebreak_detector.py  # Tiebreak detection logic
    ├── processors/        # Data processing
    │   ├── match_processor.py    # Main match processing logic
    │   ├── stats_extractor.py    # Extract stats from API
    │   └── tournament_detector.py  # Tournament type detection
    ├── storage/           # Data storage
    │   ├── cache_manager.py      # Cache management
    │   └── csv_logger.py         # CSV logging
    └── utils/             # Utilities
        ├── constants.py   # Constants (colors, etc.)
        └── helpers.py     # Helper functions
```

## Running the Application

```bash
python main.py
```

## Features

1. **1-1 Sets Alert**: Sends Telegram notification when a match reaches 1-1 sets
2. **Break Alert**: Sends Telegram notification when a player who lost the first set breaks serve in the second set and is leading
3. **Tiebreak Alert**: Sends Telegram notification when 3rd set reaches 6-6 (tiebreak)
4. **CSV Logging**: Logs qualified matches (1-1 sets, early 3rd set) to CSV
5. **Odds Tracking**: Tracks starting and live odds from Polymarket

## Configuration

### Environment Variables

Create a `.env` file in the project root (or set environment variables):

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

See `env.example` for a template.

### Other Settings

Edit `config.py` to modify:
- API URLs
- Allowed tournaments
- Polling interval

## Dependencies

See `requirements.txt` for required packages.

