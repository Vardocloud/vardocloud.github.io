# YouTube Ekonomi Kanalları — Takip Listesi & Veri Çekme Rehberi

**Oluşturma:** 27 Haziran 2026
**Amaç:** API anahtarı olmadan YouTube ekonomi/yatırım kanallarından video listesi ve transcript çekme.

---

## 📺 Kanal Listesi

### Türkçe Kanallar
| Kanal | Handle | Channel ID | Abone | Odak |
|-------|--------|------------|-------|------|
| Kayıt Dışı İktisat (Prof. Dr. Ceyhun Elgin) | @Kayitdisi | `UCFrDHMXMBvxkPryv1qRxhtw` | 66.8K | Makro, Türkiye ekonomisi |
| Yatırım 101 | @yatirim101 | `UCWsudnBrEOJLQ1JpkdloxKg` | 384K | Portföy yönetimi, BIST |
| Kendine Milyoner (Self Millionaire) | @KendineMilyoner | `UCjdUCRPvoqvTVBJZfEZrd1A` | 80.5K | Finansal okuryazarlık |
| Borsadan Hisse | @borsadanhisse | `UC2n7FaAFNuIpR9Ul3R_MGuw` | 86.8K | Teknik analiz, BIST |

### Yabancı Kanallar
| Kanal | Handle | Channel ID | Abone | Odak |
|-------|--------|------------|-------|------|
| Mark Tilbury | @marktilbury | `UCxgAuX3XZROujMmGphN_scA` | 8.56M | Yatırım, finansal özgürlük |

---

## 🔧 Veri Çekme Yöntemleri (API Anahtarı Gerekmez)

### 1. RSS Feed — Son Videoları Listele

Her kanalın RSS feed'i:
```
https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}
```

Python ile çekme:
```python
import urllib.request, xml.etree.ElementTree as ET

rss_url = f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'
req = urllib.request.urlopen(rss_url, timeout=10)
tree = ET.parse(req)
root = tree.getroot()
ns = {'atom': 'http://www.w3.org/2005/Atom'}
entries = root.findall('atom:entry', ns)
for entry in entries:
    title = entry.find('atom:title', ns).text
    video_id = entry.find('atom:videoId', ns).text
```

**web_extract ile de doğrudan RSS çekilebilir:**
```
web_extract(["https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"])
```

### 2. Transcript — Video Altyazılarını Çek

```python
from youtube_transcript_api import YouTubeTranscriptApi

# Yeni API (v2) — get_transcript() DEĞİL, .fetch() kullan
api = YouTubeTranscriptApi()
transcript = api.fetch(video_id, languages=['tr', 'en'])

# transcript = liste, her segment: {start: float, text: str, duration: float}
for seg in transcript[:5]:
    print(f'[{seg.start:.1f}s] {seg.text}')
```

**Önemli:** Eski API (`YouTubeTranscriptApi.get_transcript(video_id)`) kullanımdan kalktı. Yeni API:
```python
api = YouTubeTranscriptApi()
api.fetch(video_id)                    # Varsayılan dil: İngilizce
api.fetch(video_id, languages=['tr'])  # Türkçe altyazı
```

### 3. oEmbed — Video Metaverisi (API'siz)

```
https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={VIDEO_ID}&format=json
```

Dönen JSON: `title`, `author_name`, `author_url`, `thumbnail_url`, `html`

### 4. Kanal ID Keşfi — Browser Console ile

Bir video veya kanal sayfasında browser console'da çalıştır:
```javascript
JSON.stringify(window.ytInitialData).match(/"channelId":"(UC[^"]+)"/)
// veya
JSON.stringify(window.ytInitialData).match(/"externalChannelId":"(UC[^"]+)"/)
```

**Alternatif:** Kanala ait bir videoyu aç, browser console'da:
```javascript
(function() {
  const data = JSON.stringify(window.ytInitialData);
  const match = data.match(/"channelId":"(UC[^"]+)"/);
  return match ? match[1] : 'not found';
})()
```

---

## ✅ Test Sonuçları (27 Haz 2026)

| Yöntem | Durum | Not |
|--------|-------|-----|
| RSS Feed | ✅ Çalışıyor | Her kanal için son 15 video |
| Transcript (Türkçe) | ✅ Çalışıyor | 660 segment (Ceyhun Elgin videosu) |
| Transcript (İngilizce) | ✅ Çalışıyor | Otomatik çeviri mevcut |
| yfinance canlı veri | ✅ Çalışıyor | Altın, Dolar/TL, BIST |
| oEmbed | ✅ Çalışıyor | Video başlık, kanal adı, thumbnail |
| Channel ID (browser) | ✅ Çalışıyor | ytInitialData JSON |

---

## 📊 yfinance Entegrasyonu

```python
import yfinance as yf

# Altın fiyatı
gold = yf.Ticker('GC=F')
gold_price = gold.history(period='2d')['Close'].iloc[-1]

# Dolar/TL
usdtry = yf.Ticker('USDTRY=X')
usd_price = usdtry.history(period='2d')['Close'].iloc[-1]

# BIST100 endeksi
bist = yf.Ticker('XU100.IS')
bist_price = bist.history(period='2d')['Close'].iloc[-1]
```

**Önemli Ticker Sembolleri:**
- Altın ons: `GC=F`
- Gümüş: `SI=F`
- Bakır: `HG=F`
- Dolar/TL: `USDTRY=X`
- Euro/TL: `EURTRY=X`
- BIST100: `XU100.IS`
- S&P500: `^GSPC`
- Ham Petrol: `CL=F`
