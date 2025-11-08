#!/bin/bash
# Quick setup script for Docker deployment

echo "🚀 Kıbrıs Emlak Scraper - Docker Setup"
echo "======================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker bulunamadı. Lütfen Docker'ı yükleyin: https://www.docker.com/get-started"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose bulunamadı. Lütfen Docker Compose'u yükleyin."
    exit 1
fi

echo "✅ Docker ve Docker Compose kurulu"
echo ""

# Create necessary directories
echo "📁 Gerekli klasörleri oluşturuluyor..."
mkdir -p pages listings reports temp
echo "✅ Klasörler hazır"
echo ""

# Build Docker image
echo "🔨 Docker image oluşturuluyor (bu işlem birkaç dakika sürebilir)..."
docker-compose build
if [ $? -eq 0 ]; then
    echo "✅ Docker image başarıyla oluşturuldu"
else
    echo "❌ Docker image oluşturma başarısız"
    exit 1
fi
echo ""

# Test run
echo "🧪 Test çalıştırması yapılıyor..."
docker-compose run --rm scraper python -c "import sys; print(f'✅ Python {sys.version} hazır'); import crawl4ai; print('✅ Crawl4AI hazır'); import pandas; print('✅ Pandas hazır'); import docx; print('✅ python-docx hazır')"
echo ""

echo "✅ Kurulum tamamlandı!"
echo ""
echo "🎯 Hızlı başlangıç komutları:"
echo ""
echo "# Scraper'ı çalıştır:"
echo "docker-compose run --rm scraper python main.py"
echo ""
echo "# Veri çıkarımı:"
echo "docker-compose run --rm scraper python extract_data.py"
echo ""
echo "# Rapor oluştur:"
echo "docker-compose run --rm scraper python report.py"
echo ""
echo "# Narenciye analizi:"
echo "docker-compose run --rm scraper python orchard_analysis.py"
echo ""
echo "# Word rapor:"
echo "docker-compose run --rm scraper python generate_agent_report.py"
echo ""
echo "# Arka planda servis olarak çalıştır:"
echo "docker-compose up -d scraper"
echo ""
echo "📚 Daha fazla bilgi için README.md dosyasına bakın"
