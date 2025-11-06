#!/bin/bash
# Tüm kiralık ilanları Docker ile çek - OPTİMİZE YÖNTEM

set -e

# Renkler
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   101evler.com TÜM KİRALIK İLANLAR - DOCKER OPTİMİZE     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Şehirler
CITIES=("lefkosa" "girne" "magusa" "gazimagusa" "iskele" "guzelyurt")
# Tipler
TYPES=("kiralik-daire" "kiralik-villa")

TOTAL=$((${#CITIES[@]} * ${#TYPES[@]}))
CURRENT=0
SUCCESS=0
FAILED=0

START_TIME=$(date +%s)

echo -e "${GREEN}🎯 Toplam konfigürasyon: $TOTAL${NC}"
echo -e "${GREEN}🏙️  Şehirler: ${CITIES[*]}${NC}"
echo -e "${GREEN}🏠 Tipler: ${TYPES[*]}${NC}"
echo ""

# Her şehir ve tip için döngü
for CITY in "${CITIES[@]}"; do
    for TYPE in "${TYPES[@]}"; do
        CURRENT=$((CURRENT + 1))
        
        # İsim oluştur
        NAME="${CITY^} ${TYPE/kiralik-/}"
        
        echo ""
        echo -e "${BLUE}[$CURRENT/$TOTAL] 🔄 $NAME${NC}"
        echo -e "${BLUE}============================================================${NC}"
        echo -e "📍 Şehir: $CITY"
        echo -e "🏠 Tip: $TYPE"
        echo ""
        
        # Config dosyasını güncelle
        echo -e "${YELLOW}⚙️  Config güncelleniyor...${NC}"
        sed -i "s/^CITY = .*/CITY = \"$CITY\"  # Auto-updated/" /app/src/scraper/config.py
        sed -i "s/^PROPERTY_TYPE = .*/PROPERTY_TYPE = \"$TYPE\"  # Auto-updated/" /app/src/scraper/config.py
        
        # Scraper'ı çalıştır
        echo -e "${GREEN}🚀 Scraping başlıyor...${NC}"
        
        if python -m scraper.main 2>&1 | tee /tmp/scraper_log.txt; then
            echo -e "${GREEN}✅ BAŞARILI: $NAME${NC}"
            SUCCESS=$((SUCCESS + 1))
        else
            echo -e "${RED}❌ HATA: $NAME${NC}"
            FAILED=$((FAILED + 1))
            echo -e "${YELLOW}Son 10 satır:${NC}"
            tail -n 10 /tmp/scraper_log.txt
        fi
        
        # İlerlem göster
        ELAPSED=$(($(date +%s) - START_TIME))
        AVG=$((ELAPSED / CURRENT))
        REMAINING=$(((TOTAL - CURRENT) * AVG))
        
        echo ""
        echo -e "${BLUE}📊 İlerleme: $CURRENT/$TOTAL (${GREEN}✅$SUCCESS ${RED}❌$FAILED${BLUE})${NC}"
        echo -e "${BLUE}⏱️  Geçen: $((ELAPSED / 60))m ${ELAPSED % 60}s | Kalan: ~$((REMAINING / 60))m ${REMAINING % 60}s${NC}"
        
        # Rate limiting
        if [ $CURRENT -lt $TOTAL ]; then
            echo -e "${YELLOW}⏸️  3 saniye bekleniyor...${NC}"
            sleep 3
        fi
    done
done

# Extraction çalıştır
echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}🔄 EXTRACTION BAŞLATILIYOR${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

if python -m scraper.extract_data; then
    echo -e "${GREEN}✅ Extraction başarılı!${NC}"
else
    echo -e "${RED}❌ Extraction hatası${NC}"
fi

# Özet
echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}📊 ÖZET İSTATİSTİKLER${NC}"
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}✅ Başarılı: $SUCCESS/$TOTAL${NC}"
echo -e "${RED}❌ Hatalı: $FAILED/$TOTAL${NC}"
echo -e "${BLUE}⏱️  Toplam süre: $((ELAPSED / 60))m ${ELAPSED % 60}s${NC}"
echo -e "${BLUE}⚡ Ortalama: ${AVG}s/config${NC}"
echo ""

# CSV özeti
if [ -f "/app/property_details.csv" ]; then
    echo -e "${BLUE}📊 CSV ÖZET:${NC}"
    python -c "
import pandas as pd
try:
    df = pd.read_csv('/app/property_details.csv')
    rentals = df[df['listing_type'] == 'Rent']
    print(f'  Toplam kayıt: {len(df)}')
    print(f'  Kiralık kayıt: {len(rentals)}')
    print()
    print('  Şehir dağılımı (kiralıklar):')
    for city, count in rentals['city'].value_counts().items():
        print(f'    {city}: {count}')
except Exception as e:
    print(f'  CSV okunamadı: {e}')
"
fi

echo ""
echo -e "${GREEN}🎉 İŞLEM TAMAMLANDI!${NC}"
