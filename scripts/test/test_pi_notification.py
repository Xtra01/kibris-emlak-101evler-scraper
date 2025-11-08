#!/usr/bin/env python3
"""
Raspberry Pi - Notification Test
Container içinden Telegram test mesajı gönderir
"""

import sys
sys.path.insert(0, '/app/src')

# Direct import - reports modülünü bypass et
from emlak_scraper.notifications import get_notifier

print("🔍 Notification Config Check:")
notifier = get_notifier()

print(f"   Telegram enabled: {notifier.enable_telegram}")
print(f"   Telegram token: {notifier.telegram_token[:20]}..." if notifier.telegram_token else "   Telegram token: NOT SET")
print(f"   Telegram chat ID: {notifier.telegram_chat_id}")
print(f"   Email enabled: {notifier.enable_email}")
print(f"   SMTP user: {notifier.smtp_user}")
print()

if notifier.enable_telegram and notifier.telegram_chat_id:
    print("📤 Sending test message...")
    success = notifier.send_telegram(
        "🍓 *Raspberry Pi Notification Test*\n\n"
        "✅ Bildirim sistemi Pi üzerinde aktif!\n"
        "📊 Scan devam ediyor...\n"
        "🔔 Her 5 config'de güncelleme alacaksınız\n\n"
        "_Test mesajı - Container içinden gönderildi_"
    )
    
    if success:
        print("✅ Test mesajı başarıyla gönderildi!")
    else:
        print("❌ Test mesajı gönderilemedi")
else:
    print("⚠️  Telegram config eksik!")
