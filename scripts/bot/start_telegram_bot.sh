#!/bin/bash
# Telegram Bot Startup Script for Pi
# Bu script bot'u Docker container içinde başlatır

echo "🤖 Telegram Bot Başlatılıyor..."
echo ""

# Check if container is running
if ! docker ps | grep -q emlak-scraper-101evler; then
    echo "❌ Container çalışmıyor!"
    echo "   Önce container'ı başlatın:"
    echo "   docker-compose up -d"
    exit 1
fi

echo "✅ Container bulundu"
echo ""

# Install psutil if not present
echo "📦 Bağımlılıklar kontrol ediliyor..."
docker exec emlak-scraper-101evler pip list | grep -q psutil || {
    echo "   psutil kuruluyor..."
    docker exec emlak-scraper-101evler pip install psutil
}

echo "✅ Bağımlılıklar hazır"
echo ""

# Copy bot script to container
echo "📋 Bot scripti kopyalanıyor..."
docker cp /home/ekrem/projects/emlak-scraper/scripts/bot/telegram_bot.py emlak-scraper-101evler:/app/telegram_bot.py

echo "✅ Script kopyalandı"
echo ""

# Start bot in background
echo "🚀 Bot başlatılıyor..."
docker exec -d emlak-scraper-101evler python3 /app/telegram_bot.py

echo "✅ Bot başlatıldı!"
echo ""
echo "📱 Telegram'dan komutları deneyin:"
echo "   /help - Komut listesi"
echo "   /status - Durum raporu"
echo "   /progress - İlerleme detayı"
echo "   /health - Sistem sağlığı"
echo ""
echo "🛑 Durdurmak için:"
echo "   docker exec emlak-scraper-101evler pkill -f telegram_bot.py"
echo ""
