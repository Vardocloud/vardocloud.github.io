#!/usr/bin/env python3
"""
Upwork Job Search via Google Custom Search API + Firecrawl
Cloudflare-free job discovery for Edel's freelancing pipeline.

Architecture:
1. Google CSE searches "site:upwork.com/jobs [keywords]" → gets job URLs + snippets
2. Firecrawl parses full job pages for details (budget, skills, client info)
3. Results saved as JSON + formatted Telegram message
4. Runs daily via cron

Usage:
  python3 upwork_job_search.py [--keywords "python ai" --limit 10]
"""

import json
import os
import sys
import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

# Output directory
OUTPUT_DIR = Path("/home/ubuntu/data/upwork_jobs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# History file for deduplication
HISTORY_FILE = OUTPUT_DIR / "job_history.json"
HISTORY_FILE.touch(exist_ok=True)


def load_history():
    """Load previously seen job IDs to avoid duplicates."""
    try:
        with open(HISTORY_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_history(jobs):
    """Save job IDs to history for deduplication."""
    existing = load_history()
    seen = set(j["job_id"] for j in existing)
    
    new_jobs = []
    for job in jobs:
        if job["job_id"] not in seen:
            seen.add(job["job_id"])
            new_jobs.append(job)
    
    # Keep last 500 jobs in history
    all_jobs = existing + new_jobs
    if len(all_jobs) > 500:
        all_jobs = all_jobs[-500:]
    
    with open(HISTORY_FILE, "w") as f:
        json.dump(all_jobs, f, indent=2, ensure_ascii=False)
    
    return new_jobs


def google_cse_search(query, cx, api_key, limit=10):
    """Search Google Custom Search Engine for Upwork jobs."""
    import urllib.request
    
    url = f"https://www.googleapis.com/customsearch/v1?q={quote(query)}&cx={cx}&key={api_key}&num={min(limit, 10)}"
    
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            return data.get("items", [])
    except Exception as e:
        print(f"Google CSE error: {e}")
        return []


def parse_job_from_search_result(item):
    """Extract job info from Google search result."""
    url = item.get("link", "")
    title = item.get("title", "")
    snippet = item.get("snippet", "")
    
    # Extract job ID from URL
    job_id = ""
    if "/jobs/" in url:
        parts = url.split("/jobs/")
        if len(parts) > 1:
            job_id = parts[1].split("?")[0].split("/")[0]
    
    # Generate hash ID if URL parsing fails
    if not job_id:
        job_id = hashlib.md5(url.encode()).hexdigest()[:12]
    
    # Extract date if available
    date_posted = ""
    for part in snippet.split():
        if part in ["hour", "hours", "day", "days", "week", "weeks"]:
            idx = snippet.split().index(part)
            if idx > 0:
                date_posted = f"{snippet.split()[idx-1]} {part} ago"
            break
    
    return {
        "job_id": job_id,
        "title": title.replace(" - Upwork", "").strip(),
        "url": url,
        "snippet": snippet,
        "date_posted": date_posted,
        "source": "google_cse",
        "discovered_at": datetime.now(timezone.utc).isoformat(),
    }


def scrape_job_details_with_firecrawl(url, api_key):
    """Use Firecrawl to get full job details from Upwork page."""
    import urllib.request
    
    firecrawl_url = os.environ.get("FIRECRAWL_API_URL", "https://api.firecrawl.dev")
    
    payload = json.dumps({
        "url": url,
        "formats": ["markdown"],
        "onlyMainContent": True,
    })
    
    req = urllib.request.Request(
        f"{firecrawl_url}/v1/scrape",
        data=payload.encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode())
            if data.get("success") and data.get("data"):
                return data["data"].get("markdown", "")
    except Exception as e:
        print(f"  Firecrawl error for {url}: {e}")
    
    return ""


def parse_job_details(markdown):
    """Extract structured data from job page markdown."""
    details = {}
    
    # Look for budget info
    for line in markdown.split("\n"):
        line_lower = line.lower()
        if any(k in line_lower for k in ["budget", "hourly", "fixed", "price"]):
            details["budget_hint"] = line.strip()
            break
    
    # Look for skills
    if "skills" in markdown.lower():
        skills_section = ""
        in_skills = False
        for line in markdown.split("\n"):
            if "skill" in line.lower():
                in_skills = True
                continue
            if in_skills:
                if line.startswith("#") or line.strip() == "":
                    break
                skills_section += line + " "
        if skills_section:
            details["skills_hint"] = skills_section.strip()
    
    # Look for client info
    for line in markdown.split("\n"):
        if any(k in line.lower() for k in ["client", "rating", "spent", "location"]):
            details["client_hint"] = line.strip()
            break
    
    return details


def format_telegram_message(new_jobs, all_jobs):
    """Format jobs for Telegram message."""
    if not new_jobs:
        return "🔍 Bugün Upwork'te yeni iş bulunamadı. Belki keyword'leri güncelleyelim?"
    
    msg = f"🎯 **Upwork İş Raporu** — {datetime.now(timezone.utc).strftime('%d %B %Y')}\n\n"
    msg += f"📊 **{len(new_jobs)} yeni iş** bulundu (toplam takip: {len(all_jobs)})\n\n"
    msg += "━" * 30 + "\n\n"
    
    for i, job in enumerate(new_jobs[:10], 1):  # Max 10 per message
        msg += f"**{i}. {job['title']}**\n"
        msg += f"🔗 {job['url']}\n"
        
        if job.get("snippet"):
            snippet = job["snippet"][:150]
            msg += f"📝 {snippet}...\n"
        
        if job.get("date_posted"):
            msg += f"⏰ {job['date_posted']}\n"
        
        if job.get("details"):
            d = job["details"]
            if d.get("budget_hint"):
                msg += f"💰 {d['budget_hint']}\n"
        
        msg += "\n" + "─" * 20 + "\n\n"
    
    if len(new_jobs) > 10:
        msg += f"\n...ve {len(new_jobs) - 10} iş daha. Detayları görmek ister misin?\n"
    
    msg += "\n💡 _İstediğin zaman keyword'leri güncelleyebilir, belirli bir iş hakkında detay isteyebilirsin._"
    
    return msg


def main():
    parser = argparse.ArgumentParser(description="Upwork Job Search via Google CSE")
    parser.add_argument("--keywords", default="python ai automation n8n chatbot", help="Search keywords")
    parser.add_argument("--limit", type=int, default=10, help="Max results per keyword group")
    parser.add_argument("--firecrawl", action="store_true", help="Use Firecrawl for full job details")
    parser.add_argument("--output-format", choices=["telegram", "json", "both"], default="both")
    args = parser.parse_args()
    
    # Config
    cx = "712bb8f9c4a21485e"
    google_api_key = os.environ.get("GOOGLE_CSE_API_KEY", "")
    firecrawl_api_key = os.environ.get("FIRECRAWL_API_KEY", "")
    
    if not google_api_key:
        print("ERROR: GOOGLE_CSE_API_KEY environment variable not set")
        sys.exit(1)
    
    # Split keywords into groups for better search
    keyword_groups = [
        "python",
        "ai automation",
        "n8n",
        "chatbot",
        "machine learning",
        "web scraping",
    ]
    
    if args.keywords != "python ai automation n8n chatbot":
        keyword_groups = args.keywords.split()
    
    print(f"🔍 Aranan keyword'ler: {', '.join(keyword_groups)}")
    
    all_new_jobs = []
    
    for keyword in keyword_groups:
        query = f"site:upwork.com/jobs {keyword}"
        print(f"\n📌 Arama: {query}")
        
        results = google_cse_search(query, cx, google_api_key, limit=args.limit)
        print(f"  → {len(results)} sonuç bulundu")
        
        for item in results:
            job = parse_job_from_search_result(item)
            
            # Optional: scrape full details with Firecrawl
            if args.firecrawl and firecrawl_api_key:
                print(f"  → Firecrawl ile detay alınıyor: {job['title'][:50]}...")
                markdown = scrape_job_details_with_firecrawl(job["url"], firecrawl_api_key)
                if markdown:
                    job["details"] = parse_job_details(markdown)
            
            all_new_jobs.append(job)
    
    # Deduplicate
    new_jobs = save_history(all_new_jobs)
    all_jobs = load_history()
    
    print(f"\n✅ {len(new_jobs)} yeni iş bulundu")
    
    # Output
    if args.output_format in ["json", "both"]:
        output_file = OUTPUT_DIR / f"jobs_{datetime.now().strftime('%Y%m%d')}.json"
        with open(output_file, "w") as f:
            json.dump(new_jobs, f, indent=2, ensure_ascii=False)
        print(f"📁 JSON kaydedildi: {output_file}")
    
    if args.output_format in ["telegram", "both"]:
        msg = format_telegram_message(new_jobs, all_jobs)
        print(f"\n📨 Telegram mesajı:\n{msg}")
        # Save for cron delivery
        with open(OUTPUT_DIR / "latest_telegram_msg.txt", "w") as f:
            f.write(msg)
    
    return new_jobs


if __name__ == "__main__":
    main()
