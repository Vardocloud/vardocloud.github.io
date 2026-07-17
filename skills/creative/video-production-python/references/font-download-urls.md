# Google Fonts — Doğrudan İndirme URL'leri

## CSS API ile Bulma

```bash
# Bold (700) font URL'sini bul
curl -s "https://fonts.googleapis.com/css2?family=Font+Name:wght@700&display=swap" | grep -oP 'url\(\K[^)]+' | head -1
```

## Çalışan Fontlar

| Font | CSS API Sorgusu | Durum |
|------|----------------|-------|
| Cormorant Garamond Bold | `https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@700` | ✅ |
| Montserrat Bold | `https://fonts.googleapis.com/css2?family=Montserrat:wght@700` | ✅ |
| Montserrat SemiBold | `https://fonts.googleapis.com/css2?family=Montserrat:wght@600` | ✅ |
| Playfair Display Bold | `https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700` | ❌ (descender'lar eksik) |

## İndirme Komutu

```bash
curl -sL "<URL>" -o ~/.fonts/FontName-Bold.ttf
python3 -c "from PIL import ImageFont; ImageFont.truetype('~/.fonts/FontName-Bold.ttf', 48)"
```

## Alternatif: Variable Font

Variable font indirilebilir ama PIL'de `set_variation_by_axes([700])` ile weight ayarlanmalı.
MoviePy TextClip variable font weight'ini desteklemez — statik TTF gerekli.
