"""
Email SMTP Tester
Gmail SMTP bağlantısını test eder
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import sys

load_dotenv()

print("📧 Gmail SMTP Testi\n")

# Config from environment
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL")

# Validate
if not all([SMTP_USER, SMTP_PASSWORD, NOTIFY_EMAIL]):
    print("❌ ERROR: Missing credentials in .env file!")
    print("Required: SMTP_USER, SMTP_PASSWORD, NOTIFY_EMAIL")
    sys.exit(1)

print(f"🔗 Bağlantı kuruluyor: {SMTP_HOST}:{SMTP_PORT}")

try:
    # SMTP bağlantısı
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        print("✅ SMTP sunucusuna bağlanıldı")
        
        # TLS başlat
        server.starttls()
        print("✅ TLS şifreleme aktif")
        
        # Login
        server.login(SMTP_USER, SMTP_PASSWORD)
        print(f"✅ Giriş başarılı: {SMTP_USER}\n")
        
        # Test email gönder
        print("📤 Test email'i gönderiliyor...\n")
        
        msg = MIMEMultipart('alternative')
        msg['From'] = SMTP_USER
        msg['To'] = NOTIFY_EMAIL
        msg['Subject'] = "✅ KKTC Emlak Scraper - Email Testi"
        
        body = """
<html>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <h2 style="color: #4CAF50;">✅ Email Sistemi Çalışıyor!</h2>
    
    <div style="background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 15px 0;">
        <h3>📊 Test Bilgileri</h3>
        <p><strong>SMTP Host:</strong> smtp.gmail.com</p>
        <p><strong>Port:</strong> 587 (TLS)</p>
        <p><strong>Gönderen:</strong> ekremregister@gmail.com</p>
        <p><strong>Durum:</strong> <span style="color: green;">Aktif ✓</span></p>
    </div>
    
    <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 15px 0;">
        <h3>🔔 Bildirimler</h3>
        <p>Raspberry Pi'de scraper çalıştığında:</p>
        <ul>
            <li>✅ Scan başladığında bildirim</li>
            <li>📊 Her 5 config'de ilerleme güncellemesi</li>
            <li>❌ Hata olduğunda uyarı</li>
            <li>🎉 Tamamlandığında detaylı rapor</li>
        </ul>
    </div>
    
    <p style="color: #666; font-size: 12px; margin-top: 30px;">
        KKTC Emlak Scraper - Notification System<br>
        Test mesajı - {timestamp}
    </p>
</body>
</html>
""".format(timestamp="2024-11-08 23:30")
        
        part = MIMEText(body, 'html')
        msg.attach(part)
        
        server.send_message(msg)
        
        print("✅ Test email başarıyla gönderildi!")
        print(f"   📬 {NOTIFY_EMAIL} adresini kontrol edin\n")
        
        print("🎉 Email sistemi kullanıma hazır!")

except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ Kimlik doğrulama hatası!")
    print(f"   {e}\n")
    print("🔧 Çözüm:")
    print("   1. Gmail'de 2FA aktif mi kontrol edin")
    print("   2. App Password doğru mu kontrol edin")
    print("   3. https://myaccount.google.com/apppasswords")
    print("      adresinden yeni App Password oluşturun\n")
    
except smtplib.SMTPException as e:
    print(f"\n❌ SMTP hatası: {e}\n")
    
except Exception as e:
    print(f"\n❌ Hata: {e}\n")
    print("🔧 Çözüm:")
    print("   1. İnternet bağlantınızı kontrol edin")
    print("   2. Firewall port 587'yi engelliyor olabilir")
    print("   3. Gmail hesabınızı kontrol edin\n")
