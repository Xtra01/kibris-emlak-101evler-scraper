#!/usr/bin/env python3
"""
Simple FastAPI server for emlak scraper statistics
Serves real-time stats from data directory
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
from datetime import datetime
import os

app = FastAPI(title="Emlak Scraper API", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path("/app/data/raw/listings")
ANALYSIS_FILE = Path("/app/data/site_analysis.json")

def count_files_by_config():
    """Count HTML files per config (scraped listings)"""
    stats = {}
    if not DATA_DIR.exists():
        return stats
    
    for city_dir in DATA_DIR.iterdir():
        if not city_dir.is_dir():
            continue
        for config_dir in city_dir.iterdir():
            if not config_dir.is_dir():
                continue
            config_name = f"{city_dir.name}/{config_dir.name}"
            # Count HTML files (raw scraped data)
            html_files = list(config_dir.glob("*.html"))
            if len(html_files) > 0:
                stats[config_name] = len(html_files)
    
    return stats

@app.get("/")
async def root():
    return {
        "service": "Emlak Scraper API",
        "version": "1.0.0",
        "endpoints": ["/stats", "/health"]
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/stats")
async def get_stats():
    """Get current scraping statistics"""
    
    # Count scraped files
    config_stats = count_files_by_config()
    total_files = sum(config_stats.values())
    total_configs = 72
    completed_configs = len([v for v in config_stats.values() if v > 0])
    remaining_configs = total_configs - completed_configs
    
    # Load analysis data if available
    expected_totals = {}
    if ANALYSIS_FILE.exists():
        try:
            with open(ANALYSIS_FILE, 'r', encoding='utf-8') as f:
                analysis = json.load(f)
                expected_totals = analysis.get("configs", {})
        except:
            pass
    
    # Calculate progress
    progress_percent = (completed_configs / total_configs * 100) if total_configs > 0 else 0
    
    return {
        "total_files": total_files,
        "total_configs": total_configs,
        "completed": completed_configs,
        "remaining": remaining_configs,
        "progress_percent": round(progress_percent, 1),
        "config_details": config_stats,
        "expected_totals": expected_totals,
        "last_updated": datetime.now().isoformat()
    }

@app.get("/configs")
async def get_configs():
    """Get detailed config information"""
    config_stats = count_files_by_config()
    
    # Load expected totals
    expected = {}
    if ANALYSIS_FILE.exists():
        try:
            with open(ANALYSIS_FILE, 'r', encoding='utf-8') as f:
                analysis = json.load(f)
                expected = analysis.get("configs", {})
        except:
            pass
    
    configs = []
    for config_name, scraped in config_stats.items():
        expected_count = expected.get(config_name, 0)
        progress = (scraped / expected_count * 100) if expected_count > 0 else 0
        
        configs.append({
            "name": config_name,
            "scraped": scraped,
            "expected": expected_count,
            "progress": round(progress, 1),
            "status": "completed" if scraped >= expected_count and expected_count > 0 else "in-progress" if scraped > 0 else "not-started"
        })
    
    return {
        "configs": configs,
        "total": len(configs)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
