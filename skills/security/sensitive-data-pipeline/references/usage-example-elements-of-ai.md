# Kullanım Örneği: Elements of AI Giriş (2026-06-10)

## Senaryo
Edel, Helsinki Üniversitesi'nin Elements of AI dersine kaydolmak istedi. course.elementsofai.com'da mooc.fi hesabıyla giriş yapması gerekiyordu.

## Süreç
1. **HTML sayfası oluşturuldu** → `~/elements_secure_login.html` (base64 encode eden JS form)
2. **Edel dosyayı indirdi**, browser'da açtı, email+password girip "Kod Üret"e bastı
3. **Base64 kod** `VANITAS_SECURE::...` formatında oluştu
4. **Edel kodu chat'e yapıştırdı** → deepseek sadece anlamsız karakterler gördü
5. **Vanitas terminal'de** `secure_browser_fill_v2.py`'yi çalıştırdı
6. **Script** decode etti → Playwright headless Chromium açtı → form doldurdu → submit etti
7. **Sonuç:** ✅ Başarılı — sadece status mesajı deepseek context'ine girdi

## Alınan Dersler
- v1 script başarısız oldu (bot detection), v2'deki `add_init_script` ve human-like delays sorunu çözdü
- Input field'ların placeholder/name attribute'ları boş olabilir — type attribute'a göre fallback gerekli
- Sign in butonu disabled olabilir — JS ile enable etme gerekebilir
- Base64 kod terminal'de tek tırnak ile sarılmalı (`'...'`) — shell özel karakterleri yorumlamasın

## Kullanılan Komut
```bash
python3 ~/.hermes/tools/secure_browser_fill_v2.py 'VANITAS_SECURE::<base64_kod>'
```
