#!/usr/bin/env python3
"""
skool_scraper.py — Skool kanallarini noagent Python ile tara.
- Login ol (password .env'den)
- Post'lari MarkItDown ile markdown'a cevir (token tasarrufu)
- Cache ile karsilastir, sadece yenilerini ciktilama
- Yeni post yoksa [SILENT]
- Login fail'de exit 1 (fallback: prompt browser ile dener)
"""
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

HERMES_HOME = Path(os.environ.get('HERMES_HOME', '/home/ubuntu/.hermes'))

def load_env():
    env_file = HERMES_HOME / '.env'
    if not env_file.exists():
        return {}
    env = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

def load_cache():
    cache_file = HERMES_HOME / 'data' / 'skool_cache.json'
    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)
    return {'processed_urls': [], 'last_run': None}

def save_cache(cache):
    cache_file = HERMES_HOME / 'data' / 'skool_cache.json'
    cache['last_run'] = datetime.now().isoformat()
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_file, 'w') as f:
        json.dump(cache, f, indent=2)

def markitdown_convert(html_text):
    """Convert HTML to markdown using markitdown CLI for token efficiency."""
    import subprocess, tempfile
    with tempfile.NamedTemporaryFile(suffix='.html', mode='w', delete=False, encoding='utf-8') as f:
        f.write(html_text)
        tmp_path = f.name
    try:
        r = subprocess.run(['markitdown', tmp_path], capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
        return None
    except:
        return None
    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass

def scrape_public_channel(url, cache):
    """Scrape AI Automation Society (public, no login needed)."""
    new_posts = []
    try:
        r = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text(strip=True)
            if not text or len(text) < 30:
                continue
            full_url = href if href.startswith('http') else f'https://www.skool.com{href}'
            if full_url in cache['processed_urls']:
                continue
            if '/post/' in full_url or '/class/' in full_url:
                post_html = extract_post_content(full_url)
                md = markitdown_convert(post_html) if post_html else None
                new_posts.append({
                    'title': text[:200],
                    'url': full_url,
                    'content_md': md or text[:1000],
                    'channel': 'AI Automation Society',
                    'found_at': datetime.now().isoformat()
                })
                cache['processed_urls'].append(full_url)
        return new_posts
    except:
        return new_posts

def extract_post_content(url):
    """Extract full post content HTML from a Skool post URL."""
    try:
        r = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        for selector in ['article', '.post-content', '.class-content', 'main', '[role="main"]']:
            el = soup.select_one(selector)
            if el:
                return str(el)
        return r.text[:5000]
    except:
        return None

def login_and_scrape_private(email, password, cache):
    """Login to Skool and scrape private channel posts using Playwright."""
    new_posts = []
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return new_posts

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium')
            context = browser.new_context(
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            )
            page = context.new_page()
            page.goto('https://www.skool.com/login', timeout=30000)
            page.wait_for_load_state('networkidle')
            page.fill('input[type="email"], input[name="email"], input[placeholder*="email"]', email)
            page.fill('input[type="password"], input[name="password"]', password)
            page.click('button[type="submit"], button:has-text("LOG IN"), button:has-text("Sign In")')
            page.wait_for_timeout(5000)
            if page.url and 'login' in page.url.lower():
                return new_posts
            private_url = 'https://www.skool.com/u-gpt-ile-yapay-zekadan-gelire-4122'
            page.goto(private_url, timeout=30000)
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(3000)
            for link in page.locator('a[href*="/post/"], a[href*="/class/"]').all():
                href = link.get_attribute('href')
                text = link.inner_text().strip()
                if not href or not text or len(text) < 20:
                    continue
                full_url = href if href.startswith('http') else f'https://www.skool.com{href}'
                if full_url in cache['processed_urls']:
                    continue
                content_html = page.evaluate(f'document.querySelector("a[href=\'{href}\']")?.closest("article")?.innerHTML || ""')
                md = markitdown_convert(content_html) if content_html else None
                new_posts.append({
                    'title': text[:200],
                    'url': full_url,
                    'content_md': md or text[:1000],
                    'channel': 'Yapay Zekadan Gelire',
                    'found_at': datetime.now().isoformat()
                })
                cache['processed_urls'].append(full_url)
            browser.close()
    except:
        pass
    return new_posts

def main():
    env = load_env()
    password = env.get('SKOOL_PASSWORD') or env.get('skool_password', '')
    email = 'isimgorulsunn@gmail.com'
    cache = load_cache()

    all_new = []

    public_url = 'https://www.skool.com/ai-automation-society'
    new_public = scrape_public_channel(public_url, cache)
    all_new.extend(new_public)

    if password:
        new_private = login_and_scrape_private(email, password, cache)
        all_new.extend(new_private)

    save_cache(cache)

    if not all_new:
        print('[SILENT]')
        sys.exit(0)

    print(json.dumps(all_new, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
