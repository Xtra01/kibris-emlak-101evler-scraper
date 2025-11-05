# 101evler.com Scraper and Data Extractor

This project scrapes property listing data from 101evler.com (specifically for Northern Cyprus) and extracts the details into a structured CSV file.

## Features

*   Scrapes listing URLs from search result pages.
*   Uses Playwright for search pages to handle dynamic content.
*   Saves individual listing pages as HTML files.
*   Avoids re-scraping already saved listings and search pages.
*   Extracts detailed information from saved HTML listing pages using BeautifulSoup.
*   Handles potential errors during scraping and extraction.
*   Calculates approximate monthly rent in TL (based on a 14x multiplier and current exchange rates from the Turkish Central Bank).
*   Outputs extracted data to a CSV file (`property_details.csv`).
*   Includes continuous run mode for `extract_data.py`.
*   Automatically detects the total number of pages and listings.
*   Pauses for 10 minutes when blocked by access controls, then automatically resumes.
*   Stops when two consecutive blocking attempts are detected.

## Prerequisites

*   Python 3.8+
*   pip (Python package installer)

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-directory>
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Playwright browsers:**
    The `crawl4ai` library uses Playwright. You might need to install its browser binaries the first time:
    ```bash
    playwright install
    ```

## Usage

### 1. Scraping Listings (`main.py`)

This script crawls the search result pages to find listing URLs and then scrapes each listing's HTML content.

*   **Configuration:**
    *   Open `main.py`.
    *   Modify `base_search_url`: Change the path (e.g., `/magusa`, `/girne`, `/lefkosa`) to target different areas or property types (e.g., `kiralik-daire`, `satilik-villa`). The base should look like `https://www.101evler.com/kibris/<listing_type>/<area>`.
    *   You can also adjust the `output_dir` (default: `listings`) and `pages_dir` (default: `pages`) if needed.
*   **Command-line Arguments:**
    *   `--max-pages`: Specify the maximum number of search pages to scrape.
      ```bash
      python main.py --max-pages 15
      ```
      If not specified, the script will automatically detect and use the total number of pages from the website.
*   **Run the scraper:**
    ```bash
    python main.py
    ```
    The script will:
    *   Fetch the first search page and automatically determine the total number of pages and listings.
    *   Fetch search result pages (using Playwright) up to the determined maximum number of pages.
    *   Save search page HTML to the `pages/` directory.
    *   Extract listing URLs from these pages.
    *   Fetch individual listing pages (without Playwright).
    *   Save listing HTML to the `listings/` directory.
    *   Skip already downloaded search pages and listings.
    *   Log progress and delays to the console.
    *   When access is blocked, wait for 10 minutes and retry automatically.
    *   If blocked on second attempt, the script will stop.
    *   Failed listing URLs are saved to `listings/failed/failed_urls.txt` for potential retries.

### 2. Extracting Data (`extract_data.py`)

This script parses the saved HTML files in the `listings/` directory and extracts property details into a CSV file.

*   **Run the extractor:**
    ```bash
    python extract_data.py
    ```
    The script will:
    *   Read all `.html` files from the `listings/` directory.
    *   Skip listings already present in the output CSV.
    *   Parse HTML using BeautifulSoup to extract details like price, location, features, dates, agency, etc.
    *   Fetch current TRY exchange rates for price conversion.
    *   Calculate an estimated 14x monthly rent in TL (`price_tl_14x`).
    *   Append the extracted data to `property_details.csv`.
    *   Update existing TL prices in the CSV based on current exchange rates.
*   **Continuous Mode:**
    To run the extractor periodically (e.g., if the scraper runs in the background or via cron):
    ```bash
    python extract_data.py --continuous [INTERVAL_MINUTES] [MAX_RUNS]
    ```
    *   `INTERVAL_MINUTES`: Wait time in minutes between runs (default: 30).
    *   `MAX_RUNS`: Maximum number of times to run (default: 10).

## Output

*   **`listings/`**: Directory containing the raw HTML of individual property listings.
*   **`pages/`**: Directory containing the raw HTML of search result pages.
*   **`property_details.csv`**: CSV file containing the extracted and structured property data.

## Automatic Total Page Detection

The script now automatically determines the total number of pages and listings by:

1. Making an API request to mimic the website's JavaScript behavior
2. Analyzing HTML content to find pagination information
3. Calculating the total pages based on total listings (assuming 30 listings per page)
4. Selecting the most reliable source of information

This means you no longer need to manually set the maximum number of pages to scrape. The script will:
- Print the detected total listings and total pages
- Use the detected values for scraping
- Allow you to override with the `--max-pages` argument if needed
- Stop automatically when reaching empty pages

## Auto-Retry When Blocked

The script implements a smart cooldown system when access is blocked:

1. When a blocking page is detected (Cloudflare or other access controls), the script:
   - Displays a message: `!!! Erişim engellendi. 10 dakika bekleniyor ve tekrar denenecek... !!!`
   - Waits for 10 minutes (cooldown period)
   - Automatically retries the same request

2. This allows temporary IP restrictions or rate-limiting to expire before continuing.

3. If blocked again on the second attempt, the script will stop to prevent further blocking.

This feature makes the scraper more resilient against temporary access restrictions and allows for unattended operation.

## Dependencies

See `requirements.txt`.

---

## Docker Deployment

### Quick Start with Docker

The easiest way to run this scraper is using Docker, which handles all dependencies including Playwright browsers automatically.

#### Prerequisites
- Docker installed (version 20.10+)
- Docker Compose installed (version 1.29+)

#### Build and Run

1. **Build the Docker image:**
   ```bash
   docker-compose build
   ```

2. **Run the scraper (one-time execution):**
   ```bash
   docker-compose run --rm scraper python main.py
   ```

3. **Run data extraction:**
   ```bash
   docker-compose run --rm scraper python extract_data.py
   ```

4. **Generate reports:**
   ```bash
   docker-compose run --rm scraper python report.py
   ```

5. **Run orchard analysis:**
   ```bash
   docker-compose run --rm scraper python orchard_analysis.py
   ```

6. **Generate Word report for agents:**
   ```bash
   docker-compose run --rm scraper python generate_agent_report.py
   ```

7. **Search examples:**
   ```bash
   # Basic search
   docker-compose run --rm scraper python search.py basic "guzelyurt arsa" --out reports/search_results.xlsx
   
   # Advanced search
   docker-compose run --rm scraper python search.py advanced --city guzelyurt --property-type arsa --min-donum 5
   ```

#### Persistent Storage

All important data is persisted via Docker volumes:
- `property_details.csv` - Main database
- `pages/` - Search result HTML pages
- `listings/` - Individual listing HTML files
- `reports/` - Generated reports (MD, XLSX, DOCX)
- `temp/` - Temporary files

These directories are mapped to your local filesystem, so data persists even if containers are removed.

#### Run as a Service

To run the scraper continuously in the background:

```bash
docker-compose up -d scraper
```

View logs:
```bash
docker-compose logs -f scraper
```

Stop the service:
```bash
docker-compose down
```

#### Scheduled Execution (Optional)

To enable automated scheduling with cron:

1. Edit `crontab` file to configure your schedule
2. Start the scheduler service:
   ```bash
   docker-compose --profile scheduler up -d scraper-scheduler
   ```

Example cron schedule:
- Daily scraping at 2 AM
- Data extraction at 2:30 AM
- Report generation at 3 AM
- Weekly orchard analysis on Mondays at 4 AM

#### Resource Management

Default resource limits:
- CPU: 1-2 cores
- Memory: 1-2 GB

Adjust in `docker-compose.yml` under `deploy.resources` if needed.

#### Shell Access

For debugging or manual operations:
```bash
docker-compose run --rm scraper /bin/bash
```

#### Environment Variables

Add custom environment variables in `docker-compose.yml` under the `environment` section:
```yaml
environment:
  - PYTHONUNBUFFERED=1
  - CUSTOM_VAR=value
```

### Docker Commands Reference

```bash
# Build image
docker-compose build

# Run specific script
docker-compose run --rm scraper python <script.py>

# Start service in background
docker-compose up -d

# View logs
docker-compose logs -f [service-name]

# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Shell access
docker-compose run --rm scraper /bin/bash

# Check container status
docker-compose ps

# Restart service
docker-compose restart scraper
```

### Troubleshooting

**Playwright browser issues:**
- Browsers are pre-installed in the Docker image
- If issues occur, rebuild: `docker-compose build --no-cache`

**Permission errors:**
- Ensure the mounted directories are writable
- On Linux: `chmod -R 777 pages listings reports temp`

**Out of memory:**
- Increase memory limits in docker-compose.yml
- Or restart Docker Desktop and allocate more resources

**Network timeouts:**
- Check your internet connection
- Increase timeout values in scripts if needed

**Data not persisting:**
- Verify volume mounts in docker-compose.yml
- Check that local directories exist before running 

---

## Project Structure

```
.
├─ listings/                 # Saved listing HTML files (persisted)
├─ pages/                    # Saved search page HTML files (persisted)
├─ reports/                  # Generated reports (MD/XLSX/DOCX)
├─ temp/                     # Temporary files
├─ docs/
│  └─ DOCKER.md             # Docker deployment guide
├─ orchard_analysis.py       # Orchard pricing analysis (CLI & library)
├─ generate_agent_report.py  # Emlakçıya yönelik Word rapor üretimi
├─ report.py                 # Genel/arsa/kira raporlama yardımcıları
├─ search.py                 # Basic/advanced arama ve CLI
├─ extract_data.py           # HTML'den CSV çıkarımı
├─ main.py                   # Scraper giriş noktası
├─ docker-compose.yml        # Orkestrasyon
├─ Dockerfile                # Multi-stage Docker image
├─ .dockerignore             # Build optimizasyonu
├─ crontab                   # Opsiyonel cron görevleri
├─ setup-docker.sh           # Linux/Mac kurulum kolaylaştırıcı
├─ setup-docker.bat          # Windows kurulum kolaylaştırıcı
├─ requirements.txt          # Python bağımlılıkları
└─ README.md                 # Bu dosya
```

---

## Ready-to-use code snippets

### 1) Güzelyurt arsa (≥1 dönüm) narenciye analizi ve özet JSON
```powershell
python orchard_analysis.py --city guzelyurt --property-type arsa --listing-type Sale --min-donum 1 --export-json reports/guzelyurt_orchard_summary.json
```

### 2) 10 dönümlük Piyalepaşa odağı ve Word rapor
```powershell
python orchard_analysis.py --min-donum 10 --core-city-token guzelyurt --core-district-tokens piyalepasa,merkez --export-xlsx reports/guzelyurt_orchard_pricing_core10.xlsx
python generate_agent_report.py
```

### 3) Gelişmiş arama: Güzelyurt ≥5 dönüm arsa, ₺/dönüm artan
```powershell
python search.py advanced --city guzelyurt --property-type arsa --min-donum 5 --sort price_per_donum_try:asc --out reports/arama_guzelyurt_arsa_5donum.xlsx
```

### 4) Raporları üret (Markdown + Excel)
```powershell
python report.py
python excel_report.py
```