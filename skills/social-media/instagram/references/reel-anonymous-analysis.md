# Anonymous Reel Analysis (Browser + Vision)

Instagram Reel içeriğini **login olmadan** browser üzerinden analiz etme tekniği.

## Prerequisites

### Pollinations API Key (Vision İçin ZORUNLU)

Instagram Reel analizinde **vision** (görsel içerik analizi) için Pollinations API key'i gerekir. Edel'in tercihi: **Pollinations MCP + queen (qwen-vision)** modeli. API key yoksa vision araçları 401 Authentication Required hatası verir.

**Akış:**
1. `~/.hermes/bin/bws secret list` ile POLLINATIONS_API_KEY ID'sini bul
2. `mcp_pollinations_setApiKey(key="<value>")` ile ayarla

> ⚠️ **PITFALL:** `setApiKey` başarılı dönse bile (`authenticated: true`), `describeImage` ve `chatCompletion` araçları bazen "Authentication failed" hatası verebilir. Bu durumda snapshot metin analizine düş.

## Workflow

1. **Pollinations API Key'i ayarla** — Önce `mcp_pollinations_setApiKey` ile Pollinations secret key'ini ayarla (BWS'den al). Yoksa vision adımı 401 hata verir.

2. **Navigate** — `browser_navigate(url)` ile Reel linkini aç. İlk denemede timeout alınırsa tekrar dene — Instagram bazen yavaş yüklenir.

3. **Login pop-up'ı kapat** — Sayfa yüklenince "Sign up" / "Log in" pop-up'ı gelir. `browser_snapshot` ile close butonunun ref ID'sini bul (genellikle "Close" veya "X" butonu, ref=e167 gibi), tıkla.

4. **Vision ile analiz** — Pop-up kapandıktan sonra iki yöntem:
   
   **Birincil (tercih edilen):** Pollinations MCP queen (qwen-vision) modeli
   ```python
   browser_vision ile screenshot al -> screenshot path'ini kullan
   Screenshot'ı geçici HTTP sunucu ile serve et:
     python3 -m http.server 8765 --bind 127.0.0.1 --directory /tmp/reel_serve (background)
   mcp_pollinations_describeImage(
     imageUrl="http://127.0.0.1:8765/screenshot.png",
     model="openai",
     prompt="Videoda tam olarak ne anlatılıyor? ..."
   )
   ```
   
   **İkincil (fallback):** `browser_vision` (Pollinations key ayarlıysa çalışabilir)

5. **Video açıklaması** — Snapshot'taki StaticText'lerden video caption'ını oku.

6. **Profil bilgisi** — Hesap adı, verified durumu, snapshot'tan oku.

7. **Yorum analizi (Kritik)** — Yorumlar videonun gerçek doğasını ortaya çıkarır. Snapshot'taki tüm yorum StaticText'lerini tara. Olumsuz/şüpheci yorum oranı yüksekse video "get rich quick" veya sahte vaat içeriyordur.

## Neler Görünür

| Öğe | Durum |
|-----|-------|
| Video player | ✅ Oynatılabilir, ses kapalı |
| Caption/açıklama | ✅ Görünür |
| Yorumlar | ✅ Görünür (ilk birkaç) |
| Like/save/comment sayıları | ✅ Görünür |
| Profil adı + verified | ✅ Görünür |
| Diğer postlar (grid) | ✅ Görünür |
| Bio | ❌ Login gerekebilir |

## Limits

- Video **sesini** analiz edemezsin — sadece görsel içerik
- Uzun videolarda vision birkaç kareyi yakalar, tam akışı kaçırabilir
- Instagram bazen bot detection yapar — WARP SOCKS5 proxy varsa onu kullanan bir Chrome instance'ı tercih et

## Pitfalls

### Vision API Auth Failure → Snapshot Fallback

`browser_vision` veya `vision_analyze` bazen 401 Authentication Required hatası verebilir (Pollinations API key yoksa veya geçersizse). Bu durumda **panik yapma** — snapshot metninde analiz için yeterli veri var:

| Ne var? | Nerede? |
|---------|---------|
| Video caption/açıklama | `StaticText` içinde, genellikle profil adının altında |
| Hesap adı | `link` öğesinde |
| Yorumlar | Her yorum `StaticText` olarak snapshot'ta görünür |
| Like/süre bilgisi | `StaticText` veya `time` elementlerinde |
| Hesap tipi (verified) | `image "Verified"` elementi |

**Analiz ipucu:** Yorumlar genellikle videonun gerçek doğasını ortaya çıkarır. Olumsuz/şüpheci yorumlar "get rich quick" veya sahte vaat içeriklerini işaret eder. Yorum tonunu analiz ederek videonun güvenilirliği hakkında çıkarım yapabilirsin.

### Cookie Durumunun Anonymous Erişime Etkisi

- `sessionid` eksik olsa bile (cookie'de sadece `csrftoken` varsa) **Reel sayfası açılır ve içerik görünür**
- Cookie'siz de aynı sonuç — Instagram Reel sayfaları login olmadan public erişime açık
- Cookie preflight check'te `sessionid: ❌` görmek panik sebebi değil — anonymous analysis için sorun yok
- **Sadece DM, profil düzenleme, post paylaşma gibi işlemlerde sessionid gerekir**

## NE ZAMAN KULLANILIR

- Edel "şu linke bak ne anlatıyor" dediğinde
- IG operasyonu kapsamında hedef hesap içeriğini analiz ederken
- Trendleri takip ederken
