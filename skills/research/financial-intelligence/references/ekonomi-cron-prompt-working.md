# 📈 Ekonomi Zekası — Çalışan Cron Prompt'u

**Oluşturma:** 27 Haziran 2026
**Job ID:** `3acdcd93e3b7`
**Zamanlama:** `0 8,18 * * *` (günde 2 kere — sabah 08:00, akşam 18:00)
**Skills:** financial-intelligence, sohbet
**Model:** deepseek-v4-flash-free @ opencode-zen
**Toolsets:** web, terminal, file, search
**Deliver:** origin (mevcut chat'e)

---

## Prompt Metni (Tam)

```
# 📈 Ekonomi Zekası — Yatırım İstihbaratı Bülteni

financial-intelligence ve sohbet skill'lerini yükle.

Şu an saat SABAH 08:00 ise → "🌅 SABAH BÜLTENİ — Piyasa Öncesi"
Şu an saat AKŞAM 18:00 ise → "🌆 AKŞAM BÜLTENİ — Gün Sonu"

## 1️⃣ VERİ TOPLA

### a) BBC Business — web_extract ile
web_extract(["https://www.bbc.com/news/business"])

### b) Google News — web_search ile
- "BIST 100 endeksi bugün"
- "Türkiye ekonomisi haberleri"
- "altın gümüş bakır fiyatları"
- "dolar euro kuru"
- (sabah) "Asya piyasaları" + "ABD vadeli işlemler"
- (akşam) "BIST kapanış" + "emtia fiyatları"

### c) Emtia Fiyatları
web_search("ons altın gram altın gümüş bakır fiyatı bugün")

### d) 🐝 Bitcoin Arısı — Kripto Drop & Birikim Fırsatları
- Dosyayı kontrol et: ~/.hermes/data/bitcoin-arisi/birikim-fikirleri.json
- Son 24 saatte yeni birikim fikri varsa bültende paylaş
- Kripto drop fırsatları: düşüşte alım, ön satış (presale), ucuz coin analizleri
- Kategoriler: 📉 DROP fırsatı / 💎 UCUZ yatırım / 🎯 Hedef fiyat
- Not: Bu veri @BitcoinArisi kanalından toplanır, günde 1 kere (sabah 09:00) güncellenir

## 2️⃣ ANALİZ ET (Buffett Gözlüğü)

Her haber/bilgi için:
- Kategorize: Makro / Sektör / Emtia / BIST / Forex
- 5N1K özet (1-2 cümle)
- Buffett filtre: İşletme → Finansal → Değer → Uzun Vade
- Etiket: 🟢 FIRSAT / 🔴 RİSK / ⚪ NÖTR
- Makro bağlantı: faiz/enflasyon/büyüme ile ilişki

## 3️⃣ RAPORLA

Format:
📍 MANŞET → 📰 HABERLER (max 4-5) → 📊 MAKRO PANEL
→ 🎯 ÖNE ÇIKAN FIRSAT/RİSK

Her haber: 📈 [SEKTÖR] Başlık | 📋 5N1K | 🎯 Gözlük | ⚡ Etiket | 🔮 Beklenti

⚠️ Yatırım tavsiyesi değildir.
```

---

## Çalışma Prensibi

### Sabah Bülteni (08:00) — Piyasa Öncesi
- Gece gelişmeleri (Asya kapanışı, ABD vadeli)
- Günün makro takvimi
- Beklenti odaklı: "Bugün ne bekleniyor?"

### Akşam Bülteni (18:00) — Gün Sonu
- BIST kapanış (endeks, hacim)
- Emtia güncellemesi (altın, gümüş, bakır, petrol)
- Forex (USD/TRY, EUR/TRY)
- Günün özeti: "Bugün ne oldu?"

### Hata Yönetimi
- web_extract başarısız → diğer kaynaklarla devam
- web_search başarısız → kalan sorgularla devam
- Tüm kaynaklar başarısız → "Bugün dikkat çeken haber bulunamadı"
- Haftasonu/tatil → "Piyasalar kapalı" notu
- Asla boş veya hatalı bülten gönderme

---

## İlk Çalışma
**27 Haziran 2026 18:00'de** ilk akşam bülteni otomatik gönderilecek.
