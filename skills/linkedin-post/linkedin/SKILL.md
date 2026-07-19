---
name: linkedin
description: "LinkedIn post otomasyonu — psikoloji içerik üretimi + OAuth API entegrasyonu. Firecrawl ile araştırma, duplicate kontrolü, Türkçe post yazımı ve otomatik paylaşım."
version: 2.5.0
metadata:
  hermes:
    tags: [linkedin, social-media, psychology, content, automation]
    category: linkedin-post
---

# LinkedIn Post Otomasyonu

Edel'in Bardo Psychology LinkedIn hesabı için psikoloji içerikli Türkçe post üretimi.

## API Kurulumu (29 Mayıs 2026)

- **App**: Bardo Psychology, Client ID: `7780feuhqlkxe0`
- **Ürün**: Share on LinkedIn (`w_member_social` scope)
- **Token**: OAuth 2.0 3-legged flow ile alındı, 60 gün geçerli, refresh token mevcut
- **Token dosyası**: `~/.hermes/secrets/linkedin_token.json` (600)
- **Credential dosyası**: `~/.hermes/secrets/linkedin.env` (600)
- **Person URN**: `urn:li:person:hy0rYB54uc` (Berkcan Ulucan)
- **API script**: `~/.hermes/scripts/linkedin_api.py`
- **OAuth yöntemi**: `http://localhost/callback` redirect ile manuel code kopyalama

### Token Yenileme

- Token 60 gün geçerli, 50 günde otomatik yenilenir
- Manuel yenileme: `python3 ~/.hermes/scripts/linkedin_api.py refresh`
- Durum kontrolü: `python3 ~/.hermes/scripts/linkedin_api.py status`

```
### Post Paylaşım

```bash
# Metin post (archive_id ile — otomatik arşiv güncellemesi)
python3 ~/.hermes/scripts/linkedin_api.py post "Post metni buraya" --archive-id "post-id-buraya"

# Metin post (archive_id olmadan — eski davranış)
python3 ~/.hermes/scripts/linkedin_api.py post "Post metni buraya"

# Görselli post (1 Haz 2026 — test edildi ✅)
python3 -c "
from linkedin_api import create_post
result = create_post('Post metni...', image_path='/tmp/gorsel.jpg')
print(result)
"
```

### Post Silme

URN encode edilmeli: `urllib.parse.quote(urn, safe='')`. Başarılı → `204 No Content`.

### Görsel Üretimi — KALDIRILDI (Pollinations terk edildi)

[14 Tem 2026] Pollinations tamamen terk edildi. LinkedIn postları **görsel olmadan (sadece metin)** yayınlanır.

Görselli post için alternatif bir çözüm bulunana kadar `create_post(text="...")` ile sadece metin post atılır.
python3 -c "
from linkedin_api import create_post
print(create_post('Post metni', image_path='/tmp/gorsel.jpg'))
"

# Silme (URN URL-encode edilmeli)
# DELETE /v2/ugcPosts/urn%3Ali%3Ashare%3A...
```

Python'dan:
```python
from linkedin_api import create_post
create_post("metin", image_path="/tmp/image.jpg")
create_post("metin", archive_id="post-id")  # arşiv otomatik güncellenir
```

### Post Silme

```python
import urllib.parse, requests
encoded = urllib.parse.quote('urn:li:share:XXX', safe='')
requests.delete(f'https://api.linkedin.com/v2/ugcPosts/{encoded}', headers={...})
# → 204 No Content

Endpoint: `POST https://api.linkedin.com/v2/ugcPosts`
Headers: `X-Restli-Protocol-Version: 2.0.0`, `LinkedIn-Version: 202505`

## Workflow

**⚠️ HER ZAMAN EKİP'E DEVRET!** Post araştırması ve yazımı, ana konuşmayı BLOKE ETMEMELİDİR.

### EKİP Multi-Agent İş Akışı (4 Haz 2026 güncel)

| Adım | Ajan | Model | Port | Görev |
|------|------|-------|------|-------|
| 1 | 🔬 Analist | mimo-v2.5-free | Zen | Güncel psikoloji konusu araştır, 3 maddede özetle |
| 2 | ✍️ Yazar | GPT-5.4-mini | 19999 | Araştırmayı Türkçe LinkedIn postuna dönüştür |
| 3 | 📦 Yardımcı | Gemma | 19999 | Uzunluk, hashtag, yasaklı kelime kontrolü |
| 4 | ~~🎨 Görsel~~ | ~~—~~ | ~~—~~ | ~~Görsel üretimi durduruldu (Pollinations terk edildi)~~ |

### curl ile EKİP Kullanımı
```bash
# ADIM 1 — Analist araştırma
curl -s --max-time 45 http://127.0.0.1:19998/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"glm-5.1","messages":[...],"max_tokens":2000}'

# ADIM 2 — Yazar post yazımı
curl -s --max-time 30 http://127.0.0.1:19999/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-5.4-mini","messages":[...],"max_tokens":1000}'
```

**⚠️ Türkçe metinde JSON hatası (31 Mayıs 2026):** curl `-d` ile Türkçe karakter (ğ, ü, ş, ı, ö, ç) veya tırnak işareti içeren metin gönderirken "Malformed JSON" hatası alınır. ÇÖZÜM: `jq -n --arg` ile güvenli encoding:
```bash
CONTENT=$(cat /tmp/content.txt)
curl -s http://127.0.0.1:19999/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg c "$CONTENT" '{"model":"gpt-5.4-mini","messages":[{"role":"user","content":$c}],"max_tokens":800}')"
```
Direkt inline `-d '{"content":"Türkçe..."}'` kullanma — tırnaklar ve özel karakterler JSON'ı bozar.

**Neden curl?** Hermes `delegate_task` tek bir global model destekler, per-task override yok (issue #9459). Çok modelli EKİP için curl→proxy tek doğru yöntem.

**⚠️ delegate_task paralel tuzağı (1 Haz 2026):** `delegate_task`'in `tasks[]` dizisi **paralel** çalışır. Analist ve Yazar'ı aynı `tasks[]` içinde gönderirsen Yazar, Analist'in çıktısını **göremez** — kendi başına yeni kaynak arar, bambaşka bir konuda post yazar. Bu durumda Vanitas mecburen Yazar'ın postunu düzeltmek zorunda kalır (soru silme, ton ayarı vs). **Sıralı bağımlılık varsa ya EKİP curl kullan ya da delegate_task'i 2 ayrı çağrıda sıralı yap.**

### ⚠️ KRİTİK: HUMAN IN THE LOOP — Onaysız Paylaşım KESİNLİKLE YASAK

**Bu kural ihlal edilemez. İhlal = Edel postu silmek zorunda kalır.**

1. **Cron job ASLA kendiliğinden paylaşım yapmaz.** Cron'un tek görevi: taslak + görsel hazırla, Edel'e sun.
2. **Paylaşım sadece Edel ile birebir sohbette, açık onay sonrası yapılır.**
3. **Onay kelimeleri:** "paylaş", "gönder", "yolla", "onaylıyorum", "tamam", "evet", "yayınla" — bunlardan biri gelmeden İŞLEM YAPMA.
4. **"Onaylarsan paylaşacağım" mesajına istinaden otomatik paylaşım YAPMA.** Edel'in cevabını bekle.
5. **Edel "düzelt" veya "şurayı değiştir" derse** → postu düzelt, tekrar göster, tekrar onay bekle. Düzeltilmiş hali onaylamadan paylaşma.
6. **Arşiv canlandırma da aynı kurala tabi.** "Arşivden şunu paylaşayım mı?" → Edel onaylamadan paylaşma.
7. **Bu kuralın istisnası YOKTUR.** Cron job "post hazır, onaylar mısın?" diye sorar, Edel "paylaş" veya eşdeğer bir onay kelimesi söylemeden ASLA paylaşılmaz.

### Post Reddedilirse (31 Mayıs 2026)

Edel yeni hazırlanan postu beğenmezse **önce arşive bak**, yeni araştırmaya ATLAMA:

1. `linkedin_posts_archive.json` dosyasını oku
2. `status == "pending_approval"` (⚠️ "pending" DEĞİL!) olan postları filtrele
3. En güncel pending_approval postu Edel'e göster
4. Arşivde yoksa veya Edel onları da beğenmezse, ancak o zaman yeni araştırma başlat

**EK KURALLAR (29 Mayıs 2026):**
- **Üst üste farklı postları onaysız ATMA!** — İki farklı postu peş peşe, onay almadan paylaşma. Her post ayrı ayrı onaylanmalı.
- **Sabah/öğle/akşam çoklu post normaldir** — yeter ki her biri için Edel onayı alınsın.
- **Arşiv canlandırma = yeni post!** — Arşivdeki (`linkedin_posts_archive.json`) eski bir postu canlandırmadan önce de Edel'e sor. "Arşivden şu postu paylaşayım mı?" diye onay al.
- **Yanlış post atıldıysa** hemen Edel'i bilgilendir, durumu açıkla.

## 🔑 API Entegrasyonu (OAuth 2.0)

### ⚠️ ÖNCE ARAŞTIR, SONRA UYGULA

LinkedIn API entegrasyonu karmaşıktır. **İlk denemede ezbere gitme.** 
- OAuth flow başlamadan önce güncel endpoint'leri, redirect URI politikasını, 
  ve Developer Portal UI değişikliklerini araştır.
- Aynı yöntemi 2 kez başarısız olunca 3. denemeyi yapma — farklı strateji düşün.
- **App zaten kuruluysa Token Generator önerme!** Edel "app kurdum zaten" 
  dediğinde gereksiz yere sıfırdan kurulum önermek sinir bozucu.

### 🥇 Birincil Yöntem: Localhost Redirect + Manuel Kod Kopyalama

Bu yöntem **callback server gerektirmez** — en basit ve en güvenilir yöntemdir.

1. Developer Portal → Auth → Redirect URLs → ekle: `http://localhost/callback`
2. Authorization URL oluştur (`redirect_uri=http://localhost/callback`)
3. Edel linki tarayıcıda açar, onaylar
4. Tarayıcı `http://localhost/callback?code=XXX&state=YYY` adresine yönlenir
5. **Sayfa açılmaz** ("siteye ulaşılamıyor") — bu NORMAL! 
6. Edel **adres çubuğundaki URL'in tamamını** kopyalayıp sana gönderir
7. `code` parametresini parse edip token exchange yaparsın

```python
# Manuel kod ile token alma
code = "AQT..."  # Edel'den gelen
resp = requests.post(
    "https://www.linkedin.com/oauth/v2/accessToken",
    data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost/callback",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
)
```

### 🥈 Yedek Yöntem: Callback Server (Port 80)

Eğer localhost yöntemi çalışmazsa (örn. LinkedIn localhost redirect'i engelliyorsa).

Script: `scripts/callback_server.py`

- **Port 80 kullan** — Oracle Cloud VCN Security List'te 8888 kapalıdır!
- UFW kontrol et: `sudo ufw allow 80/tcp` (genelde zaten açık)
- Sunucu log'larını `~/.hermes/secrets/linkedin_callback.log` dosyasına yazar
- `serve_forever()` kullan, `handle_request()` tek istekte kapanır
- PYTHONUNBUFFERED=1 ile çalıştır, yoksa log buffer'lanır

```bash
# Manuel kod kopyalama (Edel'e söyle):
# "Adres çubuğundaki TÜM URL'i kopyala, code parametresi içinde olacak"
```

### ❌ Çalışmayan Yöntemler

| Yöntem | Neden Çalışmaz |
|--------|---------------|
| `https://www.linkedin.com/developers/tools/oauth/redirect` | **Boş sayfa** döner, code görünmez |
| `http://127.0.0.1:8888/callback` | Local Docker ortam, callback server aktif |
| Token Generator ("Generate Token" butonu) | App zaten kuruluysa gereksiz, Edel'in istemediği yönlendirme |

### Credential'lar

| Dosya | İçerik | İzin |
|-------|--------|------|
| `~/.hermes/secrets/linkedin.env` | `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET`, `LINKEDIN_REDIRECT_URI` | 600 |
| `~/.hermes/secrets/linkedin_token.json` | OAuth `access_token`, `refresh_token`, `expires_in` | 600 |

### OAuth Flow Adımları

1. **State oluştur** → `secrets.token_urlsafe(32)`
2. **Authorization URL** oluştur → `redirect_uri=http://localhost/callback` ile
3. **Edel linki açar, onaylar** → tarayıcı `localhost/callback?code=...` adresine yönlenir
4. **Edel URL'deki code'u kopyalar** → sana gönderir
5. **Token exchange** → `POST /oauth/v2/accessToken` ile access token al
6. **Token'ı ve person_urn'i kaydet** → `linkedin_token.json`
7. **Access token süresi**: 60 gün (5,183,999 saniye). 50 günde otomatik yenile.

### ⚠️ Oracle Cloud Port Pitfall

Oracle Cloud ARM64 sunucularda VCN Security List, UFW'den ayrı çalışır. 
- **8888 portu Oracle Security List'te kapalıdır** — UFW'de açsan da dışarıdan erişilemez
- **Port 80 ve 443** Oracle Security List'te zaten açıktır (HTTP/HTTPS)
- **Çözüm**: Callback server'ı direkt port 80'de çalıştır. `LINKEDIN_OAUTH_PORT=80` env var ile.

Detaylı endpoint'ler, header'lar ve örnek istekler: `references/api-integration.md`

### Token Ömrü ve Refresh

- Access token: 60 gün geçerli (LinkedIn policy)
- Refresh token ile yenileme:
  ```
  POST /oauth/v2/accessToken
  grant_type=refresh_token&refresh_token=<token>&client_id=...&client_secret=...
  ```
- **Pitfall**: Token expire olursa 401 döner → refresh dene, başarısızsa yeni OAuth flow başlat

### Post API: İki Seçenek

| Seçenek | Endpoint | Not |
|---------|----------|-----|
| **UGC Posts** | `POST /v2/ugcPosts` | ✅ **Çalışıyor (29 May 2026)** — `X-Restli-Protocol-Version: 2.0.0` + `LinkedIn-Version: 202505` header |
| **REST Posts** | `POST /rest/posts` | Yeni (2024+), `LinkedIn-Version: 202505` header |

**UGC Posts API kullanılır** (REST Posts denenmedi, gerek yok). Detaylı örnek: `references/api-integration.md`

### Person ID (URN) Alma

```python
GET https://api.linkedin.com/v2/userinfo
Authorization: Bearer <access_token>
# Response: {"sub": "abc123", "name": "...", "email": "..."}
# URN: f"urn:li:person:{sub}"
```

Her post öncesi person ID kontrol edilir, yoksa `/v2/userinfo` ile alınır.

### Post Gönderme

`scripts/linkedin_api.py` kullan. Direkt Python:
```python
from linkedin_api import create_post
# Metin post
result = create_post("Post metni")
# Fotoğraflı post (1 Haz 2026 — çalışıyor)
result = create_post("Post metni", image_path="/path/to/image.jpg")
# → {"success": True, "id": "urn:li:share:..."}
```

Endpoint: `POST https://api.linkedin.com/v2/ugcPosts`
Headers: `X-Restli-Protocol-Version: 2.0.0`, `LinkedIn-Version: 202505`, `Authorization: Bearer <token>`

### Callback Server

Script: `scripts/callback_server.py`

```bash
# 1. Port 80 kullan (Oracle Cloud'da 8888 VCN tarafından engellenir!)
export LINKEDIN_OAUTH_PORT=80

# 2. State ile başlat
export LINKEDIN_OAUTH_STATE=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
sudo -E python3 scripts/callback_server.py

# 3. Token alındıktan sonra — port 80 HTTP için sürekli açık, kapatma
```

## ⚠️ KRİTİK PİTFALL: LinkedIn Anti-Bot Koruması

**LinkedIn, otomatik isteklere karşı en agresif platformlardan biridir.**

- ❌ Firecrawl ile LinkedIn URL'leri çekilemez — `"Your request was blocked."` hatası alınır
- ❌ Doğrudan web scraping LinkedIn'de çalışmaz
- ❌ `web_extract` ve `web_search` LinkedIn sayfalarında engellenir

### Çözüm: Alternatif Kaynaklar

LinkedIn içeriği için **LinkedIn'in kendisini scrape etmeye çalışma**. Bunun yerine:

| Kaynak | URL | Not |
|--------|-----|-----|
| APA (American Psychological Association) | apa.org | Akademik, güvenilir. RSS feed mevcut → `references/apa-content.md` |
| Psychology Today | psychologytoday.com | Popüler psikoloji, güncel |
| PsycNet | psycnet.apa.org | Araştırma veritabanı |
| Science Daily - Psychology | sciencedaily.com/news/mind_brain | Güncel araştırma özetleri |
| Türk Psikologlar Derneği | psikolog.org.tr | Yerel içerik |
| Google Scholar (psikoloji) | scholar.google.com | Akademik makaleler |

## 🛑 KONU BİRİKME LİMİTİ (ZORUNLU — ATLANAMAZ)

**Kuyrukta 2'den fazla konu biriktiğinde yeni içerik taraması (besleme) DURUR.**

- Kontrol edilecek kayıtlar: `status == "pending"` VEYA `status == "pending_approval"`
- Toplam >= 2 ise → **[SILENT]** — yeni kaynak tarama, mevcutları işle
- Toplam < 2 ise → yeni kaynak ara
- Bu kural HEM cron job'da HEM manuel işlemlerde geçerlidir
- Amaç: Edel'in önünde onay bekleyen 2'den fazla post birikmemesi

### 🔴 DUPLICATE KONTROLÜ (ZORUNLU — ATLANAMAZ)

Her yeni post ÜRETMEDEN ÖNCE aşağıdaki adımları UYGULA:

1. `linkedin_posts_archive.json` dosyasını oku (tüm postlar burada)
2. Şu kriterlerden HERHANGİ BİRİ eşleşirse o konuyu ATLA:
   - Aynı `source_url` daha önce işlenmişse (posted veya pending_approval)
   - Aynı BAŞLIK (title) %80+ benzerlikle daha önce kullanılmışsa
   - Aynı KAYNAK (APA makalesi vb.) daha önce referans gösterilmişse
3. Eşleşme varsa → farklı konu bul, yeni kaynak ara
4. Eşleşme yoksa → yeni post üret

**ÖNEMLİ:** Bir kaynak (APA makalesi) BİR KEZ kullanılır, 3 farklı postta kullanılmaz.

**Kontrol dosyaları:**
- `~/.hermes/data/linkedin_posts_archive.json` (tam metin — öncelikli)
- `~/.hermes/data/linkedin_posts.json` (özet kayıt)

**⚠️ Pitfall:** Statü `"pending_approval"` (DEĞİL `"pending"`!). Metin alanı `"text"` (DEĞİL `"content"`!).

## Post Arşivi

LinkedIn kurulumu olmadığında onay bekleyen postlar birikir. Tüm post metinleriyle birlikte:
`~/.hermes/data/linkedin_posts_archive.json`

Bu dosya tam metinleri içerir, LinkedIn kurulduğunda buradan alınıp paylaşılabilir.

## Post Formatı

### Yazım Stili: Hakan Türkçapar
Akademik altyapılı ama günlük dilden, sıcak, samimi, okuyucuyu zorlamayan, bilgiyi sohbet havasında veren bir anlatım. Karmaşık psikoloji kavramlarını herkesin anlayabileceği şekilde sadeleştir. Otoriter değil, "birlikte düşünelim" havasında olsun.

**Türkçapar yazı örnekleri:** `references/turkcapar-writing-samples.md` — post yazarken bu dosyadaki örnekleri referans al. Karakteristik özellikler: soruyla başlama, sohbet akışı, kısa paragraflar, "Yani...", "Dahası..." bağlaçları, spesifik detaylara yer verme.

### Post Yapısı (6 Katman)
Şu sırayla ak:
1. **Vurucu giriş** — 1 cümle, okuyucuyu içine çeken, düşündüren
2. **APA kaynak referansı** — "APA Monitor on Psychology'nin X sayısındaki Y yazısı" formatında
3. **Yani / çıkarım** — Kaynağı yorumlayan, "Yani..." ile bağlayan 1 cümle
4. **Araştırma detayı** — Spesifik atıf: "Yazar ve arkadaşlarının YIL'da DERGİ'de yayımladığı meta-analiz"
5. **Dahası / ek detay** — "Dahası..." ile bağlanan ilginç ikincil bulgu
6. **Vurucu kapanış** — "Bu demek oluyor ki..." veya "Belki..." ile başlayan akılda kalan son cümle

### Kurallar
- Dil: **Türkçe**, doğal sohbet havası
- Uzunluk: **500-750 karakter** (kısa ve öz)
- **Hashtag KULLANMA** — hiç ekleme
- Hitap: doğrudan anlatım (ne "sen" ne "siz" — direkt anlat)
- KISA paragraflar (maks 1-2 cümle)
- Doğal bağlaçlar: "Yani...", "Dahası...", "Bu demek oluyor ki..."
- Referanslar APA formatında: "Yazar ve ark., YIL, DERGİ"

### YASAKLAR
- ❌ Emoji (post metninde)
- Maks 3-4 hashtag, post sonunda ayrı satırda (konuyla ilgili seç: #Psikoloji #YapayZeka #RuhSağlığı #DijitalSağlık #AI #MentalHealth vb.)
- ❌ #terapi veya "terapi" kelimesi
- ❌ CTA/soru ("ne düşünüyorsun?", "yorumlarda buluşalım")
- ❌ Genel referans ("APA'nın araştırmasına göre" gibi)
- ❌ "sen" veya "siz" hitabı

## 🖼️ Görsel Ekleme (1 Haz 2026 ✅)

linkedin_api.py image upload destegi eklendi. create_post(text, image_path="...") ile calisir.

### Görsel Üretimi — KALDIRILDI

[14 Tem 2026] Pollinations terk edildiği için görsel üretimi yok. `create_post(text="...")` ile sadece metin post atılır.

### Post Silme

DELETE /v2/ugcPosts/urn%3Ali%3Ashare%3AXXX → 204 No Content (URN encode edilmeli)

### ⚠️ Yayınlamadan Önce: Kaynak Doğrula!

Post metnindeki HER İDDİA için kaynak makaleyi web_extract ile aç, doğrula. "Psychology Today'de çıkan araştırmaya göre" yazdıysan, o makaleyi gerçekten açıp kontrol et. Postu ancak doğrulamadan sonra paylaş. Edel'in direktifi: "bilgiyi doğruladıktan sonra aldığın kaynaktan."

## Cron Job'lar

- `272dc0178605` (linkedin_sabah) — 09:00, günlük sabah postu (NVIDIA/minimax-m3)
- ~~`79aa6f693b23` (linkedin_aksam) — Pollinations kapandı, cron silindi~~

### ⚠️ Cron Prompt Senkronizasyonu (5 Haz 2026)

**PITFALL:** Cron job prompt'ları skill'deki EKİP workflow'undan bağımsız yaşar — skill'i güncellemek cron prompt'unu otomatik güncellemez. Skill'e yeni bir adım (örn. görsel üretimi) eklendiğinde, cron job prompt'ları da `cronjob(action='update', job_id='...', prompt='...')` ile güncellenmelidir.

**Kontrol listesi:**
- Skill'deki EKİP workflow adımları ile cron prompt'undaki ADIM'lar birebir aynı olmalı
- Yeni adım eklenince İKİ cron job'u da (sabah + akşam) güncelle
- Görsel adımı (ADIM 4) ATLANAMAZ — MEDIA: ile gösterim zorunlu

### Pipeline Durdurma/Başlatma

LinkedIn kurulumu hazır değilse veya bakım gerekiyorsa:

```bash
# Durdur
cronjob(action='pause', job_id='272dc0178605')
cronjob(action='pause', job_id='79aa6f693b23')

# Başlat
cronjob(action='resume', job_id='272dc0178605')
cronjob(action='resume', job_id='79aa6f693b23')
```

### Post Arşivi

- **Duplicate kontrol JSON'u:** `~/.hermes/data/linkedin_posts.json` — başlık, URL, hash (işlenmiş/onayda postlar)
- **Tam metin arşivi:** `~/.hermes/data/linkedin_posts_archive.json` — tüm postların tam metni, statüsü ve kaynağıyla birlikte
- **⚠️ Alan adı:** `"text"` (DEĞİL `"content"`!) — yanlış alan adıyla okursan boş döner
- **⚠️ Statü değeri:** `"pending_approval"` (DEĞİL `"pending"`!) — filtrelerken tam eşleşme kullan

**⚠️ Arşiv arama pitfall'ları:**
- **Statü değeri:** `"pending_approval"` — `"pending"` DEĞİL! `"pending"` diye filtreleyince hiçbir sonuç çıkmaz.
- **Metin alanı:** `"text"` — `"content"` DEĞİL!
- **İki dosya farkı:** Arşivde 7 post olabilirken duplicate kontrol dosyasında 6 post olabilir — arşiv daha günceldir. Paylaşılmamış post araken **önce arşive bak**, duplicate dosyasına değil.
- **Wiki'de linkedin post arşivi yok** — postlar sadece bu iki JSON dosyasında tutulur.

**⚠️ Arşiv statü değerleri:**
| Statü | Anlamı |
|-------|--------|
| `posted` | Paylaşıldı |
| `pending_approval` | Onay bekliyor (⚠️ "pending" DEĞİL!) |

Filtreleme yaparken `status == "pending"` diye ararsan **0 sonuç** alırsın. Doğrusu: `status == "pending_approval"`.

## Hata Durumları

| Hata | Sebep | Çözüm |
|------|-------|-------|
| `Duplicate content` | Aynı konu | Farklı kaynak ara |
| Firecrawl timeout | Kaynak yavaş | Timeout'u 60s yap |
| **API 401 Unauthorized** | Token expire olmuş | Refresh token ile yenile, başarısızsa yeni OAuth flow |
| **API 403 Forbidden** | Scope yetkisiz / ürün eksik | Developer Portal → Products → "Share on LinkedIn" ekle |
| **OAuth `invalid_redirect_uri`** | URI Developer Portal'da kayıtlı değil | Auth sekmesinde URI'yi kontrol et |
| **Callback server timeout** | 120sn içinde kullanıcı onaylamadı | Süreyi artır, port 80'e geç, veya manuel kod kopyalama yap |
| **Token Generator önerme!** | App zaten kurulu → Token Generator gereksiz, Edel sinirlenir | Direkt callback server ile hallet, Token Generator sadece sıfırdan kurulumda |
| **REST API 404** | REST Posts endpoint kullanılamıyor | UGC Posts'a fallback yap (otomatik) |
| **Arşiv boş görünüyor (0 sonuç)** | `status == "pending"` filtresi yanlış | `status == "pending_approval"` kullan |
| **curl "Malformed JSON" (31 Mayıs)** | Türkçe karakter/özel karakter JSON'ı bozuyor | `jq -n --arg` ile güvenli encoding, inline `-d` kullanma |
| **Yazar farklı kaynak kullanmış (1 Haz)** | `delegate_task` paralel → Yazar Analist'in çıktısını göremez, kendi başına yeni kaynak arar | EKİP curl (sequential) veya delegate_task'i sıralı 2 çağrıda yap. Paralel tasks[] array'i sadece birbirinden bağımsız işler için. |
| **Yazar curl timeout exit 28 (1 Haz)** | Uzun içerik (2000+ kelime) GPT-5.4-mini'de 30sn'yi aşıyor | `--max-time 45` kullan. Kısa içerikte 30sn yeterli, uzun makale özetlerinde 45sn. |
| **Yardımcı/Gemma #terapi eklemiş (2 Haz)** | Gemma "#terapi kullanma" kuralını görmezden gelip posta #terapi EKLİYOR | Gemma kontrolüne GÜVENME. Postu mutlaka manuel kontrol et, #terapi varsa sil. Final hashtag'leri Vanitas kendisi 3-4'e indirsin. |
| **GLM-5.1 timeout exit 28 (2 Haz)** | OpenCode Go proxy üzerinden GLM-5.1 hiç yanıt vermez, `--max-time 60` da yetmez | GPT-5.4-mini fallback (port 19999). İkinci kez GLM-5.1 deneme. Detay: `references/ekip-agent-pitfalls.md` |

### APA İçerik Kullanımı ✅ (29 Mayıs 2026)

**Edel direktifi**: My APA'yı kaynak olarak kullan, bilgileri Edel'e öğret.

- **Birincil kaynak: Monitor on Psychology** — RSS feed 29 Mayıs 2026 itibarıyla Incapsula korumalı, artık browser ile taranıyor
- APA içeriğini sadece post için değil, **Edel'in mesleki gelişimi** için de kullan
- Yeni araştırma bulduğunda: önce özetle, sonra "bu senin pratiğinde nasıl kullanılır" diye sor
- CE kurslarını takip et, Edel'e hangilerini alması gerektiğini söyle
- Monitor dergisinin her sayısını kontrol et, en iyi makaleleri öner
- Detaylı katalog: `references/apa-content.md`

### Erişim Matrisi

| Yöntem | Sonuç | Not |
|--------|-------|-----|
| **`browser_navigate`** (Hermes browser) | ✅ Çalışıyor | Gerçek tarayıcı (Browserbase), hem APA Incapsula'yı hem Skool Cloudflare'ı aşıyor, tam metin |
| **`web_extract`** | ⚠️ Kısmi | ~5000 karakter alınabiliyor, sonra LLM timeout'a giriyor |
| **`requests` + WARP SOCKS5** | ❌ | WARP IP değiştiriyor ama Incapsula JS challenge'ı aşamıyor (212 byte boş sayfa). Skool'da da çalışmaz. |
| **RSS feed** (curl) | ❌ Engelleniyor | 29 Mayıs 2026 itibarıyla Incapsula koruması eklendi |
| **Browser console extract** | ✅ Çalışıyor | `document.querySelector('main').innerText` ile tam metin |
| Playwright local (stealth+WARP) | ❌ | `navigator.webdriver=false` ama `plugins=0` yakalanıyor |
| Cookie export → curl | ❌ | `reese84` cookie'si browser fingerprint ile doğrulanıyor |

**APA ve Skool için birincil yöntem: `browser_navigate` (`engine: auto`) ile tam metin oku.** `engine: chrome` (WARP) sadece Google servisleri için kullanılır, APA/Skool'da çalışmaz. Detay: `warp-proxy` skill'i.

### İçerik İş Akışı

```
Monitor on Psychology       →  browser_navigate + browser_console ile makaleleri tara
      ↓
İlginç makale seçimi       →   Psikolojiyle alakalı başlık + özet (AI makaleleri öncelikli)
      ↓
browser_console            →   document.querySelector('main').innerText ile tam metin
      ↓
Vanitas okur + özetler     →   Basit Türkçe, jargonu açıklayarak (Edel tercihi)
      ↓
📝 Wiki'ye kaydeder        →   ~/wiki/apa-articles/ altında İngilizce
      ↓
🎙️ NotebookLM podcast      →   Özel prompt ile Türkçe sohbet formatında podcast
      ↓
📱 Edel'e iletir           →   "Bu hafta APA'dan öğrendiklerin" + podcast
      ↓
✂️ LinkedIn post taslağı   →   Podcast'ten en çarpıcı bölümü 800-1500 karakter
      ↓
Edel onayı                 →   ASLA onaysız post atma!
      ↓
linkedin_api.py post       →   Otomatik paylaşım
```

### NotebookLM Podcast Prompt'u

```
Bu içeriği bir psikolog arkadaşına anlatır gibi, Türkçe, sohbet havasında, 
jargonu açıklayarak, pratik uygulamaları vurgulayarak anlat. 
Kısa tut, en fazla 10 dakika. 
Araştırmanın bulgularını, günlük hayattaki karşılığını ve 
bir terapist olarak nasıl kullanabileceğini anlat.
```

### My APA Kaynakları (Üye Girişiyle)

| Kaynak | Erişim | Kullanım |
|--------|--------|----------|
| **Monitor on Psychology** | Aylık dergi | LinkedIn içeriği, mesleki gelişim |
| **Research Alerts** | Haftalık email | Yeni araştırma bildirimleri |
| **Ücretsiz CE Kursları** | 5 hak | Lisans yenileme kredisi |
| **Journal abonelikleri** | Member | Akademik makaleler |
| **APA Divisions** | Member | Uzmanlık ağları |

### APA Login ✅ (Test Edildi, Çalışıyor — 29 Mayıs 2026)

- Login sayfası: `https://sso.apa.org/apasso/idm/apalogin?ERIGHTS_TARGET=https://www.apa.org`
- Browser ile login sayfası açılıyor (Incapsula yok)
- Input ID'leri: `#loginName` (email), `#loginPassword` (şifre)
- Hesap: `isimgorulsunn@gmail.com`
- Şifre: `~/.hermes/secrets/apa.env` (600)
- **Login BAŞARILI** — My APA portal (`my.apa.org/portal/home`) tam erişim
- Auth cookie: `ERIGHTS` + `reese84` (fingerprint bağlı, curl'da çalışmaz)
- Cookie dosyası: `~/.hermes/secrets/apa_cookies.json`
- Member kaynakları: Monitor on Psychology, dergi abonelikleri, CE credits

### RSS Feed Detayları

- URL: `https://www.apa.org/news/press/releases/press-release-rss.xml`
- Format: RSS 2.0, XML
- İçerik: Her `<item>` içinde `<title>`, `<description>`, `<link>`, `<pubDate>`
- Örnek makale bağlantısı: RSS'teki `<link>` → browser ile açılır
- Güncelleme sıklığı: Haftada 1-2 yeni makale
- Tüm teknik detaylar: `references/apa-incapsula.md`

## Referanslar

- `references/youtube-backlink-pipeline.md` — YouTube backlink pipeline (Google OAuth scope, veo video, Julian Goldie analizi)
- `references/delegation-pattern.md` — Alt ajana devretme pattern'i
- `references/delegate-workflow.md` — Alt ajana devretme iş akışı
- `references/compound-error-pitfall.md` — Bileşik hata yapmama kuralı
- `references/gmail-notebooklm-pipeline.md` — Gmail → NotebookLM pipeline
- `references/my-apa-catalog.md` — My APA üye portalı
- `references/apa-incapsula.md` — APA Incapsula WAF araştırması
- `references/apa-wiki-conventions.md` — APA makale wiki yazım kuralları
- `references/apa-content.md` — APA içerik kaynakları
- `references/anti-bot-errors.md` — LinkedIn anti-bot hataları
- `references/provider-issues.md` — Provider kesintisi tanı ve çözüm
- `references/api-integration.md` — OAuth flow, token yönetimi, Post API (+image, +silme)
- `references/ekip-agent-pitfalls.md` — EKİP ajan hataları: GLM-5.1 timeout/boş dönme, Gemma #terapi sabotajı (2 Haz 2026)
- `scripts/linkedin_api.py` — Token yönetimi + post oluşturma (+image, +silme)
- `scripts/callback_server.py` — OAuth callback yakalama server'ı

## Absorbed Skills

The following LinkedIn-related skills were consolidated into this umbrella. Their unique content was moved into `references/`.

| Absorbed Skill | Reference File |
|---|---|
| `linkedin-api` | `references/linkedin-api-guide.md` |
| `linkedin-writing` | `references/linkedin-writing-methodology.md` |
| `apa-referenced-content` | `references/apa-content-production.md`, `references/article-retrieval-pipeline.md`, `references/article-rotation.md`, `references/onay-akisi.md`, `references/apa-webinar-registration.md` |
