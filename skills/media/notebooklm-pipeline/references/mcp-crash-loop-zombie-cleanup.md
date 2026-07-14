# MCP Crash-Loop + Zombie Cleanup (24 Haz 2026)

## Problem

NotebookLM MCP authenticate olamadığında (cookie'ler expire olmuş, profil bozulmuş), MCP
her restart denemesinde yeni bir `undetected_chromedriver` + Chrome instance'ı başlatır.
Zamanla bu process'ler birikir:

```
ps aux | grep undetected_chromedriver | wc -l  # 10+ olabilir
ps aux | grep chrome_profile_notebooklm | wc -l  # birden çok Chrome
```

## Belirtiler

1. **MCP healthcheck:** `{status: "needs_auth", authenticated: false}` — sürekli bu durumda
2. **Zombie birikmesi:** `undetected_chromedriver` process'leri onlarcaya çıkar
3. **Chrome ProcessSingleton hatası:** Aynı profile birden çok Chrome bağlanmaya çalışınca
   `"An instance of Chromium already exists"` benzeri hatalar (genelde sessizce başarısız olur)
4. **Disk şişmesi:** Her Chrome yeni bir crash dump + profile kopyası oluşturur

## Çözüm — Temizlik ve Sıfırdan Başlatma

### Adım 1: Tüm Chrome/undetected_chromedriver Process'lerini Öldür

```bash
# Tüm MCP ilişkili process'leri temizle
pkill -f undetected_chromedriver 2>/dev/null
pkill -f "chrome.*notebooklm" 2>/dev/null
pkill -f notebooklm-mcp 2>/dev/null
sleep 2
# Doğrulama
ps aux | grep -E "(undetected_chromedriver|chrome.*notebooklm|notebooklm-mcp)" | grep -v grep
# → boş olmalı
```

### Adım 2: VNC Stack + Cloudflared'ı Yeniden Başlat

Xvfb ve x11vnc genelde hala çalışıyordur. Sadece cloudflared'ı yenile:

```bash
# cloudflared'ı öldürüp yeniden başlat
pkill -f cloudflared 2>/dev/null
sleep 2
/tmp/cloudflared tunnel --url http://localhost:6080 --no-autoupdate &
sleep 5
# URL'yi al (process output'undan)
```

### Adım 3: "hazır" Protokolü

- **Kullanıcı VNC'de login olana kadar HİÇBİR ŞEY YAPMA**
- Playwright navigasyonu, browser yenileme, sayfa müdahalesi — hepsi YASAK
- Sadece kullanıcı "giriş yaptım", "al artık", "hazır" dedikten SONRA adım at

### Adım 4: CDP ile storage_state Export Et

Kullanıcı login olduktan sonra VNC'deki Chrome'a CDP ile bağlan:

```python
from playwright.async_api import async_playwright
import json

# VNC'deki Chrome'un debugging port'unu bul
# (genelde 41227, 40333 gibi — ps aux | grep remote-debugging-port)
CDP_URL = "http://127.0.0.1:41227"

async def export_state():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]
        state = await context.storage_state()
        with open("/home/ubuntu/.hermes/notebooklm_storage_state.json", "w") as f:
            json.dump(state, f)
        print(f"✅ {len(state.get('cookies',[]))} cookie export edildi")
        await browser.close()
```

### Adım 5: Empty storage_state + MCP Restart

```bash
# storage_state'i boşalt — Selenium _load_cookies() sessizce Playwright cookie'lerini düşürür
echo '{"cookies":[],"origins":[]}' > /home/ubuntu/.hermes/notebooklm_storage_state.json

# MCP'yi başlat (config'deki ayarlarla)
# Profile zaten login durumda olduğu için MCP headless Chrome'u auth'lanır
```

### Adım 6: Healthcheck Doğrula

```python
# MCP ayağa kalktıktan sonra
# healthcheck → {status: "healthy", authenticated: true}
```

## Tam Akış (24 Haz 2026)

```
1. Kullanıcı "aç bidaha" / "hazır" der
2. Zombie process'leri temizle
3. VNC URL'yi kullanıcıya ver
4. Kullanıcı NoteboookLM'a login olur
5. Kullanıcı "giriş yaptım al artık" der
6. CDP ile storage_state export et
7. TÜM Chrome/undetected_chromedriver process'lerini öldür (Adım 1 tekrar)
8. Empty storage_state yaz
9. MCP'yi restart et
10. Healthcheck ile doğrula
```

## ÖNEMLİ

- Her restart denemesi yeni zombie yaratır. Başarısız denemelerden sonra mutlaka temizle.
- storage_state.json export başarılı görünse bile MCP _load_cookies() sessizce düşürebilir.
  Empty storage_state trick (Option I) bu sorunu çözer.
