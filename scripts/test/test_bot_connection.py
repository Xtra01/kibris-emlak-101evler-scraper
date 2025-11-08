#!/usr/bin/env python3
"""Test Telegram Bot Connection"""
import os
import sys
sys.path.insert(0, '/app')
from dotenv import load_dotenv
import requests

load_dotenv('/app/.env')

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

print(f"TOKEN: {TOKEN[:20]}...")
print(f"CHAT_ID: {CHAT_ID}")

# Test bot API
response = requests.get(f'https://api.telegram.org/bot{TOKEN}/getMe')
print(f"\nBot Info: {response.json()}")

# Test get updates
response = requests.get(f'https://api.telegram.org/bot{TOKEN}/getUpdates')
print(f"\nRecent Updates: {response.json()}")

# Send test message
response = requests.post(
    f'https://api.telegram.org/bot{TOKEN}/sendMessage',
    json={
        'chat_id': CHAT_ID,
        'text': '🧪 Bot Connection Test - Manual Test Script'
    }
)
print(f"\nSend Message Result: {response.json()}")
