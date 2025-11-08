import requests

TOKEN = "8567356269:AAH839-_n3--eykejU4TQBQ4eQS8FY_10yE"
CHAT_ID = 8386214866
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

try:
    r = requests.get(URL, params={"chat_id": CHAT_ID, "text": "Test mesajı çalıştı!"}, timeout=10)
    print(r.json())
except requests.exceptions.RequestException as e:
    print("Bağlantı hatası:", e)
