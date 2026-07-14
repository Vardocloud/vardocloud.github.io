# Gmail Deep Dive — Link Takip Pattern'leri

Bir email'deki her link tipi farklı işlem gerektirir. Aşağıdaki sınıflandırmayı kullan.

## 1. Blog / Duyuru Linki

**Tespit:** Medium, Substack, newsletter, kişisel blog, haber sitesi domain'i

**İşlem:**
- `web_extract` ile TAM yazıyı çek (özet değil)
- Ana argümanı çıkar
- 5-7 önemli nokta listele
- Referansları ve verileri not et
- Yazar adı ve tarih mutlaka kaydet

**Tuzak:** Özet/tanıtım yazısına takılıp kalma. URL'nin kendisi newsletter teaser'ı olabilir — scroll et veya devamını oku.

```python
# Örnek: blog içeriğini çek
from hermes_tools import web_extract
result = web_extract(urls=["https://example.com/blog/post"])
print(result)
```

## 2. Skool Post Linki

**Tespit:** skool.com domain'i, topluluk içi paylaşım

**İşlem:**
- `browser_navigate` ile sayfaya git (Skool login gerektiriyorsa skool-login-pattern.md'e bak)
- Post içeriğini baştan sona oku
- Repo/kaynak linki varsa ONLARA DA GİT
- Repo için: README, description, yıldız sayısı, son güncelleme

**Tuzak:** Skool auth gerektirir. Login değilsen `browser_vision` içerik göstermeyebilir. Email kod ile login pattern'ini kullan.

## 3. Provider / Tool Linki (Fırsat Taraması)

**Tespit:** SaaS, API, tool, platform domain'i

**İşlem:**
- Pricing/features sayfasını aç (`/pricing`, `/plans`)
- SADECE ücretsiz ($0 / free tier) olanları not et
- Paralı servisleri ATLA (kaydetme, wiki'ye girme)
- Özellik setini kategorilendir: AI, analiz, otomasyon, data vb.

**Tuzak:** "Free trial" ≠ ücretsiz. Credit card isteniyorsa paralı say.

## 4. APA / Akademik Link

**Tespit:** apa.org, psycnet, pubmed, scholar domain'i

**İşlem:**
- `web_extract` ile dene (Incapsula engeli varyantı için apa-incapsula-workaround.md'e bak)
- Tam metin yoksa özet/künye bilgilerini al
- Webinar/etkinlik linki varsa → click.info.apa.org tracking linkini curl -IL ile çöz

## 5. Transactional / Doğrulama Linki

**Tespit:** "verify", "confirm", "reset password", "login code"

**İşlem:** ATLA. İçerik değeri yok.

## Hiyerarşi

Her email için:
1. `gmail get` ile body'yi al
2. Body'deki linkleri tara (href veya text URL)
3. Domain'e göre yukarıdaki kategorilerden birine ata
4. İlgili pattern'i uygula
5. Hiç link yoksa: body içeriğini direkt işle
