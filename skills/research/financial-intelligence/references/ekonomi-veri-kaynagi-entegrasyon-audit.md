# Ekonomi Zekası — Veri Kaynağı Entegrasyon Audit'i

**Tarih:** 18 Temmuz 2026
**Kapsam:** Tüm veri kaynaklarının Ekonomi Zekası bültenine entegrasyon durumu

## Kaynak Bazında Durum

| Kaynak | Job ID | Toplanıyor | Bültende Kullanılıyor | Model |
|--------|--------|:----------:|:---------------------:|-------|
| Bitcoin Arısı (@BitcoinArisi) | `9d515802f2b2` + `9f8302bc6a18` | ✅ no_agent (Python scrape) | ✅ (birikim-fikirleri.json) | LLM gerekmez |
| Coin Listesi (CoinGecko) | `67f6794f67f7` | ✅ no_agent | ✅ (makro panel) | LLM gerekmez |
| BIST Günlük Takip | `951b4536ee4f` | ✅ no_agent | ✅ (makro panel) | LLM gerekmez |
| BBC Business | — (bülten içi) | ✅ web_extract | ✅ | deepseek-v4-flash |
| Google News | — (bülten içi) | ✅ web_search | ✅ | deepseek-v4-flash |
| Makro Veri (yfinance) | — (bülten içi) | ✅ terminal | ✅ | deepseek-v4-flash |
| **YouTube Ekonomi Kanalları** | `e0ab298fccc8` | ✅ no_agent (transkript var) | ❌ **KULLANILMIYOR** | LLM gerekmez |
| **Para Dergisi** | `45e8c6b7d2af` | ✅ agent mode | ⚠️ **AYRI KANAL** (bültene entegre değil) | deepseek-v4-flash |

## Kritik Bulgular

### 1. YouTube Transcript Gap
YouTube tarama script'i (`youtube_tarama.py`) her sabah 07:00'de 5 kanalı tarıyor, Yatırım 101'in transkriptlerini `~/.hermes/data/youtube/transcripts/` dizinine JSON olarak kaydediyor. Ama bülten prompt'unda YouTube referansı **hiç yok**. Veriler toplanıp bekliyor.

**Yapılması gereken:** Bülten prompt'una "📺 YouTube'dan Öne Çıkanlar" bölümü eklenmeli.

### 2. Para Dergisi Ayrı Kanalda
Para Dergisi job'ı ayrı bir Telegram kanalına (origin) gönderiyor, Ekonomi Zekası bülten kanalına değil. Ayrıca agent mode ile LLM harcıyor. No_agent'a çekilirse scraping + başlık toplama yapabilir, LLM sadece önemli bulunanları işleyebilir.

### 3. DeepSeek Flash Free (opencode-zen) Çalışmıyor
18 Tem 2026 itibarıyla deepseek-v4-flash-free **403 Forbidden** (error code 1010). Model watchdog 33 kez FAILED raporlamış, protected olduğu için değiştirilmemiş.

**Etkilenen cron job'lar:**
| Job | ID |
|-----|----|
| Vanitas 8-Boyutlu Rüya | `f9ddbe495a13` |
| Skool Daily Check | `50002951d6bc` |
| Skool Community İstihbaratı | `40448623b352` |
| LinkedIn Kuyruk Besle | `45a6f33e0d02` |

**Çözüm:** Elle `custom:opencode-go` (deepseek-v4-flash) veya NVIDIA modellerine çekilmeli.

### 4. Bitcoin Arısı — İki Job'lu Yapı
- **Bitcoin Arısı Tarama** (09:00): Tüm sayfayı tara, birikim fikirlerini kategorize et, rapor yaz
- **Bitcoin Arısı Yeni Mesaj Kontrol** (12:00): State tut, sadece yeni mesaj varsa bildir (yoksa sessiz)

İkisi de no_agent (Python script), LLM harcamaz. "Yeni Mesaj Kontrol" daha sıklaştırılabilir, "Tarama" gereksiz olabilir.

## Provider Seçimi (18 Tem 2026)

| Provider | Durum | Kullanım |
|----------|-------|----------|
| `custom:opencode-go` (deepseek-v4-flash, port 19998) | ✅ En güvenilir | Ana sohbet + Ekonomi Zekası bülteni |
| `opencode-zen` (deepseek-v4-flash-free) | ❌ 403 Forbidden | Kullanma |
| `NVIDIA` (build.nvidia.com) | ⚠️ Worker overload riski | GLM 5.2 (%100 stabil), M3 (%80 stabil) |
