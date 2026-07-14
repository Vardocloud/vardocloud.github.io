# Telegram Kanalı — Veri Kaynağı Olarak Ekleme Pattern'i

Bir Telegram kanalını Ekonomi Zekası'na scrape edip veri kaynağı olarak eklemek için adım adım pattern.

---

## 1. Kanalı Keşfet

| Durum | Yöntem | Gereken |
|-------|--------|---------|
| **Public kanal** | `https://t.me/s/KANALADI` web görünümü | curl + BeautifulSoup yeterli |
| **Private kanal** | Telethon API | API ID + API Hash (my.telegram.org) + session |

Public kanal web görünümü **statik HTML döndürür** — JavaScript gerekmez. curl ile direkt çekilebilir.

## 2. Scraping Tekniği

### Temel Yakalama
```python
import requests
from bs4 import BeautifulSoup

url = f"https://t.me/s/{KANAL}"
headers = {'User-Agent': 'Mozilla/5.0 ...'}
r = requests.get(url, headers=headers, timeout=20)
soup = BeautifulSoup(r.text, 'html.parser')

for wrap in soup.select('.tgme_widget_message_wrap'):
    msg = wrap.select_one('.tgme_widget_message')
    post_id = msg['data-post'].split('/')[1]   # "BitcoinArisi/123" → "123"
    text = msg.select_one('.tgme_widget_message_text')
    time = msg.select_one('time')['datetime']
    views = msg.select_one('.tgme_widget_message_views').get_text(strip=True)
```

### CSS Selectors
| Alan | Selector | Not |
|------|----------|-----|
| Mesaj sarmalayıcı | `.tgme_widget_message_wrap` | Her mesaj için bir tane |
| Mesaj datası | `.tgme_widget_message[data-post]` | Benzersiz ID içerir |
| Mesaj metni | `.tgme_widget_message_text` | Düz metin + emoji |
| Zaman | `time[datetime]` | ISO 8601 formatı |
| Görüntülenme | `.tgme_widget_message_views` | "1.71K" formatında |
| Medya mesajı | `.message_media_not_supported_label` | Fotoğraf/video varsa |
| Link preview | `.link_preview_title` / `.link_preview_description` | Paylaşılan link başlığı |

### Sayfalama (Tüm Geçmiş)
Telegram web görünümü `?before=` parametresi ile sayfalar:
```python
# Sayfanın en altındaki "Load more" linkini bul
prev_link = soup.select_one('.js-messages_more_wrap a[href*="before="]')
if prev_link:
    href = prev_link.get('href', '')
    match = re.search(r'before=(\d+)', href)
    next_before = match.group(1)  # Sonraki sayfanın before parametresi
    next_url = f"{BASE_URL}?before={next_before}"
```

**Not:** Web görünümü sadece **son ~30 mesajı** gösterir. Daha eskileri için sayfalama gerekir. Tüm geçmiş isteniyorsa `before` parametresi ile loop yap.

## 3. Filtreleme Pattern'leri

### Reklam / Bot Tanıtımı
```python
REKLAM_KELIMELER = [
    r'@\w+_bot', r'bot', r'reklam', r'ücretsiz',
    r'sinyal', r'giriş yap', r'kaydol', r'premium',
    r'vip', r'özel üyelik', r'davet et', r'çevrenizi davet',
]
# Eğer sadece @mention varsa ve mesaj kısa (<150 chars) → reklam
if re.search(r'@\w+', mesaj) and len(metin) < 150:
    return True
```

### Kategorizasyon
| Kategori | Anahtar Kelimeler | Örnek |
|----------|-------------------|-------|
| 📉 Drop fırsatı | `direnç`, `destek`, `düşüş`, `fırsat`, `alım` | "Solana 87,5$ direnci kırılırsa..." |
| 💎 Ucuz yatırım | `0,\d+\$`, `ön satış`, `presale`, `ico`, `erken` | "$VOID 0,0012$ presale" |
| 🎯 Hedef fiyat | `hedef`, `orta vade`, `beklenen` | "Orta vade hedef 240$" |

### Kripto Türü Tespiti
```python
COIN_MAP = {
    'bitcoin': 'Bitcoin', 'btc': 'Bitcoin',
    'solana': 'Solana', 'sol ': 'Solana',
    'sui': 'Sui', 'chz': 'Chiliz', 'chiliz': 'Chiliz',
}
```

## 4. Cron Entegrasyonu

### İki Aşamalı Mimarı (Önerilen)

```
[Kanal Tarama]
  no_agent cron (günde 1 kere)
  ↓
bitcoin-arisi-tarayici.py --cron
  ↓                   ↓
JSON veri dosyası    stdout (sadece yeni varsa)
(~/.hermes/data/     → Telegram bildirimi
 <kanal>/)
  ↓
[Ekonomi Zekası Bülteni]
  cron (günde 2 kere)
  ↓
JSON dosyasını oku → bültende kullan
```

### Tarama Cron'u (no_agent=True)
```yaml
schedule: "0 9 * * *"        # Günde 1 kere, sabah
no_agent: true
script: python3 ~/.hermes/scripts/kanal-tarayici.py --cron
# --cron modu: sadece yeni mesaj varsa çıktı verir
# Yeni mesaj yoksa → boş stdout → [SILENT]
```

### Bülten Entegrasyonu
Bülten cron prompt'unda:
```
### 1G. 🐝 KANALADI — Konu
- Dosyayı kontrol et: ~/.hermes/data/kanal/birikim-fikirleri.json
- Son 24 saatte yeni fırsat varsa bültende paylaş
```

### Script'te --cron Modu Deseni
```python
def cron_cikisi(veri):
    yeni = veri['istatistik']['yeni_mesaj']
    if yeni == 0:
        return  # boş stdout → cron [SILENT]
    print(f"🐝 @Kanal — {yeni} YENİ MESAJ")
    print(f"💰 Birikim fikri: {len(fikirler)}")
    # En yeni 3 fikri göster
    for f in fikirler[:3]:
        print(f"  [{f['tarih']}][{f['kripto']}] {f['metin'][:150]}")
```

## 5. Veri Dizini Yapısı
```
~/.hermes/data/
  └── <kanal-adi>/
      ├── mesajlar.json          # Tüm ham mesajlar (id → mesaj)
      └── birikim-fikirleri.json # Filtrelenmiş + kategorize edilmiş çıktı
```

## 6. Pitfall'lar

- **Rate limiting:** t.me/s/ sayfasına 30sn'de 1'den fazla istek atma — IP ban yiyebilirsin
- **Sayfalama loop:** `before` parametresi aynı sayfayı döndürebilir — `mevcut_idler` seti ile duplicate kontrolü yap
- **HTML yapısı değişikliği:** Telegram web widget HTML'i nadiren değişir ama değişirse selector'lar kırılır. `browser_vision` ile periyodik kontrol önerilir
- **Medya mesajları:** Fotoğraf/video mesajları `.tgme_widget_message_text` içermez — alternatif selector'dan kontrol et
- **no_agent=True sessizlik:** Script boş stdout üretirse cron otomatik sessiz kalır. Hata durumunda bile boş stdout = sessizlik. Hataları stderr'e yaz, `2>&1` ile cron'a yansıtmamaya dikkat et

---

## Örnek: Bitcoin Arısı (@BitcoinArisi)

- **Script:** `~/.hermes/scripts/bitcoin-arisi-tarayici.py`
- **Cron:** `9d515802f2b2` (09:00, no_agent)
- **Veri:** `~/.hermes/data/bitcoin-arisi/`
- **Kategori:** Kripto drop + presale fırsatları
- **Filtre:** @Btcarisi_bot reklamları atlanır
