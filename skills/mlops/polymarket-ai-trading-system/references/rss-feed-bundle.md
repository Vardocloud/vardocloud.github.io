# RSS Feed Bundle — Polymarket News Signal Strategy

14 kaynak, 4 kategoride. Tümü blogwatcher-cli v0.2.1 ile yönetilir.

## Kurulum ve Yönetim

```bash
# Veritabanı (varsayılan: /data/pm-trader/blogwatcher.db)
# Docker'da /data/ yoksa: ~/.local/share/pm-trader/blogwatcher.db
DB="/data/pm-trader/blogwatcher.db"
# Fallback:
# DB="$HOME/.local/share/pm-trader/blogwatcher.db"

# Feed ekleme (homepage + explicit feed URL)
blogwatcher-cli --db $DB add "Name" "https://homepage.com" --feed-url "https://feed.url/rss.xml"

# Feed silme (pipe gerektirir)
echo "y" | blogwatcher-cli --db $DB remove "Name"

# Tüm feed'leri tara
blogwatcher-cli --db $DB scan

# Bekleyen makaleleri listele
blogwatcher-cli --db $DB articles

# Son durum
blogwatcher-cli --db $DB blogs
```

## Kaynaklar

### ₿ Kripto (Kraken IPO, airdrop, kripto regülasyon)
| Kaynak | Homepage | Feed URL |
|--------|----------|----------|
| CoinDesk | coindesk.com | coindesk.com/arc/outboundfeeds/rss |
| CoinTelegraph | cointelegraph.com | cointelegraph.com/rss |
| Decrypt | decrypt.co | decrypt.co/feed |
| Blockworks | blockworks.com | blockworks.com/feed |

### 🏛️ UK Siyaset (Starmer, UK election)
| Kaynak | Homepage | Feed URL |
|--------|----------|----------|
| BBC Politics | bbc.com/news/politics | feeds.bbci.co.uk/news/politics/rss.xml |
| BBC World | bbc.com/news/world | feeds.bbci.co.uk/news/world/rss.xml |
| Guardian Politics | theguardian.com/politics | theguardian.com/politics/rss |
| Telegraph | telegraph.co.uk | telegraph.co.uk/rss.xml |

### 🤖 Tech/AI (OpenAI, GPT-5)
| Kaynak | Homepage | Feed URL |
|--------|----------|----------|
| TechCrunch | techcrunch.com | techcrunch.com/feed/ |
| Ars Technica | arstechnica.com | feeds.arstechnica.com/arstechnica/index |
| The Verge | theverge.com | theverge.com/rss/index.xml |
| OpenAI Blog | openai.com/news | openai.com/news/rss.xml |
| Hacker News | news.ycombinator.com | hnrss.org/frontpage |

### 🌍 Dünya (Ukrayna, NATO, Macron)
| Kaynak | Homepage | Feed URL |
|--------|----------|----------|
| Al Jazeera | aljazeera.com | aljazeera.com/xml/rss/all.xml |

## Notlar

- **Reuters/AP:** Public RSS yok. İçerikleri SearXNG üzerinden çekilir.
- **The Block:** RSS'i var ama cloudflare korumalı (403). SearXNG kullan.
- **DB yolu:** `/data/pm-trader/blogwatcher.db` (Docker'da yoksa `~/.local/share/pm-trader/` kullan) — SQLite, doğrudan sorgulanabilir.
- **Önemli kolonlar:** `articles.published_date` (NOT `published_at`), JOIN: `articles.blog_id = blogs.id`
- **Makale sayısı:** İlk scan ~1500+ makale, günlük ~200-300 yeni.
