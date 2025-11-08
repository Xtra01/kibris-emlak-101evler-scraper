"""
Telegram Chat ID Finder & Tester
Botunuza /start komutu gönderdikten sonra bu scripti çalıştırın
"""

import requests
import json

# Bot token
BOT_TOKEN = "8567356269:AAH839-_n3--eykejU4TQBQ4eQS8FY_10yE"

print("🔍 Telegram Bot Chat ID Bulucu\n")
print("📱 Adımlar:")
print("   1. Telegram'da @teletesti01_bot botunuzu bulun")
print("   2. /start komutu gönderin")
print("   3. Bu script çalışacak\n")

# Get updates
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

try:
    response = requests.get(url, timeout=10)
    data = response.json()
    
    if not data.get('ok'):
        print(f"❌ Hata: {data.get('description')}")
        exit(1)
    
    updates = data.get('result', [])
    
    if not updates:
        print("⚠️  Henüz mesaj yok!")
        print("   👉 Telegram'da botunuza /start gönderin ve tekrar deneyin")
        exit(0)
    
    # En son mesajı al
    latest = updates[-1]
    chat = latest.get('message', {}).get('chat', {})
    
    chat_id = chat.get('id')
    chat_type = chat.get('type')
    username = chat.get('username', 'N/A')
    first_name = chat.get('first_name', 'N/A')
    
    print("✅ Bot bulundu!\n")
    print(f"📋 Bilgiler:")
    print(f"   Chat ID: {chat_id}")
    print(f"   Type: {chat_type}")
    print(f"   Username: @{username}")
    print(f"   Name: {first_name}\n")
    
    # .env dosyasını güncelle
    env_file = ".env"
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Chat ID'yi güncelle
    content = content.replace('TELEGRAM_CHAT_ID=PLACEHOLDER_WILL_AUTO_DETECT', 
                              f'TELEGRAM_CHAT_ID={chat_id}')
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ .env dosyası güncellendi!")
    print(f"   TELEGRAM_CHAT_ID={chat_id}\n")
    
    # Test mesajı gönder
    print("📤 Test mesajı gönderiliyor...\n")
    
    send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': '✅ *Telegram Bot Testi Başarılı!*\n\n🔔 KKTC Emlak Scraper bildirimleri aktif.\n\n_Scraper çalıştığında buradan bildirim alacaksınız._',
        'parse_mode': 'Markdown'
    }
    
    test_response = requests.post(send_url, json=payload, timeout=10)
    
    if test_response.status_code == 200:
        print("✅ Test mesajı gönderildi!")
        print("   👉 Telegram'da mesajı kontrol edin\n")
    else:
        print(f"❌ Mesaj gönderilemedi: {test_response.text}\n")
    
    print("🎉 Kurulum tamamlandı!")
    print("   Artık notification sistemi kullanıma hazır.\n")

except requests.exceptions.RequestException as e:
    print(f"❌ Bağlantı hatası: {e}")
    exit(1)
except Exception as e:
    print(f"❌ Hata: {e}")
    exit(1)
