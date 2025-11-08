#!/usr/bin/env python3
"""Test crawl4ai Playwright initialization"""
import asyncio
import sys
import os

# Apply Windows UTF-8 fix
if sys.platform == 'win32':
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from crawl4ai import AsyncWebCrawler

async def test():
    print("Starting AsyncWebCrawler...")
    async with AsyncWebCrawler() as crawler:
        print("✓ Crawler started successfully!")
        print(f"Crawler ID: {id(crawler)}")
        
        # Test simple fetch
        print("Testing simple fetch...")
        result = await crawler.arun("https://example.com")
        print(f"✓ Fetch successful! HTML length: {len(result.html) if result and result.html else 0}")
        
    print("✓ Crawler closed successfully!")
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test())
        print("\n[SUCCESS] All tests passed!")
        sys.exit(0)
    except Exception as e:
        print(f"\n[FAILED] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
