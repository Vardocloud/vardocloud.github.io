# Bardo Psikoloji — Brand Paleti & Tasarım Sistemi

Instagram karusel ve sosyal medya görselleri için tutarlı marka kimliği.

## Renk Paleti

### Koyu Tema (Slayt 1, 3, 5, 6)
| Kullanım | Renk | HEX | CSS |
|----------|------|-----|-----|
| Arka plan (koyu) | Lacivert | `#1a1a2e` | `background: linear-gradient(160deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)` |
| Arka plan (mavi) | Koyu mavi | `#16213e` | |
| Vurgu | Lacivert ton | `#0f3460` | |
| Ana metin | Krem | `#f5e6d3` | `color: #f5e6d3` |
| İkincil metin | Soluk krem | `rgba(245,230,211,0.7)` | |
| Vurgu metin | Altın | `#c9a86c` | `color: #c9a86c` |
| Kart arka plan | Yarı saydam | `rgba(255,255,255,0.05)` | `background: rgba(255,255,255,0.06)` |
| Kart border | Soluk | `rgba(255,255,255,0.1)` | |

### Açık Tema (Slayt 2, 4)
| Kullanım | Renk | HEX | CSS |
|----------|------|-----|-----|
| Arka plan | Krem | `#faf7f2` | `background: #faf7f2` |
| Kart arka plan | Beyaz | `#ffffff` | `background: white` |
| Highlight kutusu | Krem | `#f5ede0` → `#ede3d3` | `background: linear-gradient(135deg, #f5ede0 0%, #ede3d3 100%)` |
| Highlight border | Altın | `#c9a86c` | `border-left: 5px solid #c9a86c` |
| Ana başlık | Lacivert | `#1a1a2e` | `color: #1a1a2e` |
| Gövde metin | Koyu gri | `#4a4a5a` | `color: #4a4a5a` |
| İkincil metin | Gri | `#5a5a6a` | `color: #5a5a6a` |
| Araştırma tag'ı | Lacivert | `#1a1a2e` | `background: #1a1a2e; color: #f5e6d3` |

### İkon Arka Planları (3 Sütun Slaytı)
| Sütun | HEX |
|-------|-----|
| Empati | `rgba(201,168,108,0.2)` |
| Koşulsuz Kabul | `rgba(100,180,180,0.2)` |
| Otantiklik | `rgba(200,140,150,0.2)` |

## Fontlar

| Kullanım | Font | Stil | Boyut |
|----------|------|------|-------|
| Kapak başlık | Playfair Display | Bold 600 | 76px |
| Slayt başlık | Playfair Display | Bold 600 | 46-52px |
| Kapak alıntı | Playfair Display | Italic 400 | 24px |
| Kapanış alıntı | Playfair Display | Italic 600 | 42px |
| Gövde metin | Inter | Regular 400 | 16-22px |
| Sayı/etiket | Inter | Medium 500 | 14px |
| CTA buton | Inter | SemiBold 600 | 20px |
| Brand/metin alt | Inter | Light 300 | 14-15px |

Boyutlar 1080×1350px karusel slayt içindir.

## Slayt Yapısı

```
+------------------------------------------+
|  (üst padding: 80-90px)                  |
|  ✦ NN  (slayt numarası, 14px, uppercase) |
|                                          |
|  Başlık (Playfair Display, 46px)         |
|                                          |
|  [içerik]                                |
|                                          |
|  (alt padding: 80-90px)                  |
+------------------------------------------+
                                         1080px
```

Her slayt:
- `width: 1080px; height: 1350px` (Instagram 4:5)
- `border-radius: 40px; overflow: hidden`
- `padding: 80-90px` (iç kenar boşluğu)
- Koyu/açık arka plan dönüşümlü: Slayt 1(koyu) → 2(açık) → 3(koyu) → 4(açık) → 5(koyu) → 6(koyu)

## Karusel Slayt Sırası (Standart 6 Slayt)

| # | Tema | Arka Plan | İçerik Türü |
|---|------|-----------|-------------|
| 1 | Kapak (başlık + alıntı + brand) | Koyu | Merkezi, büyük başlık |
| 2 | Tanım / Kavram | Açık | Highlight kutusu + araştırma tag'ı |
| 3 | 3 Sütun / Liste | Koyu | İkon + başlık + açıklama |
| 4 | Veri / Araştırma | Açık | Numaralı kartlar |
| 5 | İpuçları / Öneriler | Koyu | İkonlu satırlar |
| 6 | Kapanış + CTA | Koyu | Alıntı + buton + brand |
