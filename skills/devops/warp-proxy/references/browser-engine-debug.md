# Browser Engine Debug Trace (2026-05-28)

## Symptom
`browser_navigate` to Skool.com times out or returns empty page. WARP+ SOCKS5 proxy works fine via curl.

## Root Cause
`config.yaml` had `engine: local` which is **not a valid value**. Valid: `auto`, `chrome`, `lightpanda`.
Agent-browser fell back to `auto` → Browserbase cloud → bypassed WARP proxy entirely.

## Debugging Workflow (the lesson)

1. **Browser fails twice** → STOP retrying. Change strategy.
2. **Check logs immediately:**
   ```bash
   journalctl --user -u hermes-gateway --since '5m' --no-pager | grep -iE 'browser|engine|unknown'
   ```
3. **Key log line that revealed the bug:**
   ```
   WARNING tools.browser_tool: Unknown browser engine 'local' (valid: auto, chrome, lightpanda), falling back to 'auto'
   ```
4. **Fix:** `engine: local` → `engine: chrome` in config.yaml
5. **Restart:** `systemctl --user restart hermes-gateway`

## Verification Checklist
After any browser/WARP config change:
- Navigate to `https://ifconfig.me`
- IP should be **104.x.x.x** (Cloudflare), NOT 193.x (Oracle) or 76.x (Browserbase residential)
- `via` header should NOT contain "1.1 google"
- UA should be **Linux + Chrome**, NOT Mac + Chrome

## Config State (correct)
```yaml
# config.yaml
browser:
  engine: chrome
```
```bash
# .env
ALL_PROXY=socks5://127.0.0.1:1080
```
```bash
# warp-proxy service
systemctl is-enabled warp-proxy  # must be "enabled"
systemctl is-active warp-proxy   # must be "active"
```
