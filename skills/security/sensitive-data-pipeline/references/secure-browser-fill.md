# Secure Browser Fill — Reference

## Files

- **Script (v1 — basic):** `~/.hermes/tools/secure_browser_fill.py`
- **Script (v2 — robust, recommended):** `~/.hermes/tools/secure_browser_fill_v2.py`
- **HTML template:** `~/elements_secure_login.html`

## How to Use

1. Share the HTML page with the user (send as MEDIA or direct file)
2. User opens it locally (file://), enters credentials, clicks "Generate Code"
3. User pastes the `VANITAS_SECURE::<base64>` code into chat
4. Call terminal: `python3 ~/.hermes/tools/secure_browser_fill_v2.py '<the_code>'`
5. Script returns JSON with status only

## Script Comparison

| Feature | v1 | v2 |
|---|---|---|
| Automation detection bypass | ❌ | ✅ (`navigator.webdriver`, `navigator.plugins`) |
| Human-like delays | ❌ | ✅ (0.3–0.5s between actions) |
| JS-based button enable fallback | ❌ | ✅ (if disabled button detected) |
| Input field scanning | ❌ | ✅ (logs all inputs for debugging) |
| `add_init_script` | ❌ | ✅ |
| Verified working (course.elementsofai.com) | ❌ (failed) | ✅ (success) |

## Test Command

```bash
python3 ~/.hermes/tools/secure_browser_fill_v2.py "VANITAS_SECURE::dGVzdEB0ZXN0LmNvbXx8fHRlc3QxMjM="
```

## Debugging

If the script fails:
1. Check Ollama is running: `curl http://localhost:11434/api/tags`
2. Check Chromium is installed: `ls ~/.cache/ms-playwright/chromium-*/chrome-linux/chrome`
3. Run manually to see full error traceback
4. Screenshots saved at `/tmp/elements_login_filled.png` (v1) or `/tmp/elements_login_v2.png` (v2)
5. To debug selector issues locally: use `tesseract` on the screenshot for OCR analysis

## Security Notes

- Always wrap the base64 code in single quotes when passing to terminal (prevents shell interpretation of special chars)
- The script NEVER writes decoded credentials to stdout — only status messages
- The Playwright instance creates a FRESH browser session (no shared cookies with Vanitas browser tools)
