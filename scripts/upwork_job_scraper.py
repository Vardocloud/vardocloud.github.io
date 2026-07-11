#!/usr/bin/env python3
"""
Upwork Job Scraper via Google Custom Search API
Daily cron job: searches Upwork jobs and sends report to Edel.
"""

import requests
import json
import os
import sys
from datetime import datetime, timedelta

# Config
API_KEY_FILE = os.path.expanduser("~/.hermes/secrets/google_cse_api_key.txt")
CX = "712bb8f9c4a21485e"  # Google Custom Search Engine ID
OUTPUT_DIR = os.path.expanduser("~/.hermes/data/upwork_jobs")
MAX_RESULTS = 10

def load_api_key():
    with open(API_KEY_FILE, 'r') as f:
        return f.read().strip()

def search_upwork_jobs(keywords, days_ago=3):
    """Search Upwork jobs via Google Custom Search API."""
    api_key = load_api_key()
    
    all_jobs = []
    
    # For each keyword, search Google for site:upwork.com/jobs
    for keyword in keywords:
        # Search query: site:upwork.com/jobs [keyword] posted in last N days
        query = f'site:upwork.com/jobs "{keyword}"'
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": CX,
            "q": query,
            "num": 10,
            "dateRestrict": f"d{days_ago}",  # last N days
            "sort": "date",
        }
        
        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            
            items = data.get("items", [])
            for item in items:
                job = {
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "source": keyword,
                    "date": item.get("pagemap", {}).get("metatags", [{}])[0].get("article:published_time", ""),
                }
                all_jobs.append(job)
        except Exception as e:
            print(f"Error searching '{keyword}': {e}")
            continue
    
    # Deduplicate by URL
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        if job["url"] not in seen:
            seen.add(job["url"])
            unique_jobs.append(job)
    
    return unique_jobs

def format_report(jobs):
    """Format jobs into a nice Turkish report."""
    if not jobs:
        return "Bugün Upwork'te yeni uygun iş bulunamadı. 🤷‍♀️"
    
    report = f"🔍 **Upwork Günlük İş Raporu**\n"
    report += f"📅 {datetime.now().strftime('%d %B %Y')}\n"
    report += f"💼 Toplam {len(jobs)} fırsat bulundu\n\n"
    report += "━━━━━━━━━━━━━━━━━━\n\n"
    
    for i, job in enumerate(jobs, 1):
        report += f"**{i}. {job['title']}**\n"
        report += f"🔗 {job['url']}\n"
        
        # Clean snippet
        snippet = job.get('snippet', '')
        if snippet:
            # Truncate long snippets
            if len(snippet) > 200:
                snippet = snippet[:200] + "..."
            report += f"📝 {snippet}\n"
        
        if job.get('date'):
            report += f"📆 {job['date']}\n"
        
        report += f"🏷️ Arama: {job['source']}\n"
        report += "\n━━━━━━━━━━━━━━━━━━\n\n"
    
    report += "\n💡 Detaylar için linklere tıklayabilirsin!"
    
    return report

def main():
    # Keywords to search (can be customized)
    keywords = os.environ.get(
        "UPWORK_KEYWORDS",
        "python,ai,machine learning,data science,automation,n8n,chatbot,web scraping,freelance developer,LLM"
    ).split(",")
    
    keywords = [k.strip() for k in keywords]
    
    print(f"🔍 Searching Upwork for: {', '.join(keywords)}")
    
    jobs = search_upwork_jobs(keywords, days_ago=3)
    
    print(f"✅ Found {len(jobs)} unique jobs")
    
    # Format report
    report = format_report(jobs)
    
    # Save to file
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = os.path.join(OUTPUT_DIR, f"upwork_jobs_{today}.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    
    print(f"📁 Saved to {output_file}")
    
    # Print report for cron delivery
    print("\n" + "=" * 50)
    print(report)
    
    return report

if __name__ == "__main__":
    main()
