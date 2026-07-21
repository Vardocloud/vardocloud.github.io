---
name: browser
description: Umbrella for browser-related Hermes skills (navigation patterns, Cloudflare strategy, etc.)
umbrella: true
category: browser
---

# Hermes Browser Umbrella

This umbrella consolidates browser-related skills into a reusable library. It provides labeled subsections for absorbed skills to improve discoverability and reuse.

## Absorbed Skills (umbrella)

- browser-smart-navigation
- cloudflare-bot-bypass
- **headless-browser-auth** (see `devops/headless-browser-auth`) — Headless browser cookie auth for Google/NotebookLM: Camofox managed persistence, Playwright CDP, cookie import/refresh, Google sign-in bot blockade workarounds

### browser-smart-navigation

Core strategy: Intelligent navigation with snapshot control and anti-repeat rules. Includes a decision tree and guardrails for efficient browsing.

### cloudflare-bot-bypass

Pattern notes: Bot-detection evasion considerations for Cloudflare, with caveats on platform policies and recommended safe operational patterns.
