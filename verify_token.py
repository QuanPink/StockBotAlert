import sys

import requests


def verify_token(bot_token: str) -> bool:
    """Verify if token is valid"""
    print("🔍 Verifying bot token...")

    try:
        response = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe", timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                bot_info = data['result']
                print("✅ Token is valid!")
                print(f"📱 Bot name: {bot_info['first_name']}")
                print(f"🔗 Bot username: @{bot_info['username']}")
                return True

        print("❌ Invalid token!")
        print(f"Response: {response.text}")
        return False


    except requests.exceptions.Timeout:
        print("\n❌ Request timeout - check your internet connection")
        return False

    except requests.exceptions.ConnectionError:
        print("\n❌ Connection error - cannot reach Telegram API")
        return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python verify_token.py YOUR_BOT_TOKEN")
        sys.exit(1)

    token = sys.argv[1]

    if verify_token(token):
        print("\n✅ You can use this token in config.py!")
    else:
        print("\n❌ Please get a valid token from @BotFather on Telegram")
