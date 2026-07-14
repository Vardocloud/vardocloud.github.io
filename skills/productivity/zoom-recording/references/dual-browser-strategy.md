# Dual-Browser Strategy (2 Tem 2026)

CDP WebSocket timeout verdiğinde veya Zoom CSP'si kontrolü engellediğinde,
Hermes'in kendi `browser_*` araçları (port 9222) alternatif UI kontrolü sağlar.

## Problem

1. Custom Chrome (9333) ses kaydı için ZORUNLUDUR
2. CDP WebSocket bazen timeout verir (Zoom sayfası ağır yüklenir)
3. `browser_*` araçları (9222) Zoom CSP'sinden etkilenmez — JS çalıştırabilir
4. Ama browser_* (9222) ses KAYDETMEZ (PULSE_SINK yoktur)

## Çözüm: İki Chrome, Aynı Meeting

```
Custom Chrome (9333)  → zoom_rec.monitor → ffmpeg → SES KAYDI
Hermes browser_* (9222) → UI kontrolü (join, form, durum)
```

## Adım Adım

### 1. Önce Custom Chrome'da ses kaydı başlat
```bash
# Custom Chrome zaten çalışıyor (setup'ta başlatılmış)
# ffmpeg zaten zoom_rec.monitor'dan kayıt alıyor
```

### 2. Hermes browser_* ile Zoom join yap
```javascript
// browser_navigate → app.zoom.us/wc/join/MEETING_ID

// browser_console ile form doldur
var setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
var inp = document.getElementById('input-for-name');
setter.call(inp, 'Sudenaz');
inp.dispatchEvent(new Event('input', {bubbles: true}));
inp.dispatchEvent(new Event('change', {bubbles: true}));

// Join butonuna tıkla
document.querySelectorAll('button')[2].click();
```

### 3. Custom Chrome'da da join yap
```bash
# Custom Chrome'da yeni tab aç
curl -X PUT "localhost:9333/json/new?https://app.zoom.us/wc/join/MEETING_ID"
sleep 8

# CDP ile form doldur + join
python3 /tmp/custom_join2.py
```

### 4. Ses doğrulama
```bash
ffmpeg -t 3 -f pulse -i zoom_rec.monitor -af volumedetect -f null - 2>&1 | grep mean_volume
```

## Ne Zaman Kullanılır

- CDP WebSocket "Connection timed out" hatası verdiğinde
- Zoom CSP'si puppeteer evaluate'ı blokladığında
- İlk join denemesi başarısız olduğunda

## Önemli Kurallar

- İki Chrome da ayrı kullanıcılar olarak meeting'e katılır
- browser_* başarılı olsa bile Custom Chrome join yapmazsan ffmpeg SESSİZLİK kaydeder
- Chrome 9333 ölürse → restart + curl /json/new + rejoin
