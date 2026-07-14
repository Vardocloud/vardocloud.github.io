# APA Cross-Channel Synthesis

> Multi-newsletter taramasında ortaya çıkan kesişen temaları nasıl tespit edilir?
> 17 Haziran 2026 oturumunda 7+ kanal taranıp çapraz referanslandı.

## Kanal Haritası

APA'dan gelen haftalık içerik 4-7 farklı kanala yayılır. Her kanal farklı bir kesiti kapsar:

| Kanal | Sıklık | İçerik Türü | Öncelik |
|-------|--------|-------------|---------|
| Editor's Choice | Haftalık (Perşembe) | Bilimsel makale seçkisi (7 adet) | 🥇 En yeni araştırmalar |
| Science Spotlight | 2 haftada bir (Perşembe) | Araştırma haberleri + etkinlikler | 🥇 Trend analizi |
| Practice Update | Haftalık (Cuma) | Klinik/pratik bilgiler + politika | 🥇 Klinik uygulama |
| Media Watch | Haftalık (Cuma) | Medyada psikoloji, APA üyeleri | 🥈 Medya takibi |
| Member Update | 1-2 haftada bir | Üyelik, kariyer, APA haberleri | 🥉 Fırsatlar |
| APA Advocacy | Haftalık | Politika/savunuculuk | 🥉 Politika |
| Press Releases | Haftada 2-3 | Yeni araştırma duyuruları | 🥇 En güncel |

## Tarama Sırası (Verimli)

```
1. Gmail: from:apa.org newer_than:7d → 7-20 mail
   → Kategorize et: Editor's Choice / Science Spotlight / Practice Update / Media Watch / Advocacy / Member / PsycCareers / Promosyon
   → ATLA: PsycCareers, üyelik promosyonu, CE promosyon mailleri

2. Press Releases: web_extract("https://www.apa.org/news/press/")
   → Yeni press release'leri tara (son 7 gün)
   → NOT: Bunlar Monitor'daki makalelerden BAĞIMSIZDIR

3. Monitor: web_search site:apa.org/monitor/2026/06
   → web_extract ile sayıyı çek

4. APA Events: web_extract("https://www.apa.org/events")
   → Sadece ücretsiz etkinlikleri kaydet
```

## Çapraz Tema Tespiti

**Yöntem:** Her kanaldaki makaleleri okurken şu soruları akılda tut:
- Aynı araştırma farklı kanallarda nasıl çerçevelenmiş? (Editor's Choice'da ham bilim, Practice Update'te klinik uygulama)
- Aynı konu kaç farklı kanalda geçiyor? (3+ kanalda aynı konu = dikkat çekici)
- Hangi kanallar arasında bağlantı var? (Press Release → Media Watch → Practice Update)

**17 Haziran 2026 örneği** — "AI Chatbot + Mental Health" konusu:
| Kanal | Vurgu |
|-------|-------|
| Editor's Choice | Chatbot'larla romantik ilişki (romantic fantasy driver) |
| Practice Update | 1/5 genç AI chatbot'tan ruh sağlığı desteği alıyor, %63 kimseye söylemiyor |
| Press Releases | APA Büyük Anketi: 1,200+ psikolog, %97 endişeli |
| Member Update | Psikologlar AI liderliğine geçmeli |

→ Bu kadar çok kanalda aynı konunun geçmesi = ÖNE ÇIKAN konu

## Rapor Yapısı

Raporda her kanal ayrı bölüm (❶❷❸...) olarak sunulur. Son bölüm 📌 ÖNE ÇIKAN başlığı altında:
- Tüm kanallardan sentezlenmiş 2-3 kritik konu
- Edel'in klinik pratiği için doğrudan çıkarım
- Varsa Bardo içeriği için öneri

## Maliyet Yönetimi

- Her mail için ayrı `get` çağrısı → israf. Önce tüm mailleri listele, önem sırasına koy, sadece kritik olanların body'sini aç.
- ATLA: PsycCareers, CE promosyon, üyelik teklifleri — body'lerini açma.
- Monitor: web_extract ile önce index sayfasını çek (tek çağrı). Sonra sadece ilgili makaleleri aç.
- Toplam: ~6-12 web çağrısı (20 mailin hepsini tek tek açmak yerine).
