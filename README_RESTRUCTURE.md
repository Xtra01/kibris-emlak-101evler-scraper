# 📦 Yeni Proje Yapısı - Emlak Scraper v2.0.0

## 🎯 Yapılan Değişiklikler

Proje, **sektör standartlarında** profesyonel bir Python paketi haline getirildi:

- ✅ PyPA (Python Packaging Authority) standartları
- ✅ Cookiecutter Data Science organizasyonu
- ✅ Web Scraping best practices
- ✅ Modüler ve test edilebilir yapı
- ✅ Docker güncellendi
- ✅ Modern Python packaging (pyproject.toml)

## 📁 Yeni Klasör Yapısı

```
emlak-scraper/
├── src/emlak_scraper/          # Ana Python paketi
│   ├── __init__.py             # Paket tanımlayıcı (v2.0.0)
│   ├── core/                   # Çekirdek scraping mantığı
│   │   ├── scraper.py          # Ana scraper (eski main.py)
│   │   ├── parser.py           # HTML/JSON parser (eski extract_data.py)
│   │   └── config.py           # Konfigürasyon
│   ├── reports/                # Rapor üreticileri
│   │   ├── excel.py            # Excel raporları
│   │   ├── markdown.py         # Markdown raporları
│   │   └── agents.py           # Word raporları
│   ├── analysis/               # Analiz modülleri
│   │   └── orchard.py          # Bahçe analizi
│   ├── utils/                  # Yardımcı araçlar
│   └── cli/                    # CLI komutları (gelecek)
│
├── scripts/                    # Organize scriptler
│   ├── scan/                   # Tarama scriptleri
│   │   ├── full_rental_scan.py
│   │   └── emergency_rental_scan.py
│   ├── check/                  # Kontrol scriptleri
│   │   ├── check_girne.py
│   │   └── check_missing_listings.py
│   ├── generate/               # Rapor scriptleri
│   │   ├── generate_excel_report.py
│   │   └── generate_agent_report.py
│   ├── manual/                 # Manuel scraping
│   │   ├── manual_scrape_451524.py
│   │   └── manual_scrape_484941.py
│   ├── setup/                  # Kurulum scriptleri
│   │   ├── setup-docker.sh
│   │   └── setup-docker.bat
│   └── utils/                  # Yardımcı scriptler
│       ├── move_data_directories.ps1
│       └── project_status.py
│
├── data/                       # Veri klasörü (git-ignored)
│   ├── raw/                    # Ham veriler
│   │   ├── listings/           # HTML ilanlar (2,659 dosya)
│   │   └── pages/              # Arama sayfaları (30 dosya)
│   ├── processed/              # İşlenmiş veriler
│   │   └── property_details.csv
│   ├── reports/                # Raporlar
│   │   └── archive/
│   └── cache/                  # Geçici cache
│       └── temp/
│
├── tests/                      # Test dosyaları
│   ├── unit/
│   ├── integration/
│   └── manual/
│
├── docker/                     # Docker konfigürasyonu
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── config/                     # Konfigürasyon dosyaları
│
├── logs/                       # Log dosyaları
│
├── docs/                       # Dokümantasyon
│
├── pyproject.toml              # Modern Python packaging
├── requirements.txt            # Bağımlılıklar
├── .gitignore                  # Git ignore (güncellendi)
├── README.md                   # Ana dokümantasyon
└── RESTRUCTURE_PLAN.md         # Detaylı plan dokümantasyonu
```

## 🔄 Eski → Yeni Mapping

### Dosya Yerleri

| Eski Konum | Yeni Konum |
|------------|------------|
| `main.py` | `src/emlak_scraper/core/scraper.py` |
| `extract_data.py` | `src/emlak_scraper/core/parser.py` |
| `config.py` | `src/emlak_scraper/core/config.py` |
| `excel_report.py` | `src/emlak_scraper/reports/excel.py` |
| `report.py` | `src/emlak_scraper/reports/markdown.py` |
| `generate_agent_report.py` | `src/emlak_scraper/reports/agents.py` |
| `orchard_analysis.py` | `src/emlak_scraper/analysis/orchard.py` |

### Data Klasörleri

| Eski Konum | Yeni Konum |
|------------|------------|
| `listings/` | `data/raw/listings/` |
| `pages/` | `data/raw/pages/` |
| `property_details.csv` | `data/processed/property_details.csv` |
| `reports/` | `data/reports/` |
| `temp/` | `data/cache/temp/` |

### Import Statements

```python
# ESKİ
from scraper.config import CITY
from scraper.main import scrape_page
import scraper.extract_data

# YENİ
from emlak_scraper.core.config import CITY
from emlak_scraper.core.scraper import scrape_page
import emlak_scraper.core.parser
```

## 🐋 Docker Kullanımı

### Yeni Komutlar

```bash
# Build
cd docker
docker-compose build

# Scraper çalıştır
docker-compose run --rm scraper python -m emlak_scraper.core.scraper

# Parser çalıştır
docker-compose run --rm scraper python -m emlak_scraper.core.parser

# Excel raporu oluştur
docker-compose run --rm scraper python -m emlak_scraper.reports.excel

# Shell (interaktif)
docker-compose run --rm scraper /bin/bash
```

### Volume Mapping

```yaml
volumes:
  - ./data:/app/data     # Tüm data klasörü
  - ./logs:/app/logs     # Log dosyaları
```

## 📦 Python Paketi Olarak Kullanım

### Geliştirme Modu Kurulumu

```bash
# Editable mode (geliştirme için)
pip install -e .

# Dev dependencies ile
pip install -e ".[dev]"
```

### Import Kullanımı

```python
# Artık her yerden import edilebilir
from emlak_scraper.core import config, scraper, parser
from emlak_scraper.reports import excel, markdown
from emlak_scraper.analysis import orchard

# Config kullanımı
config.show_config()
config.apply_quick_config("lefkosa_daire")

# Scraper kullanımı
scraper.scrape_page(url, crawler)
```

### CLI Komutları (pyproject.toml'da tanımlı)

```bash
# Script'ler artık komut olarak çalıştırılabilir
emlak-scan        # Full rental scan
emlak-parse       # Parse HTML files
emlak-report      # Generate Excel report
```

## ⚡ Hızlı Başlangıç

### 1. Geliştirme Ortamı

```bash
# Virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Paket kurulumu
pip install -e ".[dev]"
```

### 2. Docker ile

```bash
cd docker
docker-compose build
docker-compose up -d
```

### 3. Manuel Çalıştırma

```bash
# Scraping
python -m emlak_scraper.core.scraper

# Parsing
python -m emlak_scraper.core.parser

# Reporting
python -m emlak_scraper.reports.excel
```

## 🧪 Testing

```bash
# Test klasörü hazır
cd tests

# pytest ile
pytest

# Coverage ile
pytest --cov=emlak_scraper
```

## 📊 Mevcut Durum

### Taşınan Veriler

- ✅ 2,659 listing HTML dosyası → `data/raw/listings/`
- ✅ 30 arama sayfası → `data/raw/pages/`
- ✅ 1 CSV dosyası → `data/processed/`
- ✅ Raporlar → `data/reports/`

### Güncellenen Dosyalar

- ✅ `src/emlak_scraper/core/config.py` - Yeni path'ler
- ✅ `src/emlak_scraper/core/scraper.py` - Yeni import'lar
- ✅ `src/emlak_scraper/core/parser.py` - Yeni path'ler
- ✅ `src/emlak_scraper/reports/excel.py` - Yeni import'lar
- ✅ `src/emlak_scraper/reports/agents.py` - Yeni import'lar
- ✅ `docker/Dockerfile` - Yeni dizin yapısı
- ✅ `docker/docker-compose.yml` - Yeni volume mapping
- ✅ `.gitignore` - Güncel ignore patterns
- ✅ `pyproject.toml` - Modern packaging

## 🎓 Faydaları

### 1. Modüler Yapı
- Her modül kendi sorumluluğunda
- Kolay test edilebilir
- Bağımlılıklar net

### 2. Ölçeklenebilirlik
- Yeni özellikler kolayca eklenebilir
- Plugin architecture hazır
- CLI komutları genişletilebilir

### 3. Profesyonellik
- PyPI'a yüklenebilir
- Semantic versioning (2.0.0)
- Proper documentation structure

### 4. Bakım Kolaylığı
- Dosyaları bulmak kolay
- Import'lar tutarlı
- Data organizasyonu net

## 🔧 Sonraki Adımlar

1. **Testing**: Unit ve integration testler yaz
2. **Documentation**: API dokümantasyonu (Sphinx)
3. **CLI**: Click/Typer ile gelişmiş CLI
4. **CI/CD**: GitHub Actions ile otomatik test
5. **PyPI**: Paketi yayınla

## 📚 Kaynaklar

- [PyPA Packaging Guide](https://packaging.python.org/)
- [Cookiecutter Data Science](https://drivendata.github.io/cookiecutter-data-science/)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/guides/)

---

**Version**: 2.0.0  
**Date**: 2025-01-08  
**Author**: Xtra01
