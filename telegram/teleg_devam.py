# telegram_notifier.py
import os
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set in environment!")
    
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
if not TELEGRAM_CHAT_ID:
    raise ValueError("TELEGRAM_CHAT_ID not set in environment!")

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def send_message(text: str,
                 parse_mode: Optional[str] = None,
                 disable_notification: bool = False) -> dict:
    params = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "disable_notification": disable_notification,
    }
    if parse_mode:
        params["parse_mode"] = parse_mode

    resp = requests.get(f"{BASE_URL}/sendMessage",
                        params=params,
                        timeout=10)
    resp.raise_for_status()
    return resp.json()
