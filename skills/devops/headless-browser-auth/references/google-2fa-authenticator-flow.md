# Google 2FA — Authenticator App Flow (Headless Browser)

## Ne Zaman Kullanılır

"Tap Yes on your phone or tablet" (push notification) headless Chrome'da **session'ı kalıcı yapmaz** — onay geçer gibi olur ama sayfa reload'da tekrar sign-in sayfasına döner. Çünkü Google, headless browser'ı güvenilmez cihaz olarak sınıflandırır ve cookie'leri kalıcı yapmaz.

**Google Authenticator kodu** bu durumda daha güvenilirdir: kod girildikten sonra Google'ın session'ı kalıcı yapma olasılığı daha yüksektir.

## Adım Adım Akış

### 1. Giriş bilgilerini gir
```
email → Next → password → Next
```

### 2. 2FA sayfasında "Try another way" tıkla
```
browser_click(ref=e4)  # "Try another way" butonu
```

### 3. "Get a verification code from the Google Authenticator app" seç
```
browser_click(ref=e11)  # Ref her sayfada değişir, snapshot'tan kontrol et
```
Bu seçenek listede genelde 3. sıradadır.

### 4. Kodu gir
```
"Enter code" textbox'ı → kodu yaz → "Next" (e8)
```

### 5. Kullanıcıdan kod alma
Authenticator kodu **30 saniyede bir yenilenir**. Şu akış izlenir:
- Hazır olduğunu bildir ("parmaklar tuşun üzerinde")
- Browser'da email → password → "Try another way" → "Authenticator" adımlarını önceden yap, **kullanıcı beklerken** kod giriş ekranında bekle
- Kullanıcı kodu söylediğinde hemen gir + Next'e bas
- Çok kısa sürede (2-3sn) yapılabilir — 30sn fazlasıyla yeterli

### 6. Sonuç kontrolü
Kod doğruysa → Gmail inbox açılır (veya otomatik yönlenir)
Kod yanlış/süresi dolduysa → "Wrong code" hatası, yeniden dene

## Selector'lar

Sayfa yeniden yüklendiğinde ref ID'ler sıfırlanır. HTML text bazlı selector kullan:

- "Try another way" → `document.querySelector('[role="button"]')` ile text match
- "Get a verification code from the Google Authenticator app" → link text match
- "Enter code" → `input[type="text"]` (genelde tek input)
- "Next" → `button[type="submit"]`

## 🚀 File-Watch Pattern — Asenkron Kod Girişi (3 Tem 2026)

30 saniyelik süre içinde tool call'lar arası gecikme yetişmeyebilir. Çözüm: **kullanıcı kodu bir dosyaya yazar, script dosyayı izleyip otomatik gönderir.**

### Nasıl Çalışır

```
Kullanıcı: echo 751966 > /tmp/gmail_code.txt
    ↓
Bir Python script'i (headless Playwright ile) `/tmp/gmail_code.txt` dosyasını izler
    ↓
Dosya oluşunca içindeki kodu okur, browser'daki "Enter code" input'una yazar, Next'e basar
    ↓
İşlem tamam
```

### Script Mimarisi

```python
# Özet mantık:
code_file = "/tmp/gmail_code.txt"
while time.time() - start < 120:
    if os.path.exists(code_file):
        with open(code_file) as f:
            code = f.read().strip()
        if re.match(r'^\d{6}$', code):
            os.remove(code_file)
            # Kodu browser'a gir ve Next'e bas
            await code_input.fill(code)
            await next_btn.click()
            break
    await asyncio.sleep(0.2)
```

### Gerçek Kullanım Akışı

1. **Hermes'in kendi browser'ını** (`browser_navigate`) kullan — Playwright'tan daha iyi çalışır
2. Email → password → 2FA → Try Another Way → Authenticator seç
3. Kod giriş ekranında kullanıcıya şunu söyle:
   ```
   echo <KOD> > /tmp/gmail_code.txt
   ```
4. Kullanıcı kodu dosyaya yazınca script otomatik okur ve gönderir

### ⚠️ ÖNEMLİ: Hermes Browser vs Playwright

| Özellik | Hermes `browser_navigate` | Playwright (headless) |
|---------|---------------------------|----------------------|
| Google bot detection | ✅ Email+password geçer | ❌ "Couldn't sign you in" |
| 2FA aşaması | ✅ 2FA sayfasına kadar gelir | ❌ Daha baştan bloklanır |
| Session persistence | ❌ Headless'te cookie kalıcı değil | ❌ Headless'te cookie kalıcı değil |
| Kod girişi | ✅ `browser_console` JS ile girilir | ✅ `page.fill()` ile girilir |

**Kural:** Google auth için ÖNCE Hermes browser'ı dene. Playwright ancak Hermes browser çalışmazsa (ör. form doldurma, özel URL) kullanılır.

### File-Watch'ın Avantajı

- Kullanıcı kodu yazıp diğer işine devam edebilir
- Script kodu alır almaz 0.2sn içinde gönderir — 30sn bol bol yeter
- Kod Telegram'da görünmez (terminal'den yazılır)
- `os.remove()` ile dosya temizlenir, ikinci kullanımda karışmaz

### Pitfall — Playwright Google Bot Detection

Google, Playwright'ı headless olarak tespit eder ve `/v3/signin/rejected` sayfasına yönlendirir:
```
Couldn't sign you in
This browser or app may not be secure.
```

**Çözüm:** Xvfb ile headed mode (headless DEĞİL) veya Hermes browser'ı kullan. Xvfb çözümü headless-browser-auth SKILL.md'deki "Headless Chrome gets rejected by Google" bölümünde detaylı anlatılır.

### Pitfall — Sayfa Timeout vs Kod Timeout

İki farklı timeout vardır:
- **Kod timeout:** 30sn (Authenticator kodu yenilenir)
- **Browser sayfa timeout:** Değişken (Google sign-in sayfası headless'ta dakikalar içinde boşalabilir)

**File-watch ile kod timeout'u sorun değil** (script 0.2sn'de gönderir). Ama browser sayfası boşalırsa (snapshot = `"(empty page)"`), script başarısız olur. Çözüm: script başlamadan önce browser'ı hazırla ve dosya-watch'ı browser açıkken başlat.

## 🚀 browser_console JavaScript Injection — En Hızlı Yöntem (3 Tem 2026)

File-watch ve browser_type yöntemlerinden **daha hızlı** bir alternatif: **`browser_console` ile tek tool call'da kod gir + Next'e bas.**

### Neden Daha Hızlı?

| Yöntem | Tool Call Sayısı | Sorun |
|--------|-----------------|-------|
| `browser_type` + `browser_click` | 2 | Ref ID'ler arada değişebilir (Unknown ref) |
| File-watch script | 10+ (tüm giriş) | Playwright Google bot detection'a takılır |
| **browser_console JS** 🏆 | **1** | DOM'dan güncel element bulunur, ref ID gerekmez |

### Kullanım Şekli

**Adım 1:** Hermes browser'ında Authenticator kod giriş ekranına gel (email → password → 2FA → Try Another Way → Authenticator)

**Adım 2:** Kullanıcı kodu söylesin

**Adım 3:** `browser_console` ile TEK expression'da kod gir + submit:

```javascript
(() => {
  const code = '751966'; // ← kullanıcının verdiği kod
  const input = document.querySelector('input[type="text"]');
  if (!input) return 'Input bulunamadı';
  // React state'i tetiklemek için native value setter gerekli
  const nativeSetter = Object.getOwnPropertyDescriptor(
    window.HTMLInputElement.prototype, 'value'
  ).set;
  nativeSetter.call(input, code);
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
  // Next butonunu bul ve tıkla
  const buttons = document.querySelectorAll('button');
  for (const btn of buttons) {
    if (btn.textContent.includes('Next')) {
      btn.click();
      return 'Kod girildi ve Next tıklandı: ' + code;
    }
  }
  return 'Next butonu bulunamadı';
})();
```

**Nasıl çalışır:**
- `browser_console` Hermes'te tek tool call'dur — arada sayfa state'i değişmez
- `querySelector` ile DOM'dan anlık element bulunur (ref ID'ye gerek yok)
- `Object.getOwnPropertyDescriptor(...)` — React/Google'ın synthetic event'lerini tetiklemek için native value setter gerekir. Sadece `.value = kod` yapmak React state'i güncellemez
- `input` + `change` event'leri dispatch edilir — Google'ın form validation'ı çalışsın
- Next butonu `textContent.includes('Next')` ile bulunur

### Firefox vs Chromium Konsol

`browser_console` altında `expression` parametresi JavaScript çalıştırır. Bu, tarayıcının DevTools konsolu gibidir — DOM'a tam erişim vardır. Çalıştığı tarayıcı motoru fark etmez.

### Avantajları

1. **Ref ID sorunu yok** — her seferinde DOM'dan güncel element bulunur
2. **Tek tool call** — sayfa state'i değişmez, race condition olmaz
3. **Milisaniyede çalışır** — kod expire olmadan çok önce gönderilir
4. **Hermes browser'ında çalışır** — Playwright bot detection sorunu yok

### Dezavantajları

1. JavaScript hatası durumunda hata ayıklamak zor (expression düz metin)
2. `nativeSetter` çağrısı başarısız olursa React state güncellenmez, kod girilmiş gibi görünür ama submit olmaz
3. Sayfa boşaldıysa (`"(empty page)"`) çalışmaz — önce baştan başlamak gerekir

### Hata Yönetimi

Expression bir string döndürür (başarı/başarısızlık mesajı). `browser_console` çıktısından kontrol edilebilir:
- `"Kod girildi ve Next tıklandı: 751966"` → ✅ başarılı
- `"Input bulunamadı"` → sayfa boş veya yanlış aşamada
- `"Next butonu bulunamadı"` → kod girildi ama buton bulunamadı (sayfa değişmiş olabilir)

## Önemli Notlar

- **30 saniye kuralı:** Kod süresi dolmadan önce hazır ol. Adımları önceden yapıp kod giriş ekranında bekle.
- **"Don't ask again on this device" checkbox'ı** varsayılan olarak işaretlidir. Headless browser'da işe yaramaz (cookie kalıcı değil), ama işaretli kalması sorun değil.
- **"Tap Yes" flow'u ile karıştırma:** "Tap Yes" phone push notification gönderir, sayı karşılaştırması yapar. Authenticator flow doğrudan kod girişidir, telefon bildirimi GEREKMEZ.
- **Başarısız olursa:** Kod yanlışsa (Wrong code) — kullanıcıdan Authenticator uygulamasını açıp yeni kodu beklemesini iste.
- **browser_console yöntemi öncelikli tercihtir** — file-watch ve browser_type yöntemlerinden daha hızlı ve güvenilirdir.

## 🚨 Pitfall: Browser Page Timeout During User Interaction

Kullanıcıdan kod beklerken Google sign-in sayfası **timeout yiyip boş sayfaya düşebilir** (snapshot = `"(empty page)"`). Bu headless browser'da daha sık olur çünkü page lifecycle farklı işler.

**Belirtiler:**
- Kod geldiğinde `browser_type` "Unknown ref" hatası verir (ref ID'ler sıfırlanmış)
- Snapshot boş sayfa döner
- Navigasyon sign-in sayfasına döner

**Çözüm — Adım Adım:**
1. Kullanıcıya "süresi doldu, yeni kod alır mısın?" de
2. Tüm akışı **baştan başlat**: `browser_navigate` → email → password → 2FA → Try Another Way → Authenticator
3. Kod giriş ekranına gelince kullanıcıya haber ver
4. **browser_console JS yöntemini kullan** (daha hızlı, tek tool call)
5. Kullanıcı yeni kodu söyler söylemez expression'ı çalıştır

**Speedrun taktiği:** Tüm adımları (~10 tool call) 15-20sn'de tamamlayabilirsin. Google Authenticator kodu 30sn geçerli, yani rahatça yetişir — ama sayfa timeout'u kod süresinden ÖNCE gelebilir, o yüzden hızlı ol.

**Don't be clever:** Sayfa boşaldıktan sonra eski ref'lerle kod girmeye çalışma — çalışmaz. Her zaman baştan başla.

## "Tap Yes" Compare Numbers Detayı

"Tap Yes on your phone or tablet" seçeneğinde:
- Browser'da bir `figure` elementi içinde `StaticText` olarak sayı görünür (ör: `"82"`, `"96"`, `"86"`)
- Kullanıcının telefonunda 3 farklı sayı gösterilir
- Kullanıcı browser'daki sayıyla eşleşeni telefonunda işaretler
- Bu sayı her oturumda rastgele değişir

**Önemli:** Bu yöntem headless browser'da onayı geçse bile session'ı KALICI YAPMAZ. Google, headless'ı güvenilmez cihaz olarak işaretler ve cookie'leri kalıcı olarak kaydetmez. Bu yüzden Authenticator kodu tercih edilir.
