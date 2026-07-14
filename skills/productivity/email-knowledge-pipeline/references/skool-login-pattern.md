# Skool Login Pattern

## 🥇 Önce Dene: Public Post Extraction (27 Haz 2026)

Skool bildiriminden gelen bir post'a erişmek için **ilk tercih** browser login DEĞİL, public URL extraction'dır. Birçok Skool topluluğu post'ları genel erişime açar.

**Workflow:**

1. Mail body'sinden veya bildirimden post başlığını al
2. `web_search` ile public URL'yi bul:
   ```
   site:skool.com "post başlığı burada"
   ```
3. Bulunan `skool.com/<topluluk>/<post-slug>` linkini `web_extract` ile oku
4. Başarılıysa → post body'si, yorumlar, dosya linkleri gelir. Browser login'e gerek yok.
5. `web_extract` başarısız olursa veya post login duvarına takılırsa → browser login'e geç.

**Örnek (27 Haz 2026):**
- Post başlığı: "I asked Claude Code to make me as much money as possible"
- `web_search` → `skool.com/ai-automation-society/new-video-i-asked-claude-code-to-make-me-as-much-money-as-possible`
- `web_extract` → tam içerik: 4 upgrade listesi, /roast ve /session-handoff skill'leri, community yorumları

**Neden önce bu?**
- Browser login: OTP kodu gerekir, UI değişikliklerine duyarlıdır, timeout riski yüksektir
- Public extraction: 2 adımda biter, cron'da çalışır, güvenilirdir
- Sadece public olmayan post'lar için browser login'e gerek kalır

## Fallback: Browser Login (email kod ile)

## ⚠️ 7 Haz 2026 Güncelleme — UI Değişikliği

Son kullanımda (7 Haz 2026), `https://www.skool.com/login` sayfasında sadece email + password alanları göründü. "Log in with a code" seçeneği doğrudan gözükmedi.

**Olası nedenler:**
- Skool kod login'i kaldırmış veya gizlemiş olabilir (UI güncellemesi)
- Kod seçeneği email girdikten sonra görünebilir (test edilmedi)
- A/B testi olabilir

**Strateji:** Normal login dene (email+password). Eğer şifre yoksa, mail body'sinden içerik çıkar.

## Adım Adım (Kod Login — hala çalışıyorsa)

```bash
# 1. Login sayfasına git
browser_navigate("https://www.skool.com/login")

# 2. Email gir — "Log in with a code" email sonrası çıkabilir
browser_type(ref=email_input, text="isimgorulsunn@gmail.com")

# 3. Kod seçeneğini tıkla (görünüyorsa)
browser_click(ref=code_button)

# 4. Gmail'de kodu bul
ALL_PROXY="" python3 google_api.py gmail search "skool code" --max 1
# → "3155 is your Skool log in code"

# 5. Kodu Skool'da gir
browser_type(ref=code_input, text="3155")
browser_click(ref=login_button)
```

## Fallback — Kod Login Yoksa veya Şifre Yoksa

Eğer Skool'a giriş yapılamıyorsa:

1. **Mail body'sini çek:** `gmail get ID` ile mail içeriğini al
2. **Link varsa dene:** Mailde ders/araç linki varsa `web_extract` ile public sayfayı oku
3. **Tahmin et:** Ders adından içerik türünü çıkar — "Podcast Otomasyonu Açıldı" → podcast üretim aracı, "Nate Herk Connections vs Credentials" → network oluşturma stratejisi
4. **Edel'e not et:** "Skool'da X dersi var, içeriğe girmek için şifre lazım" diyerek eksik bilgiyi belirt

**Kural:** Mail "X yeni bildirim" dese bile ATLAMA. Mail body'sinden ne bilgi alabiliyorsan al, Edel'e sohbet tonunda aktar.

## Pitfalls

- Kod 10 dakika geçerli, süresi dolduysa "Resend" ile yenisini iste
- Login sonrası sayfa boş görünebilir (JS-heavy) — `browser_snapshot(full=true)` kullan
- Skool URL pattern'i: `https://www.skool.com/[topluluk-slug]/classroom/[ders-id]`
- Classroom içeriği dropdown ile açılır — butona değil, içindeki `clickable [onclick]` elementine tıkla
- Gmail aramasında `ALL_PROXY=""` zorunlu (Google API lokal bağlantı ister)
