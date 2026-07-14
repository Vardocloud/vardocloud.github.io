# NotebookLM MCP — 6 Kritik Ders (24 Haz 2026)

## 1. stdout Kirliliği → JSONRPC Bozulması

**Sorun:** MCP banner ASCII art ve debug satırları (`│ Debug: False │`) stdout'a yazılıyor. JSONRPC de stdout'tan okunduğu için aynı kanala karışıyor. Hermes MCP client'ı parse error alıyor.

**Fix (`cli.py`):** `sys.stdout = sys.stderr`

**Kontrol:** `hermes mcp test notebooklm-mcp` çıktısında "✓ Connected" görmelisin, "parse error" değil.

## 2. excludeSwitches = CRASH

**Sorun:** `undetected-chromedriver`'da `excludeSwitches` parametresi Chrome'u crash ediyor. Bu Python exception DEĞİL — Chrome process'i sessizce düşüyor, Selenium `driver` None kalıyor.

**Belirti:** `_start_browser` exception fırlatmaz ama `self.driver = None`, `_is_authenticated = False`.

**Kural:** `excludeSwitches` KULLANMA. Kesinlikle.

## 3. Headless=False Formülü

Google bot detection'ı aşmak için 4 bileşen:
```
headless=False           → headed mod
+ custom UA              → "HeadlessChrome" ibaresi OLMADAN
+ DISPLAY=:99            → Xvfb
+ excludeSwitches yok    → crash etmez
```

**Neden:** Google `navigator.webdriver` + `HeadlessChrome` UA + `--headless` flag kombinasyonunu tespit ediyor.

## 4. Profil Transferi (VNC → MCP)

```bash
# Symlink yerine cp -r daha güvenilir
cp -r /home/ubuntu/.hermes/chrome_profile_notebooklm /home/ubuntu/.notebooklm/profiles/default/browser_profile
chown -R ubuntu:ubuntu /home/ubuntu/.notebooklm/
rm -f /home/ubuntu/.notebooklm/profiles/default/browser_profile/Singleton*
echo '{"cookies":[],"origins":[]}' > /home/ubuntu/.notebooklm/profiles/default/storage_state.json
```

## 5. Port Değişir

undetected-chromedriver her restartta **rastgele** bir port açar:
```bash
ps aux | grep "chromium.*remote-debugging-port" | grep -oP 'remote-debugging-port=\K\d+'
```

CDP bağlantısı (Playwright `connect_over_cdp`) için her restartta yeni port bulunmalı.

## 6. Eski US Cookie'leri KULLANMA

Oracle Cloud (US) IP'sinden export edilmiş Google cookie'leri:
- Google Security Alert tetikler ("Yeni bir cihazdan giriş yapıldı")
- Kullanıcıya gereksiz bildirim gider
- Hesap güvenlik riski oluşturur

**Kural:** Her zaman **güncel**, **Türkiye IP'sinden** export edilmiş cookie'leri kullan.
