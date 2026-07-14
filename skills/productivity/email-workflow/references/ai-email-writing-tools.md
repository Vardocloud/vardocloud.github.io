# AI Email Writing Tools — Edel İçin Referans

## Ne Zaman Kullanılır
- Edel profesyonel/akademik bir mail istediğinde (referans mektubu talebi, üniversiteye başvuru sorusu, resmi yazışma)
- Vanitas'ın doğrudan yazdığı taslaklar Edel tarafından "robotik" veya "iyi değilsin" olarak değerlendirildiğinde
- Mailin doğal, insansı, samimi bir dilde olması gerektiğinde

## Seçenek 1: Mailmeteor AI Email Writer ⭐ (ÖNERİLEN)
- **URL:** https://mailmeteor.com/tools/ai-email-writer
- **Fiyat:** %100 ücretsiz, kayıt gerekmez
- **Dil desteği:** Çoğu büyük dil (Türkçe dahil)
- **Özellikler:**
  - Prompt yaz → AI maili yazsın
  - Ton ayarı (formal/profesyonel/dostça/kısa)
  - "Write an email to a professor asking for a recommendation letter" gibi hazır senaryolar
  - Chrome eklentisi Gmail içinde çalışır (7 gün ücretsiz deneme)
- **Kullanım:** Prompt'u İngilizce yaz, Türkçe mail iste. Örn: "Write a professional email in Turkish to a professor requesting a recommendation letter for a master's program application"

## Seçenek 2: DraftEmail
- **URL:** https://www.draftemail.com/
- **Fiyat:** Günde 5 ücretsiz email
- **Dil desteği:** 100+ dil (Türkçe dahil)
- **Özellikler:**
  - Sesle yazma (50+ dilde konuş, mail olsun)
  - 500+ profesyonel şablon
  - Chrome eklentisi (Gmail/Outlook)
  - SOC 2 uyumlu
- **Kullanım:** "Think in Turkish, email in Turkish" — Türkçe düşünüp Türkçe mail yazdırmak için ideal

## Seçenek 3: AIxploria E-mail Kategorisi
- **URL:** https://www.aixploria.com/en/category/e-mail-en/
- **Kapsam:** 61 araç listelenmiş
- **Not:** Çoğu email marketing aracı (Klaviyo, MailerLite, GetResponse) — Edel'in kullanımına uygun değil.
- Aranacak tool tipi: "AI email writer" / "email assistant" / "AI writing assistant"

## Seçenek 4: HubSpot Free AI Email Writer
- **URL:** https://www.aixploria.com/en/generateur-e-mails-gratuit-hubspot-ia/
- **Fiyat:** Ücretsiz
- **Özellikler:** Prospektif email şablonları, HubSpot entegrasyonu

## Kullanım Akışı (Vanitas İçin)
1. Edel "şu hocaya mail yaz" dediğinde → önce bu listedeki araçları dene
2. **⚠️ WARP kontrolü:** Eğer ALL_PROXY tanımlıysa (`socks5://127.0.0.1:1080`), WARP bazı sitelerin JS/API çağrılarını engelleyebilir. Önce `ALL_PROXY=""` ile dene veya WARP proxy'siz Chrome başlat (bkz: warp-proxy skill)
3. Tool'un web sayfasını aç (browser_navigate)
4. Prompt'u yaz
5. Submit disabled kaldıysa → browser_console ile JS native value setter + input/change event dispatch dene (React state'i günceller, butonu aktifleştirir)
6. Submit çalışmazsa → browser_console ile `document.querySelector('button.submit-btn').click()` dene
7. Çıktıyı al → Edel'e Telegram'da göster
8. Onay al → varsa Gmail API ile gönder

## Mailmeteor — Headless Chrome'da Çalıştırma (JS Hack)

Mailmeteor'un submit butonu React state'e bağlıdır — `browser_type` textarea'yı doldursa bile React state'i güncellenmeyebilir ve buton disabled kalır.

**Çözüm (browser_console ile):**
```javascript
// 1. Native value setter ile React state'ini güncelle
const input = document.querySelector('textarea');
const nativeSetter = Object.getOwnPropertyDescriptor(
  window.HTMLTextAreaElement.prototype, 'value'
).set;
nativeSetter.call(input, 'Your prompt here...');
input.dispatchEvent(new Event('input', { bubbles: true }));
input.dispatchEvent(new Event('change', { bubbles: true }));

// 2. Buton aktif oldu mu kontrol et
document.querySelector('button.submit-btn').disabled; // false olmalı

// 3. Butona tıkla
document.querySelector('button.submit-btn').click();
```

**Submit sonrası sonucu oku:**
```javascript
document.querySelectorAll('textarea')[1].value // result textarea
```

## Sınırlamalar
- Mailmeteor web arayüzü: prompt yaz → generate → copy-paste yapılır, direkt gönderme yok
- DraftEmail: günde 5 email limiti, kayıt gerekiyor
- Bu araçlar İngilizce prompt'lar için optimize — Türkçe prompt'ta kalite düşebilir
- En iyi sonuç: Prompt'u İngilizce yaz, "in Turkish" ekle
- **⚠️ Mailmeteor headless Chrome'da düzgün çalışmayabilir:** client-side JS ile API call yapıyor. Bot koruması veya CORS nedeniyle submit butonu disabled kalabilir. Yukarıdaki JS hack'ini dene, olmazsa Fallback'e geç.

## Fallback: Vanitas + AI Model (Tüm Web Yöntemleri Başarısız Olursa)

Web araçlarının hiçbiri çalışmazsa (submit disabled, JS hatası, bot koruması), Vanitas kendi yetenekleriyle maili yazar. **Ama direkt "çalışmıyor" deme** — önce aşağıdaki sırayla alternatifleri dene:

### Deneme Sırası (Pes Etmeden Önce)
1. **WARP kapat:** `ALL_PROXY=""` ile sayfayı yeniden yükle + işlemi dene
2. **JS native hack:** browser_console ile React state'ini güncelle (yukarıdaki JS kodu)
3. **Programmatic submit:** `document.querySelector('button.submit-btn').click()`
4. **API izle:** fetch interceptor ile endpoint bul, curl ile dene
5. **Farklı araç dene:** Mailmeteor çalışmazsa DraftEmail'e geç
6. **Ancak TÜMÜ başarısız olursa → Fallback**

### Fallback Adımları
1. Web aracı dene (yukarıdaki 5 adımı sırayla uygula)
2. Hâlâ çalışmazsa → Vanitas kendi yetenekleriyle yaz (doğal dilde, önceki hatalardan ders alarak)

### Fallback Prompt Stratejisi (2026-06-13 Dersi)
"Mail yazmada iyi değilsin" düzeltmesinden sonra öğrenilenler:
- Çok kısa ve öz yaz: gereksiz sıfatlar, zarflar, akademik jargon kullanma
- Samimi ama saygılı ton: "Merhaba X Hocam" ile başla, "saygılar" ile bitir
- Somut bilgileri liste halinde değil, cümle içinde ver
- Hocayı hatırlat: ders adı + dönem + varsa proje detayı
- Deadline'ı net belirt: "18 Eylül 2026"
- CV/transkript teklif et: "memnuniyetle gönderirim"
- Zaman planı ver: "Eylül başında tüm belgeleri ileteceğim"
- **Kesinlikle şunları kullanma:** "başvurmayı değerlendiriyorum", "Sayın Yetkili", "Saygılarımla", numaralı listeler, uzun giriş cümleleri
