import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set in environment!")
response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates")
print(response.json())

# Chat ID'yi almak için yukarıdaki kodu çalıştırın ve "message": {"chat": {"id": ...}} kısmını bulun.