# ZenMux Pricing Araştırması — 16 Haz 2026

## Session Özeti
Edel, ZenMux'a kaydolup benim (Vanitas) arka planda kullanması için bir plan almak istedi. Subscription (Builder Plan) mı yoksa PAYG mı daha iyi diye sordu.

## Kritik Hata
İlk araştırmada subscription planını **atladım** — sadece Webrazzi haberini ve ana sayfayı taradım. Oysa:
1. ZenMux'ın subscription planı var: Builder Plan (Free/Pro/Max/Ultra)
2. Subscription ve PAYG ayrı API key sistemlerine sahip
3. Subscription'da Flow adlı bir composite billing unit var (1 Flow ≈ $0.03283)
4. "Pay $20 Get $30" promosu **PAYG'e** ait, subscription'da değil

## Doğru Araştırma Sırası
1. Ana sayfa (zenmux.ai) → genel bilgi, promosyonlar
2. Pricing sayfası (zenmux.ai/pricing) → plan karşılaştırması, ikisini de gör
3. Subscription detay (zenmux.ai/pricing/subscription) → Flow sistemi, plan limitleri
4. Dokümantasyon pricing guide (docs.zenmux.ai) → model bazlı fiyatlandırma, billing
5. Models sayfası (zenmux.ai/models) → model bazlı $/M token fiyatları
6. Login sonrası panel → gerçek kullanıcı deneyimi

## Subscription vs PAYG
| Özellik | Subscription (Pro $20) | PAYG ($20 top-up) |
|---------|----------------------|-------------------|
| API Key | Ayrı Subscription key | Ayrı PAYG key |
| Rate Limit | 10-15 RPM | Sınırsız |
| Concurrency | Haftalık kotalı | Sınırsız |
| Fiyat | $20/ay sabit | $20 → $30 kredi (promo) |
| Birim | Flow (1 Flow ≈ $0.03283) | 1 kredi = $1 USD |
| Kullanım | Kişisel gelişim, vibe coding | Production, ticari |
| Bonus | 1.5x değer çarpanı | Pay $20 Get $30 + %25 holiday |

## Alınan Ders
- Fiyat/plan araştırmasında **en az 5 farklı sayfa tara** (pricing, docs, models, calculator, panel)
- Bloglara/haber sitelerine güvenme — sadece resmi site
- Hesap makinesi/calculator varsa bul, o model bazlı gerçek maliyeti gösterir
- "Yok" deme, "bulamadım" de
