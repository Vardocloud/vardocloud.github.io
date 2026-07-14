# News-Driven Polymarket Trading — Cron Job Workflow

This reference documents the MWF (Monday-Wednesday-Friday) Polymarket news signal
scan run by the `pm-trader` cron job. It combines web research, market data, and
rules-based trading decisions.

## Overview

The scan runs as a scheduled cron job (no user present). The pre-run data
collection script (`pm-trader scan`) fetches markets and RSS articles, saving
to `/data/pm-trader/latest_scan.json`. The agent then:

1. Reads the collected data
2. Checks the current portfolio
3. Researches news signals for each market
4. Applies trading decision rules
5. Produces a structured report

## Data Pipeline

### Pre-run Script (runs before agent)
```bash
# pm-trader scan — collects data from Polymarket + RSS
# Output: /data/pm-trader/latest_scan.json
```

Fields in the JSON:
- `markets[].market.slug` — market identifier for `pm-trader buy`
- `markets[].market.question` — human-readable question
- `markets[].market.yes_price` / `no_price` — current probabilities (0-1)
- `markets[].market.volume` — total volume in USDC
- `markets[].market.liquidity` — liquidity depth
- `markets[].market.end_date` — resolution date
- `markets[].news` — RSS article matches for this market
- `markets[].news_count` — how many articles found

### Portfolio Check
```bash
pm-trader portfolio --format json 2>/dev/null
```
Returns current positions (empty/error = no active positions).

## News Research Methodology

For each non-expired, non-meme market with liquidity:

1. **web_search** with relevant query terms (market-specific)
   - e.g., `"Keir Starmer UK politics resignation June 2026"`
   - e.g., `"Kraken IPO 2026 latest news"`
2. **web_extract** on promising articles for deep analysis
   - Wikipedia, CNN, Reuters, Bloomberg, local news
3. **Follow-up searches** for specific claims or dates
   - By-election dates, poll numbers, resignation announcements

### Market Filtering Rules
- Skip expired markets (YES/NO at 0 or 1, zero liquidity)
- Skip irrational/meme markets (GTA VI, obvious joke markets)
- Skip markets where news cannot drive the outcome
- Focus on REAL news-driven markets only

## Trading Decision Rules

```
News strongly supports YES and price < 40% → BUY YES (confidence > 65%)
News strongly supports NO  and price > 60% → BUY NO  (confidence > 65%)
```

### Sizing
- Max 3 concurrent positions
- Max $500 per position
- Size = $500 × confidence (confidence as decimal, e.g., 0.65)
- If no market meets strict criteria → no trades

### Execution
```bash
pm-trader buy SLUG YES $SIZE
pm-trader buy SLUG NO $SIZE
```

## Report Format

Keep reports short and structured:

```
📡 **News Signal Scan — {Day}, {Date}**
├ Marketler: {X} taranan ({Y} meme/spekülatif elendi)
├ Haberler: {N} RSS + web search
├ Analiz: sadece haber-driven marketler
├ Yeni trades: {N}
├ Portföy: {X} pozisyon
└ P&L: ${amt}

Trade varsa:
├ 💰 {slug} {YES/NO} ${size} @ {price:.0%}

Sinyal yoksa:
└ 🤖 Haber-driven fırsat bulunamadı.
```

## Example: UK Politics Market Analysis

The Starmer leadership crisis markets are a recurring high-signal opportunity.
Pattern to follow:

1. **Identify trigger:** By-election date, MP resignations, cabinet exits
2. **Check polls:** PollCheck, YouGov, constituency-level polling
3. **Read news:** CNN, BBC, Manchester Evening News for local context
4. **Assess timing:** Compare end_date vs procedural timelines
   - Leadership challenge process takes weeks, not days
   - by-election result ≠ immediate resignation
5. **Price evaluation:** Compare current price vs news-supported probability

### Key Sources for UK Politics
- Wikipedia (leadership crisis pages)
- CNN UK edition (edition.cnn.com/uk)
- Manchester Evening News (local by-election coverage)
- PollCheck (pollcheck.co.uk — constituency polling)
- GB News, The Guardian, NYT

## Common Pitfalls

- **Stale news:** A month-old article is already priced in. Look for TODAY's news.
- **Timeline mismatch:** News supports YES on a long horizon, but market end_date is too soon.
- **Binary events:** By-election results, court rulings, or votes can swing markets 20-30 points overnight. Size accordingly.
- **Low liquidity:** Markets with <$10K liquidity may have unreliable prices or be impossible to trade at displayed price.
- **End-date cliff:** Markets expiring within 2 weeks behave differently from longer-dated ones — less time for news to play out.

## Related Skills & Tools

- `pm-trader` CLI — scan, portfolio, buy, sell commands
- `polymarket` skill (this umbrella) — API data queries
- `web_search` + `web_extract` — news research
- `unified-search` skill — multi-API search orchestration for deeper research
