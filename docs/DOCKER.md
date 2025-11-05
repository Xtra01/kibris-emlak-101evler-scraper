# 🐳 Docker Kurulum Rehberi

## Hızlı Başlangıç

### Windows için:
```cmd
setup-docker.bat
```

### Linux/Mac için:
```bash
chmod +x setup-docker.sh
./setup-docker.sh
```

## Manuel Kurulum

### 1. Docker Image Oluştur
```bash
docker-compose build
```

### 2. Temel Kullanım

#### Scraper Çalıştır
```bash
docker-compose run --rm scraper python main.py
```

#### Veri Çıkarımı
```bash
docker-compose run --rm scraper python extract_data.py
```

#### Rapor Oluştur
```bash
docker-compose run --rm scraper python report.py
```

#### Narenciye Analizi
```bash
docker-compose run --rm scraper python orchard_analysis.py
```

#### Word Rapor (Emlakçı İçin)
```bash
docker-compose run --rm scraper python generate_agent_report.py
```

### 3. Arama Örnekleri

#### Basit Arama
```bash
docker-compose run --rm scraper python search.py basic "guzelyurt arsa"
```

#### Excel'e Kaydet
```bash
docker-compose run --rm scraper python search.py basic "guzelyurt arsa" --out reports/arama.xlsx
```

#### Gelişmiş Arama
```bash
docker-compose run --rm scraper python search.py advanced \
  --city guzelyurt \
  --property-type arsa \
  --min-donum 5 \
  --max-donum 20 \
  --sort price_per_donum_try:asc
```

### 4. Servis Olarak Çalıştır

#### Arka Planda Başlat
```bash
docker-compose up -d scraper
```

#### Logları İzle
```bash
docker-compose logs -f scraper
```

#### Durdur
```bash
docker-compose down
```

### 5. Otomatik Zamanlama (Cron)

1. `crontab` dosyasını düzenle
2. İstediğin zamanlamaları aktif et (# işaretini kaldır)
3. Scheduler servisini başlat:

```bash
docker-compose --profile scheduler up -d scraper-scheduler
```

## Veri Kalıcılığı

Veriler otomatik olarak yerel diskine kaydedilir:
- `property_details.csv` - Ana veritabanı
- `pages/` - Arama sayfaları HTML
- `listings/` - İlan sayfaları HTML  
- `reports/` - Oluşturulan raporlar
- `temp/` - Geçici dosyalar

## Shell Erişimi

Konteyner içinde komut satırı için:
```bash
docker-compose run --rm scraper /bin/bash
```

## Sorun Giderme

### Container başlamıyor
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Hafıza hatası
`docker-compose.yml` dosyasında memory değerini artır:
```yaml
deploy:
  resources:
    limits:
      memory: 4G
```

### Playwright tarayıcı hatası
```bash
docker-compose build --no-cache
```

### Veri kayboldu
Volume'ları kontrol et:
```bash
docker volume ls
docker-compose down  # Dikkat: -v ekleme, veriyi siler!
```

## Komut Referansı

```bash
# Image oluştur
docker-compose build

# Tek seferlik çalıştır
docker-compose run --rm scraper <komut>

# Servis olarak başlat
docker-compose up -d

# Logları görüntüle
docker-compose logs -f

# Durdur
docker-compose down

# Yeniden başlat
docker-compose restart

# Durum kontrolü
docker-compose ps

# Volume'ları da sil (DİKKAT: Veri kaybolur!)
docker-compose down -v
```

## Kaynak Yönetimi

Varsayılan limitler:
- CPU: 1-2 çekirdek
- RAM: 1-2 GB

Gerekirse `docker-compose.yml` içinden ayarlayabilirsin.

## Güvenlik Notları

- Container root kullanıcı olarak çalışır (Playwright gereksinimi)
- Network izolasyonu bridge modu ile sağlanır
- Veriler yerel sistem ile paylaşılır (volume mount)
- Outbound internet erişimi gerekir (scraping için)

## Performans İpuçları

1. **SSD kullan**: Volume mount edilen klasörleri SSD'de tut
2. **CPU çekirdek sayısı**: Çok sayfalı scraping için 2+ çekirdek öner
3. **RAM**: Büyük veri setleri için 2GB+ ayır
4. **Network**: Kararlı ve hızlı internet gerekli
5. **Docker Desktop**: En güncel versiyonu kullan

## Üretim Ortamı İçin

1. Resource limitleri ayarla
2. Health check'leri aktif et
3. Restart policy ayarla: `restart: unless-stopped`
4. Log rotation yapılandır
5. Monitoring ekle (Prometheus, Grafana vb.)
6. Backup stratejisi belirle

## Lisans

Projenin ana lisansı geçerlidir.
