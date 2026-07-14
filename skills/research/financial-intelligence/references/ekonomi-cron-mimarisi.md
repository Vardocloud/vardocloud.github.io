# Ekonomi Cron'u Mimarisi

**Amaç:** Bundle + Google haberlerinden ekonomi verisi topla, Buffett perspektifinden yorumla, Telegram'a yolla. Zamanla NotebookLM + simülasyon ekle.

---

## ✅ V1: Temel Cron (Kurulu — 27 Haz 2026)

### Zamanlama: Günde 2 Kere
- **Sabah 08:00** — Piyasa öncesi (Asya kapanışı, ABD vadeli, gece haberleri)
- **Akşam 18:00** — Gün sonu (BIST kapanış, emtia güncellemesi)

### Veri Kaynakları (çalışan)
```
web_extract → BBC Business (https://www.bbc.com/news/business)
web_search  → "BIST 100", "Türkiye ekonomisi", "altın fiyatları", "dolar kuru"
yfinance    → Altın (GC=F), USD/TRY (USDTRY=X), BIST100 (XU100.IS)
YouTube RSS → 5 ekonomi kanalının son videoları (opsiyonel cron ile)
```

### Analiz Katmanı
Her haber için:
1. 5N1K özet
2. Buffett filtresi (moat, fiyat/değer, uzun vade)
3. Fırsat/risk etiketi
4. Makro bağlantı (faiz/enflasyon/büyüme ile ilişki)

### Çıktı Formatı
``` 
📈 EKONOMİ ZEKASI — {SABAH/AKŞAM} BÜLTENİ
{DD Month YYYY} | {saat}

📍 MANŞET
📰 HABERLER (her biri: 📋 5N1K → 🎯 Buffett → ⚡ Fırsat/Risk → 🔮 Beklenti)
📊 MAKRO PANEL (faiz, enflasyon, dolar, altın, BIST100, CDS)
🎯 ÖNE ÇIKAN FIRSAT/RİSK
```
- Telegram: `deliver="origin"` (mevcut sohbete)
- Format: Kısa + öz + aksiyon odaklı

### Cron Job (çalışan)
- **Job ID:** `3acdcd93e3b7`
- **Schedule:** `0 8,18 * * *`
- **Skills:** `financial-intelligence`, `sohbet`
- **Model:** `deepseek-v4-flash-free` / `opencode-zen`
- **Toolsets:** `web`, `terminal`, `file`, `search`
- **İlk çalışma:** 27 Haz 2026 18:00

---

## ✅ V2: NotebookLM Entegrasyonu (Kurulu — 27 Haz 2026)

### Ekonomi Notebook'u
- **Adı:** `📈 Ekonomi Zekası — Yatırım İstihbaratı`
- **Notebook ID:** `1d205988-6c7f-41e8-8079-dd579444cc1e`
- **URL:** https://notebooklm.google.com/notebook/1d205988-6c7f-41e8-8079-dd579444cc1e
- **Yüklenen Kaynaklar:**
  - Yatırım Stratejisi wiki sayfası
  - Financial Intelligence SKILL.md (Buffett 12 kriter)
  - Ekonomi Cron Mimarisi (bu doküman)
- **Chat Konfigürasyonu:** Custom prompt — Buffett-style yatırım analisti
  - Yanıt yapısı: 📋 Ne Oldu? → 🎯 Yatırım Gözlüğü → ⚡ Fırsat/Risk → 🔮 Beklenti
  - Makro bağlantı zorunlu
  - Yatırım tavsiyesi değildir uyarısı
  - Türkçe yanıt
- **Tags:** ekonomi, yatırım, finans, buffett, borsa, makro

### Auth Yönetimi
- Mevcut `nb_keepalive_2h` cron'u auth'u canlı tutar
- Auth expire olursa: `nlm login` terminal komutu
- MCP refresh: `mcp_notebooklm_mcp_refresh_auth()` çağrısı

### Pipeline (planlanan)
```
Cron çalışır → çıktıyı Telegram'a yolla → 
özeti NotebookLM'e kaynak olarak ekle (manuel/otomatik) → 
NotebookLM otomatik podcast/rapor üretsin
```

---

## 🟡 V3: YouTube Kanalları (Kurulu — 27 Haz 2026)

### Takip Edilen Kanallar
5 kanal tespit edildi, kanal ID'leri alındı, hepsi test edildi.
Detaylı liste için: `references/youtube-ekonomi-kanallari.md`

### Veri Toplama (API'siz)
- **RSS Feed:** `https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}`
- **Transcript:** `YouTubeTranscriptApi().fetch(video_id, languages=['tr', 'en'])`
- **Channel ID Keşfi:** Browser console → `ytInitialData` JSON → `"channelId":"UC..."`

---

## 🎮 V4: Simülasyon (Planlanan)

### Araçlar
- `backtesting.py` — hafif Python kütüphanesi
- `yfinance` — Yahoo Finance veri çekme ✅ (kurulu, test edildi)
- `pandas` — veri işleme
- `pandas-ta` — teknik indikatörler (kurulum gerekli)

### Strateji Testleri
1. **DCF Skorlama:** Owner's earnings bazlı intrinsic value hesapla
   - Input: FCF, büyüme oranı, WACC
   - Backtest: Son 3 yıl verisiyle tutarlılık kontrolü
2. **Moat Skorlama Sistemi** — 5 faktör: marka, switching cost, ağ etkisi, maliyet, ölçek
3. **Makro Sinyal Rotasyonu** — faiz/enflasyon/büyüme bazlı sektör rotasyonu

### yfinance Test Sonuçları (27 Haz 2026)
- Altın (GC=F): $4,078.70
- USD/TRY: 46.55
- API: `yfinance.Ticker('GC=F').history(period='2d')`
