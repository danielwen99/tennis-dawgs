import cloudscraper
import json
import os


def get_updates():
    """Get recent updates from the bot to find your chat ID."""
    try:
        # Get bot token from environment variable
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            print("Error: TELEGRAM_BOT_TOKEN environment variable not set")
            print("Please set it using: export TELEGRAM_BOT_TOKEN='your_token_here'")
            return None
        
        scraper = cloudscraper.create_scraper()
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        
        response = scraper.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                updates = data.get("result", [])
                if updates:
                    print("Recent messages received by your bot:")
                    print("=" * 60)
                    for update in updates:
                        message = update.get("message", {})
                        chat = message.get("chat", {})
                        chat_id = chat.get("id")
                        chat_type = chat.get("type")
                        first_name = chat.get("first_name", "")
                        username = chat.get("username", "")
                        text = message.get("text", "")
                        
                        print(f"Chat ID: {chat_id}")
                        print(f"Type: {chat_type}")
                        print(f"Name: {first_name} (@{username})" if username else f"Name: {first_name}")
                        print(f"Message: {text}")
                        print("-" * 60)
                    
                    # Get the most recent chat ID
                    if updates:
                        latest_chat_id = updates[-1].get("message", {}).get("chat", {}).get("id")
                        print(f"\n✓ Your Chat ID is: {latest_chat_id}")
                        return latest_chat_id
                else:
                    print("No messages found. Please:")
                    print("1. Open Telegram")
                    print("2. Search for your bot")
                    print("3. Start a conversation and send a message (e.g., '/start' or 'hello')")
                    print("4. Run this script again")
            else:
                print(f"Error: {data.get('description', 'Unknown error')}")
        else:
            print(f"API Error: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Getting your Telegram Chat ID...")
    print("=" * 60)
    get_updates()

