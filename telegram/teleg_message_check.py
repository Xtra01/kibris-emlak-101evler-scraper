import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set in environment!")
CHAT_ID = 8386214866
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

try:
    r = requests.get(URL, params={"chat_id": CHAT_ID, "text": "Test mesajı çalıştı!"}, timeout=10)
    print(r.json())
except requests.exceptions.RequestException as e:
    print("Bağlantı hatası:", e)
