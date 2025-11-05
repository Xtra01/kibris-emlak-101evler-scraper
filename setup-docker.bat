@echo off
REM Quick setup script for Docker deployment (Windows)

echo ========================================
echo Kibris Emlak Scraper - Docker Setup
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker bulunamadi. Lutfen Docker'i yukleyin: https://www.docker.com/get-started
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose bulunamadi. Lutfen Docker Compose'u yukleyin.
    pause
    exit /b 1
)

echo [OK] Docker ve Docker Compose kurulu
echo.

REM Create necessary directories
echo [INFO] Gerekli klasorleri olusturuluyor...
if not exist "pages" mkdir pages
if not exist "listings" mkdir listings
if not exist "reports" mkdir reports
if not exist "temp" mkdir temp
echo [OK] Klasorler hazir
echo.

REM Build Docker image
echo [INFO] Docker image olusturuluyor (bu islem birkac dakika surebilir)...
docker-compose build
if errorlevel 1 (
    echo [ERROR] Docker image olusturma basarisiz
    pause
    exit /b 1
)
echo [OK] Docker image basariyla olusturuldu
echo.

REM Test run
echo [INFO] Test calistirmasi yapiliyor...
docker-compose run --rm scraper python -c "import sys; print(f'[OK] Python {sys.version} hazir'); import crawl4ai; print('[OK] Crawl4AI hazir'); import pandas; print('[OK] Pandas hazir'); import docx; print('[OK] python-docx hazir')"
echo.

echo ========================================
echo [OK] Kurulum tamamlandi!
echo ========================================
echo.
echo Hizli baslangic komutlari:
echo.
echo # Scraper'i calistir:
echo docker-compose run --rm scraper python main.py
echo.
echo # Veri cikarimi:
echo docker-compose run --rm scraper python extract_data.py
echo.
echo # Rapor olustur:
echo docker-compose run --rm scraper python report.py
echo.
echo # Narenciye analizi:
echo docker-compose run --rm scraper python orchard_analysis.py
echo.
echo # Word rapor:
echo docker-compose run --rm scraper python generate_agent_report.py
echo.
echo # Arka planda servis olarak calistir:
echo docker-compose up -d scraper
echo.
echo Daha fazla bilgi icin README.md dosyasina bakin
echo.
pause
