# 101evler.com Scraper - Docker Image
FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8  
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

RUN apt-get update && apt-get install -y wget gnupg ca-certificates fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 libwayland-client0 libxcomposite1 libxdamage1 libxfixes3 libxkbcommon0 libxrandr2 xvfb && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium --with-deps
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY setup.py .
COPY README.md .
RUN pip install -e .
RUN mkdir -p data/raw/listings data/raw/pages data/processed data/cache logs
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 CMD python -c "import sys; sys.exit(0)"
CMD ["python", "scripts/scan/comprehensive_full_scan.py"]