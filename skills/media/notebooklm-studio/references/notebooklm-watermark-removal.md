# NotebookLM Watermark Kaldırma — Değerlendirme

## Kısa Cevap: Uğraşmaya Değmez

NotebookLM slide deck PDF'lerinde watermark sağ alt köşede bulunur. Bunu programatik olarak kaldırmak için denenmiş yöntemlerin hepsi bir şekilde sorunludur.

## ❌ Denenmiş ve Sorunlu Yöntemler

| Yöntem | Deneme Tarihi | Sonuç |
|--------|---------------|-------|
| **Crop** (alt 40px kesmek) | 10 Tem 2026 | Görsel kompozisyonu bozuldu, Edel "resmi bozuyor" dedi |
| **OpenCV inpainting** (INPAINT_NS, radius 3-11) | 10 Tem 2026 | Küçük watermark'larda iyi, büyük alanlarda bulanıklık. Tam temizlenmedi |
| **Clone stamp** (üstteki bölgeyi kopyala + feathering) | 10 Tem 2026 | Source bölgede de watermark/sayfa numarası varsa kopyalanıyor |
| **Seamless cloning** (OpenCV seamlessClone) | 10 Tem 2026 | Source bölgedeki görsel içeriğini watermark bölgesine taşıdı |
| **Column-by-column PDF sampling** | 10 Tem 2026 | En iyi sonuç veren yöntem ama ince çizgili (stripe) artifact bırakıyor |

## 🔬 Analiz

Watermark'ı tamamen temizlemeyi başaran tek yöntem **column-by-column sampling** oldu (0 koyu piksel kaldı) ama görselde "çizgi çizgi" artifact oluşturdu. Bunun sebebi her sütunun renginin ayrı ölçülüp ayrı uygulanması — gradient geçişlerinde sütunlar arası renk farkı ince dikey çizgiler olarak görünüyor.

## Öneri

Watermark'ı kaldırmaya çalışma. NotebookLM'in kendi branding'i olarak kabul et. Instagram karusellerinde watermark zaten küçük bir alanda ve kullanıcılar tarafından fark edilmez. Watermark kaldırmak için harcanan zaman, yeni bir slide deck oluşturmaktan daha fazladır.
