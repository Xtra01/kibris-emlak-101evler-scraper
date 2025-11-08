"""
101evler.com KKTC Emlak Scraper
================================

Kuzey Kıbrıs Türk Cumhuriyeti emlak ilanlarını toplayan, 
analiz eden ve raporlayan profesyonel scraper paketi.

Modüller:
- core: Ana scraping ve parsing işlemleri
- reports: Excel ve Markdown rapor oluşturma
- analysis: Piyasa analizi ve istatistikler
- utils: Yardımcı fonksiyonlar
- cli: Komut satırı arayüzü
"""

__version__ = "2.0.0"
__author__ = "Xtra01"
__license__ = "MIT"

from .core import scraper, parser, config
from .reports import excel, markdown
from .utils import file_ops, logger

__all__ = [
    "scraper",
    "parser",
    "config",
    "excel",
    "markdown",
    "file_ops",
    "logger",
]
