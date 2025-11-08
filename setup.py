from setuptools import setup, find_packages

setup(
    name="emlak-scraper",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "crawl4ai>=0.7.6",
        "playwright>=1.48.0",
        "beautifulsoup4>=4.12.3",
        "rich>=13.9.4",
        "python-dotenv>=1.0.1",
    ],
    python_requires=">=3.11",
    author="Arda Karaosmanoglu",
    description="101evler.com KKTC property scraper",
    keywords="scraper real-estate cyprus kktc",
)
