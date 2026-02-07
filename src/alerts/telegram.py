import config


def send_telegram_message(message, scraper):
    """
    Send a message via Telegram bot.
    Configuration is read from config module.
    """
    bot_token = config.TELEGRAM_BOT_TOKEN
    chat_id = config.TELEGRAM_CHAT_ID
    
    # Skip if Telegram is not configured
    if not bot_token or not chat_id:
        print(f"    ⚠ Telegram not configured (bot_token or chat_id missing)")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        # Convert chat_id to int if it's a string
        chat_id_int = int(chat_id) if isinstance(chat_id, str) and chat_id.isdigit() else chat_id
        payload = {
            "chat_id": chat_id_int,
            "text": message,
            "parse_mode": "HTML"
        }
        
        # Use cloudscraper to send the request
        response = scraper.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print(f"    ✓ Telegram message sent successfully")
                return True
            else:
                error_desc = result.get("description", "Unknown error")
                print(f"    ✗ Telegram API error: {error_desc}")
                return False
        else:
            try:
                error_data = response.json()
                error_desc = error_data.get("description", response.text)
                print(f"    ✗ Telegram API error ({response.status_code}): {error_desc}")
            except:
                print(f"    ✗ Telegram API error ({response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"    ✗ Error sending Telegram message: {e}")
        import traceback
        traceback.print_exc()
        return False

