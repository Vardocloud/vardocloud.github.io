# APA Ücretli/Üyelik Kaynak İşleme (10 Temmuz 2026)

## Arka Plan

APA Monitor makaleleri (monitor.apa.org) APA üyeliği gerektirir. Cron job'ları web_extract ile sadece özet alır. Edel uyardı: üyeliği varken özetle geçmek yanlış.

## APA Login Durumu

- **Email:** isimgorulsunn@gmail.com
- **Hesap türü:** APA üyesi
- **Login sayfası:** sso.apa.org
- **2 yol:** direkt email+password VEYA "Log in with Google"
- **10 Temmuz 2026 itibarıyla:** verilen şifre ile login başarısız (hem direkt APA hem Google)
- **Şifre kaydı:** `/home/ubuntu/.hermes/apa_email.txt` (600) ve `/home/ubuntu/.hermes/apa_password.txt` (600) — BWS'e kayıtlı değil

## Prosedür

1. APA Monitor makalesi görünce → ÖNCE login dene
2. Login bilgilerini bul:
   - BWS'de `APA_EMAIL` / `APA_PASSWORD` secret'ları
   - `/home/ubuntu/.hermes/apa_email.txt` ve `apa_password.txt`
   - Environment variable
3. Browser APA login sayfasını aç, dene:
   - `https://sso.apa.org/apasso/idm/apalogin?ERIGHTS_TARGET=<makale-url>`
   - Email + şifre ile dene
   - Olmazsa "Log in with Google" ile dene
4. Login başarılı olursa → cookie ile sayfayı tam metin çek
5. Login başarısız olursa → Edel'e bildir, sessizce özetleme

## Tuzak

- Google login popup değil, aynı tab'da redirect ile çalışır
- Şifrede özel karakterler ($, @, #, ^) varsa browser_type düzgün giremeyebilir — JS ile kontrol et
- APA girişi başarılı olursa oturum cookie'si browser kapansa da çalışmaz — her seferinde yeni login gerekebilir
