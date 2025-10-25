#!/usr/bin/env python3
"""
Script to verify Telegram Bot Token
"""
import sys
import requests

def verify_token(bot_token):
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
                print(f"🆔 Bot ID: {bot_info['id']}")
                return True
        
        print("❌ Invalid token!")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
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
