# telegram_notifier.py
import os
import requests
from typing import Optional

TELEGRAM_BOT_TOKEN = os.environ["8567356269:AAH839-_n3--eykejU4TQBQ4eQS8FY_10yE"]
TELEGRAM_CHAT_ID = os.environ["8386214866"]

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
