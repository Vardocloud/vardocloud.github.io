# Puppeteer + Bitwarden Google Login (23 Haz 2026)

Cookie import (Option A) CookieMismatch hatasına takıldığında (Google'ın fingerprint güvenlik önlemi), Puppeteer MCP (`browser_navigate` / `browser_type` / `browser_click`) + Bitwarden'dan alınan şifre ile Google login tamamlanabilir.

## Akış

1. **Puppeteer ile Google sign-in sayfasına git:**
   ```
   browser_navigate(url="https://notebooklm.google.com/notebook/NOTEBOOK_ID")
   ```
   Bu otomatik olarak accounts.google.com'daki sign-in sayfasına yönlendirir.

2. **Email gir:**
   ```
   browser_type(ref="e...", text="isimgorulsunn@gmail.com")
   browser_click(ref="Next butonu")
   ```

3. **Şifreyi Bitwarden'dan al:**
   ```
   BW_SESSION=$(bw unlock --passwordenv BW_MASTER_PASSWORD ...)
   export BW_SESSION
   bw get password "Google"
   ```

4. **Şifre gir + Next:**
   ```
   browser_type(ref="password textbox", text="Parola")
   browser_click(ref="Next butonu")
   ```

5. **2FA bekle:** Google 2 adımlı doğrulama istediğinde, kullanıcıya telefon bildirimini onaylaması söylenir. "Don't ask again on this device" otomatik işaretliyse bir daha sormaz.

## Ön Koşullar

- **Bitwarden (bw) login durumda** ve `bw-serve` port 8087'de çalışıyor olmalı
- `BW_MASTER_PASSWORD` env var'da veya BWS secret'ta olmalı
- **Puppeteer MCP** (`browser_*` tools) Hermes config'de enabled olmalı
- Puppeteer'ın kullandığı Chrome **residential proxy'siz** çalışır — Google bot detection daha agresif olabilir

## Limitations

- **2FA gerektirir:** Hesapta 2FA etkinse, kullanıcının telefon bildirimini onaylaması gerekir. Bu adım otomatize edilemez.
- **Fingerprint detection:** Puppeteer'ın kullandığı Chrome da Google tarafından bot olarak algınabilir. "Got it" / "Try another way" gibi ek tıklamalar gerekebilir.
- **Sayfa timeout:** Google login sayfası bazen yavaş yüklenir. `browser_snapshot` ile her adımda sayfa durumunu kontrol et.
- **NotebookLM MCP'ye aktarma:** Bu yöntem sadece Puppeteer Chrome'un kendi session'ında login olur. NotebookLM MCP'nin kullandığı headless Chrome ayrı bir profile sahiptir. Login sonrası cookie'leri export edip MCP profiline import etmek gerekir.
