# Polymarket Market Landscape (Haziran 2026)

Şu anki dominant kategoriler ve strateji önceliklendirme.

## Top Kategoriler (Hacim Sırası)

| Hacim (milyon $) | Kategori | Örnek Marketler | Haber-Driven? |
|---|---|---|---|
| ~$82M | Spor (FIFA WC) | 2026 Dünya Kupası Şampiyonu | ⚠️ Uzun vadeli, complex |
| ~$31M | UK Siyaset | Starmer out by..., UK election | ✅ **PRİMER** |
| ~$22M | Pop Kültür | GTA VI markets | 🚫 MEME — filtrele |
| ~$6.5M | Teknoloji | OpenAI hardware launch, GPT-5 | ✅ **PRİMER** |
| ~$5M | Kripto/Politika | Trump crypto tax, Kraken IPO | ✅ **PRİMER** |
| ~$2.6M | Ukrayna/Jeopolitik | Russia capture, Ukraine election | ✅ **PRİMER** |
| ~$2M | Fransa Siyaset | Macron out | ✅ Orta |
| ~$1.5M | Kripto IPO | Kraken IPO dilimleri | ✅ Orta |

## Filtrelenmesi Gerekenler

- **GTA VI marketleri:** "X before GTA VI" şablonundaki tüm marketler meme'dir. Gerçek haber-driven fiyat hareketi yok.
- **Jesus, Rihanna, Playboi Carti vb.:** Kişisel inanç/eğlence marketleri. Rasyonel haber analizi yapılamaz.
- **Uzun vadeli spor futures:** FIFA WC 2026, NHL, NBA. Analiz için çok fazla değişken.

## Strateji Önceliklendirme

1. **UK Siyaset (Starmer):** $31M hacim, güçlü RSS beslemesi (BBC, Guardian, Telegraph), haber-fiyat bağlantısı direkt
2. **Kripto/Politika (Trump crypto tax, Kraken IPO):** $5M-$1.5M, CoinDesk/Telegraph/Blockworks RSS + SearXNG
3. **Ukrayna/Jeopolitik:** $2.6M, BBC World + Al Jazeera RSS, güçlü SearXNG sonuçları
4. **Macron/Fransa:** $2M, sınırlı RSS ama SearXNG ile tamamlanır

## Tarama Stratejisi

`collect_data.py` şu şekilde market toplar:
1. Gamma API'den her tag (crypto, politics, tech, world, finance) için event'leri çek
2. Her event'in altındaki marketleri parse et
3. MEME_KEYWORDS listesine takılanları atla
4. Volume < $100K olanları atla
5. Expired marketleri atla
6. Deduplicate (soru bazında)
7. Volume'a göre sırala, top 15'i al

Meme filter keywords: `['gta vi', 'gta 6', 'jesus', 'rihanna', 'playboi', 'carti', ' return before', 'release before', 'hit $1m before', '$1m before']`
