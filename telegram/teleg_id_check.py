import requests

TOKEN = "8567356269:AAH839-_n3--eykejU4TQBQ4eQS8FY_10yE"
response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates")
print(response.json())

# Chat ID'yi almak için yukarıdaki kodu çalıştırın ve "message": {"chat": {"id": ...}} kısmını bulun.