# Proje Yeniden Yapılandırma Planı
# Sektör Standardı: Python Proje Yapısı

## Araştırma: Standart Python Proje Yapısı

### 1. PyPA (Python Packaging Authority) Standartları:
```
project/
├── src/
│   └── package_name/
│       ├── __init__.py
│       ├── core/           # Ana iş mantığı
│       ├── utils/          # Yardımcı fonksiyonlar
│       └── cli/            # Komut satırı arayüzü
├── tests/                  # Test dosyaları
├── docs/                   # Dokümantasyon
├── scripts/                # Yardımcı scriptler
├── data/                   # Veri dosyaları
│   ├── raw/               # Ham veri
│   ├── processed/         # İşlenmiş veri
│   └── reports/           # Raporlar
├── config/                 # Konfigürasyon dosyaları
├── logs/                   # Log dosyaları
├── .github/               # GitHub workflows
├── pyproject.toml         # Modern Python packaging
├── setup.py               # Klasik packaging (optional)
├── requirements.txt       # Bağımlılıklar
├── .gitignore
├── README.md
└── LICENSE
```

### 2. Data Science Projeler için (Cookiecutter Data Science):
```
project/
├── data/
│   ├── raw/              # Değiştirilmez ham veri
│   ├── interim/          # Ara aşama verileri
│   ├── processed/        # Son işlenmiş veri
│   └── external/         # Dış kaynaklardan
├── notebooks/            # Jupyter notebooks
├── src/
│   ├── data/            # Veri yükleme/kaydetme
│   ├── features/        # Feature engineering
│   ├── models/          # Model eğitimi
│   └── visualization/   # Görselleştirme
├── models/              # Eğitilmiş modeller
├── reports/
│   └── figures/         # Grafikler
└── references/          # Veri sözlükleri, açıklamalar
```

### 3. Web Scraping Projeler için Best Practices:
```
project/
├── src/
│   ├── scrapers/        # Scraper modülleri
│   ├── parsers/         # HTML/JSON parsers
│   ├── pipelines/       # Veri pipeline'ları
│   └── exporters/       # Veri export
├── data/
│   ├── raw/             # İndirilen HTML/JSON
│   ├── cache/           # Önbellek
│   └── output/          # İşlenmiş veri
├── config/              # Site-specific config
└── tests/
    ├── unit/
    └── integration/
```

## BİZİM PROJE İÇİN UYARLAMA:

### Mevcut Durum Analizi:
```
SORUNLAR:
❌ Root'ta 15+ script (check_*, generate_*, full_*, emergency_*, manual_*)
❌ src/scraper/ altında karışık dosyalar
❌ utils/ ve scripts/ ayrı ayrı var
❌ analysis/ ve archive/ düzensiz
❌ listings/ ve pages/ data klasörü değil
❌ reports/ düzensiz

İYİLER:
✅ src/ klasörü var
✅ Docker yapılandırması var
✅ .github/ workflows var
✅ docs/ var
```

### Önerilen Yeni Yapı:

```
kibris-emlak-101evler-scraper/
├── src/
│   └── emlak_scraper/           # Ana paket
│       ├── __init__.py
│       ├── core/                # Ana scraping logic
│       │   ├── __init__.py
│       │   ├── scraper.py       # main.py -> buraya
│       │   ├── parser.py        # extract_data.py -> buraya
│       │   └── config.py        # Config
│       ├── reports/             # Rapor oluşturma
│       │   ├── __init__.py
│       │   ├── excel.py         # Excel raporları
│       │   └── markdown.py      # Markdown raporları
│       ├── analysis/            # Analiz modülleri
│       │   ├── __init__.py
│       │   └── market.py        # Piyasa analizi
│       ├── utils/               # Yardımcı fonksiyonlar
│       │   ├── __init__.py
│       │   ├── file_ops.py
│       │   └── logger.py
│       └── cli/                 # Komut satırı arayüzü
│           ├── __init__.py
│           └── commands.py
├── scripts/                     # Yardımcı scriptler
│   ├── scan/
│   │   ├── full_rental_scan.py
│   │   ├── full_sale_scan.py
│   │   └── emergency_scan.py
│   ├── check/
│   │   ├── check_girne.py
│   │   └── check_data.py
│   ├── generate/
│   │   ├── generate_excel.py
│   │   └── generate_report.py
│   └── setup/
│       ├── setup-docker.sh
│       └── setup-docker.bat
├── tests/                       # Test dosyaları
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_scraper.py
│   │   └── test_parser.py
│   └── integration/
│       └── test_full_scan.py
├── data/                        # VERİ KLASÖRÜ (Git'e eklenmez)
│   ├── raw/                     # Ham veri
│   │   ├── listings/            # listings/ -> buraya
│   │   └── pages/               # pages/ -> buraya
│   ├── processed/               # İşlenmiş veri
│   │   └── property_details.csv
│   ├── reports/                 # reports/ -> buraya
│   │   └── archive/
│   └── cache/                   # Geçici cache
├── logs/                        # Log dosyaları
│   └── archive/
├── docs/                        # Dokümantasyon
│   ├── api/
│   ├── user_guide/
│   └── architecture.md
├── config/                      # Konfigürasyon dosyaları
│   ├── scraper.yaml
│   └── cities.yaml
├── .github/
│   └── workflows/
├── docker/                      # Docker dosyaları
│   ├── Dockerfile
│   └── docker-compose.yml
├── .dockerignore
├── .gitignore
├── .env.example
├── pyproject.toml              # Modern Python packaging
├── setup.py                    # Backward compatibility
├── requirements.txt
├── requirements-dev.txt        # Development dependencies
├── README.md
├── LICENSE
└── CHANGELOG.md
```

### Faydaları:
1. ✅ **Modüler**: Her şey kendi yerinde
2. ✅ **Test Edilebilir**: tests/ klasörü ayrı
3. ✅ **Paketlenebilir**: pyproject.toml ile pip install edilebilir
4. ✅ **Okunabilir**: src/emlak_scraper/ altında mantıklı gruplar
5. ✅ **Ölçeklenebilir**: Yeni özellikler eklemek kolay
6. ✅ **Standart**: Tüm Python projelerinde kullanılan yapı
7. ✅ **Profesyonel**: GitHub'da iyi görünüyor

### Taşınacak Dosyalar:

**Root → scripts/**:
- check_451524.py → scripts/check/
- check_girne.py → scripts/check/
- emergency_girne_full.py → scripts/scan/
- full_rental_scan.py → scripts/scan/
- full_sale_scan.py → scripts/scan/
- generate_excel_report.py → scripts/generate/
- generate_full_report.py → scripts/generate/
- generate_mega_report.py → scripts/generate/
- generate_sale_report.py → scripts/generate/
- manual_scrape_451524.py → scripts/manual/
- manual_scrape_484941.py → scripts/manual/
- test_451524_availability.py → tests/manual/
- project_status.py → scripts/utils/

**src/scraper/ → src/emlak_scraper/core/**:
- main.py → core/scraper.py
- extract_data.py → core/parser.py
- config.py → core/config.py

**src/scraper/ → src/emlak_scraper/reports/**:
- excel_report.py → reports/excel.py
- report.py → reports/markdown.py
- generate_agent_report.py → reports/agents.py

**listings/ → data/raw/listings/**
**pages/ → data/raw/pages/**
**reports/ → data/reports/**
**property_details.csv → data/processed/**

### Sonraki Adım:
1. Yeni klasör yapısını oluştur
2. Dosyaları taşı
3. Import path'leri güncelle
4. Docker config güncelle
5. Test et
