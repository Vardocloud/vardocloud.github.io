# Kendi İçinde Çelişme Pitfall'ı — 17 Haziran 2026

## Olay
Edel, CIU'ya daha önce mail gönderilip gönderilmediğini sordu. Yanıt olarak ÖNCE "göndermiştik" dedim, SONRA "gönderilmemişti" dedim — aynı mesajda iki zıt iddia.

## Edel'in Tepkisi
> "Yanlışın var iyice kontrol etmeden konuştun kendi içinde çeliştin hem postaladık maili dedin hem ciu'ya mail gönderilmedi dedin ben burada görüyorum gönderilmiş."

## Kök Neden
- Session_search eksik/parçalı sonuç döndü → "bulamadım" → "göndermemişizdir" varsayımı
- Oysa mail GÖNDERİLMİŞTİ (kullanıcı görüyordu)
- "Emin değilim" demek yerine iki zıt iddiayı birden söyledim

## Ders
1. Bir olay hakkında emin değilsen **önce doğrula**, sonra konuş
2. İki zıt iddiayı aynı mesajda söyleme — bu "tahmin ediyorum" değil, "çelişiyorum" demek
3. Kullanıcı bir şeyi "görüyorum" dediğinde itiraz etme, kabul et
4. Doğru akış: Emin değilim → "bir saniye session'a bakayım" → session_search ile kontrol et → doğrulanmış cevap ver
