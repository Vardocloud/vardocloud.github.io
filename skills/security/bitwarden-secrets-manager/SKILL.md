---
name: bitwarden-secrets-manager
title: Bitwarden Secrets Manager Kurulumu ve Kullanımı
description: >-
  Hemres v29+ Bitwarden Secrets Manager eklentisi — bws CLI kurulumu,
  OAuth2 client_credentials token alma, secret CRUD, isimlendirme
  kuralları ve provider görünürlük önlemleri.
trigger: >-
  User mentions Bitwarden eklentisi/entegrasyonu. User wants to securely
  store API keys. "secretları deepseek görmemeli" ifadesi geçtiğinde.
  User yeni API key eklemek istediğinde.
---

# Bitwarden Secrets Manager — Hermes Eklentisi

Hermes v29+ sürümünde `secrets.bitwarden` yapılandırması ile gelen
Bitwarden Secrets Manager (BWS) entegrasyonu.

## Kurulum Adımları

### 1. BWS Binary'sini İndir

```bash
# Hermes otomatik kurulum (v2.0.0)
hermes secrets bitwarden install
```

Yeni sürüm gerekirse GitHub releases sayfasından indir (sdk-sm repo, bws-v{X.Y.Z} tag),
ardından `~/.hermes/bin/bws`'ye kopyala.

### 2. Access Token Al (OAuth2 Client Credentials)

Web UI'dan access token oluşturmak mümkün, ancak client_id + client_secret
varsa OAuth2 flow ile terminal üzerinden alınır (credential'lar AI model
context'ine girmez).

**Identity API çağrısı:**
- URL: `https://identity.bitwarden.com/connect/token`
- Headers: `Content-Type: application/x-www-form-urlencoded`, `Bitwarden-Client-Version: 2025.1.0`
- Body (form-encoded): `client_id=user.xxx&client_secret=...&scope=api&grant_type=client_credentials&deviceType=8&deviceIdentifier=<uuid>&deviceName=bws`

**Kritik:** Device bilgileri BODY'de gönderilir, header'da değil. "device_error"
hatası alınırsa device parametreleri body'ye taşınır.

**Detaylı setup:** `sensitive-data-pipeline` skill'inde `references/bitwarden-sm-oauth2-setup.md`

### 3. bws CLI Konfigürasyonu

```bash
~/.hermes/bin/bws config server-identity https://identity.bitwarden.com
~/.hermes/bin/bws config server-api https://api.bitwarden.com
```

Not: `bws config set` diye bir komut yok — direkt `bws config <NAME> <VALUE>`.

### 4. Proje Oluştur

```bash
# Proje adı positional argümandır, --name flag değil
~/.hermes/bin/bws project create "proje-adi" --output json
```

### 5. Hermes Eklentisini Aktifleştir

```bash
hermes secrets bitwarden setup \
  --access-token "$TOKEN" \
  --server-url "https://vault.bitwarden.com" \
  --project-id "$PROJECT_ID"
```

Bu komut config.yaml'e secrets.bitwarden bölümünü ekler.

## Secret CRUD İşlemleri

### 🔴 KRİTİK: Secret ID vs Key Name (14 Tem 2026)

`bws secret get <SECRET_ID>` — **SECRET_ID = UUID'dir, key name DEĞİL!**
`bws secret get OPENROUTER_API_KEY` ❌ hata verir (`invalid character`)
`bws secret get d53b6ab2-...` ✅ çalışır

UUID'yi `bws secret list` çıktısındaki `id` alanından al:

```bash
# Önce list'ten UUID'yi bul, sonra get ile çek
ID=$(bws secret list | python3 -c "import json,sys; data=json.load(sys.stdin); [print(s['id']) for s in data if s['key']=='OPENROUTER_API_KEY']")
bws secret get "$ID"
```

Bu pitfall özellikle BWS'ye yeni başlayanlar için sinsi bir hatadır — çünkü çoğu CLI tool'u (`gh secret`, `aws ssm`, `gcloud secrets`) key name ile çalışır, BWS ise UUID ister.

### Tek Secret Getirme (20 Haz 2026)

Tek bir API key'i test etmek için `bws secret get <SECRET_ID>` kullanılır (tüm listeyi çekmekten daha hızlı, daha az token):

```bash
# Single secret fetch → parse → test → return masked result
~/.hermes/bin/bws secret get <SECRET_ID> | python3 -c "
import json, sys, urllib.request, urllib.error
d = json.load(sys.stdin)
key = d['value']
masked = key[:6] + '...' + key[-4:]
print(f'SECRET: {d[\"key\"]} ({masked})')
# Immediately test the key against live API
try:
    req = urllib.request.Request(
        'https://api.routeway.ai/v1/models',
        headers={'Authorization': f'Bearer {key}'}
    )
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    print(f'API Status: ✅ HTTP {resp.status}, {len(data[\"data\"])} models')
except Exception as e:
    print(f'API Error: ❌ {e}')
"
```

Bu pattern:
- Secret'ın sadece ilk 6 + son 4 karakterini gösterir
- Key'i stdout'a yazmaz (sadece Python belleğinde kalır)
- Canlı API testini aynı terminal çağrısında yapar
- Hata durumunda net hata mesajı döndürür

### Listeleme (değerleri maskele!)

```bash
# Token env'den okunur
~/.hermes/bin/bws secret list PROJECT_ID
```

**Provider görünürlük uyarısı:** `bws secret list` çıktısı **decrypted değerleri**
içerir ve primary model context'ine girer. DeepSeek/Claude gibi external
provider'lar bu değerleri görebilir. ŞU ŞEKİLDE KULLAN:

```bash
# Değerleri maskeli göster
~/.hermes/bin/bws secret list PROJECT_ID | python3 -c "
import json, sys
data = json.load(sys.stdin)
for s in sorted(data, key=lambda x: x['key']):
    val = s['value']
    masked = val[:6] + '...' + val[-4:] if len(val) > 12 else '****'
    print(f'  {s[\"key\"]:<35} {masked}')
print(f'Total: {len(data)} secrets')
"
```

### Yeni Secret Ekle

```bash
~/.hermes/bin/bws secret create KEY_NAME --value "deger" \
  --project-id PROJECT_ID --organization-id ORG_ID
```

### 🔴 KRİTİK: Kullanıcıdan Raw Key Alındığında Workflow

Kullanıcı sana ham bir API key verdiğinde (örn: "Al bu keyi BWS'ye kaydet"):

**Adım adım workflow:**

1. **Önce canlı API'de test et** — key'in geçerli olduğunu doğrula
2. **Sonra BWS'ye kaydet** — `bws secret create`
3. **Doğrula** — `bws secret list` ile listede göründüğünü kontrol et

```bash
# ADIM 1: Test — key'i servisin canlı API'sine karşı dene
# (Servise göre endpoint değişir — curl ile basit bir test)
TEST_KEY="verilen_key_buraya"
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $TEST_KEY" \
  https://api.soniox.com/v1/models  # Örnek: Soniox için
# → 200/401/403 görmelisin

# ADIM 2: Geçerliyse BWS'ye kaydet
BWS=~/.hermes/bin/bws
$BWS secret create SONIOX_API_KEY --value "$TEST_KEY" \
  --project-id "$($BWS secret list | python3 -c "import json,sys; print(json.load(sys.stdin)[0]['projectId'])")" \
  --organization-id "$($BWS secret list | python3 -c "import json,sys; print(json.load(sys.stdin)[0]['organizationId'])")"

# ADIM 3: Doğrula
$BWS secret list | python3 -c "
import json,sys
data = json.load(sys.stdin)
for s in sorted(data, key=lambda x: x['key']):
    if 'SONIOX' in s['key'].upper():
        v = s['value']
        m = v[:6] + '...' + v[-4:] if len(v) > 12 else '****'
        print(f'  ✅ {s[\"key\"]:<35} {m}')
"
```

**Neden test önce?** Çünkü BWS'ye kaydedilen geçersiz key daha sonra kafa karıştırır — "BWS'de var ama çalışmıyor" sorununa yol açar. Ayrıca raw key'i terminal'de değişkende tutup sadece API yanıtını context'e aktarırsın (key'in kendisi context'e girmez).

**Pitfall:** `bws secret create` komutu `--project-id` ve `--organization-id` parametrelerini ister. Bunları elle yazmak yerine mevcut bir secret'tan otomatik çek (yukarıdaki gibi).

### Secret Düzenle (isim/değer değiştir)

```bash
# İsim değiştir
~/.hermes/bin/bws secret edit SECRET_ID --key "YENI_ISIM"

# Değer değiştir
~/.hermes/bin/bws secret edit SECRET_ID --value "yeni_deger"
```

### Secret Sil

```bash
~/.hermes/bin/bws secret delete SECRET_ID
```

## İsimlendirme Kuralı

Secret key ismi = environment variable adı (UPPER_CASE, underscore).

| Doğru | Açıklama |
|-------|----------|
| `POLLINATIONS_API_KEY` | Pollinations API |
| `MISTRAL_API_KEY` | Mistral AI |
| `BRAVE_API_KEY` | Brave Search |
| `GITHUB_TOKEN` | GitHub (token, API_KEY değil) |
| `HUGGINGFACE_API_KEY` | HuggingFace normal token |
| `HUGGING_FACE_API_KEY` | HuggingFace write token |

**Aynı servisten iki farklı token:** Alt çizgi ile ayırt et.
Örn: `RUNWAY_API_KEY`, `RUNWAY_API_KEY_2` (iki farklı hesap).

**Not:** Serp ve Serper **farklı platformlardır.** Serp = serpapi.com,
Serper = serper.dev. İkisi ayrı secret olarak tutulur.

## Secure API Testing (bws → Live API)

Bitwarden SM'den API key alıp canlı bir servisi test etmek için **tek bir terminal() çağrısı** yeterlidir. Raw key shell değişkeninde kalır, sadece API yanıtı context'e girer.

```bash
# Desen: fetch → parse → use → return result
DG_KEY=*** bws secret list | python3 -c "filter by key name...")
echo "Key: ${DG_KEY:0:8}...${DG_KEY:-4}"
# API çağrısı burada — raw key asla stdout'a yazılmaz
```

Notlar:
- `ctx_execute` yerine `terminal()` kullan — sandbox'ta BWS_ACCESS_TOKEN yok
- Zincir security scanner'da HIGH işaretlenir — beklenen, onay gerekir
- Raw key'i asla `echo` ile yazdırma, sadece `${VAR:0:8}...${VAR:-4}` maskele
- Doğru secret'ı `s['key']=='TAM_ISIM'` ile filtrele

## Provider Görünürlük Endişesi

> Edel'in kuralı: **"secretları deepseek görmemeli"**

Primary model (DeepSeek/Claude) tüm tool call parameter'larını ve
terminal çıktılarını görür. Şu önlemler alınır:

1. **Terminal çıktısını maskele** — `bws secret list` çıktısını
   `python3 -c "import json;..."` ile filtrele, sadece `KEY → sk_****...****` göster
2. **Değerleri sohbette gösterme** — hiçbir raw credential değeri chat response'unda yer almaz
3. **Edel kendi ekler** — kullanıcı kendi secret'larını eklemek isterse,
   `bws secret create` komutunun şablonunu ver, kendisi çalıştırsın
4. **Golden config'de placeholder** — `golden_config.yaml`'de `api_key` değerleri `''` olarak saklanır

Detaylı açıklama: `sensitive-data-pipeline` skill'inde "Provider Visibility Concern" bölümü.

## Yapılandırma Referansı

```yaml
secrets:
  bitwarden:
    enabled: true
    access_token_env: BWS_ACCESS_TOKEN
    project_id: '...'  # hermes-api-keys projesi
    cache_ttl_seconds: 300
    override_existing: true      # Bitwarden > .env
    auto_install: true
    server_url: 'https://vault.bitwarden.com'
```

### override_existing Kritik

`override_existing: true` — Hermes önce `.env`'yi okur, sonra Bitwarden'dan
gelen değerler `.env'dekileri ezer. Bu sayede:
- `.env`'deki değerler fallback olarak kalır
- Bitwarden'daki güncel değerler her zaman kazanır
- Yeni bir secret eklendiğinde `.env`'yi düzenlemeye gerek kalmaz

## Doğrulama

```bash
# Durum kontrolü
hermes secrets bitwarden status

# Secret sayısını kontrol et
~/.hermes/bin/bws secret list PROJECT_ID | python3 -c "import json,sys; print(f'{len(json.load(sys.stdin))} secrets')"

# Aktif mi kontrol: config.yaml'de secrets.bitwarden.enabled: true olduğunu doğrula
```

## Golden Config ile Bağlantı

Bitwarden setup'ından SONRA `hermes-config-resilience` sistemini
güncellemek gerekir:
1. `python3 scripts/restore_config.py --sync` (yeni Bitwarden ayarlarını golden'a ekle)
2. Golden'daki `secrets.bitwarden.enabled` değerini `true` yap (elle düzenle)
3. `python3 scripts/restore_config.py --restore` (golden'ı config'e uygula)

## 🔑 BW (Password Manager) vs BWS (Secrets Manager) Ayrımı (30 Haz 2026)

Bu ortamda **iki ayrı Bitwarden sistemi** çalışır. Hangisini kullanacağını bilmek her şeydir.

| Özellik | BW (Password Manager) | BWS (Secrets Manager) |
|----------|----------------------|----------------------|
| **Ne saklar** | Web site şifreleri, login bilgileri | API key'leri, token'lar |
| **Binary** | `~/.hermes/bin/bw` (116MB) | `~/.hermes/bin/bws` (12MB) |
| **API Server** | `bw-serve` (port 8087) — otomatik başlar | Doğrudan `bws` CLI |
| **Veri tipi** | `username`, `password`, `uris`, `notes` | `key: value` çifti (env var formatı) |
| **Komut** | `curl http://localhost:8087/list/object/items` | `~/.hermes/bin/bws secret list` |
| **İçerik** | 8 öğe: APA, deepgram, github.com, Google-isimgorulsunn, google-pro, Soniox, Upwork, zoom.us | 37 secret (API key'ler) |
| **API key'ler** | ❌ Burada ARAMA | ✅ **Burada ara** — `GROQ_API_KEY`, `POLLINATIONS_API_KEY`, vb. |

**Kritik kural:** Bir API key veya token ararken **ÖNCE BWS'ye bak.** BWS'de yoksa **BW'de (Password Manager) ara** — bazı API key'ler (ör: Soniox, eski/değişmiş key'ler) BW'de login item'ı olarak saklanmış olabilir.

```bash
# ADIM 1: BWS'de ara (API key'ler)
bws secret list | python3 -c "import json,sys; [print(s['key']) for s in json.load(sys.stdin)]"

# ADIM 2: BWS'de yoksa BW'de ara (Password Manager)
# BW session al
BW_PASS=$(bws secret list | python3 -c "import json,sys; [print(s['value']) for s in json.load(sys.stdin) if s['key']=='BW_MASTER_PASSWORD']")
bw unlock "$BW_PASS" --raw
bw list items | python3 -c "
import json,sys
items = json.load(sys.stdin)
for item in items:
    name = item.get('name','')
    login = item.get('login',{})
    print(f'{name}: user={login.get(\"username\",\"\")}, pass={login.get(\"password\",\"\")[:10]}...')
"
```

**Pitfall:** BWS'de API key yok diye "key mevcut değil" deme — önce BW'de (Password Manager) kontrol et. Edel'in bu konuda düzeltmesi var: "Bitwarden secret'ı görme konusunda hala sıkıntılısın. Bws girip baksana."

**Neden karışır:** Eskiden tüm secret'lar `.env` dosyasında düz metindi. BWS geçişi yapıldı ama hem BW Password Manager (`bw-serve`) hem BWS (`bws`) aynı anda çalışır. `bw-serve` port 8087'de otomatik başlar ve zaten unlocked durumdadır — bu yüzden "Bitwarden" deyince akla ilk o gelir. Oysa API key'lerin gerçek sahibi BWS'dir.

### BWS'ye Erişim

```bash
# Binary yolu (PATH'te değil!)
BWS=~/.hermes/bin/bws

# Tüm secret'ları listele (değerleri maskeli)
$BWS secret list | python3 -c "
import json, sys
data = json.load(sys.stdin)
for s in sorted(data, key=lambda x: x['key']):
    v = s['value']
    m = v[:6] + '...' + v[-4:] if len(v) > 12 else '****'
    print(f'  {s[\"key\"]:<35} {m}')
print(f'Total: {len(data)} secrets')
"

# Tek secret'ı ID ile al
$BWS secret get <SECRET_ID>
```

## `bw serve` REST API — Doğrudan Erişim (bw CLI olmadan)

`bw serve` (port 8087) systemd servisi olarak otomatik başlar ve unlocked durumdadır.
`bw` CLI PATH'te olmasa bile API üzerinden vault yönetilebilir.

**Endpoint'ler (127.0.0.1:8087, v2026.6.2):**
| Endpoint | Method | Kullanım |
|----------|--------|---------|
| `/status` | GET | Vault durumu: "unlocked" / "locked" |
| `/sync` | POST | Cache yenileme (çalışır) |
| `/unlock` | POST | Vault açma (`{"password":"..."}` body ile) |
| `/lock` | POST | Vault kilitleme |
| `/generate` | GET | Parola üretme |

**⚠️ ÖNEMLİ (11 Tem 2026):** `/list/object/items` endpoint'i test edilmiş ve **ÇALIŞTIĞI DOĞRULANMIŞTIR** (daha önce 404 döndüğü belirtilmişti ancak güncel `bw-serve`'de çalışıyor). Item'ları listelemek için REST API doğrudan kullanılabilir — CLI'a gerek yoktur. Eğer çalışmazsa, önce `/status` ile serve'ün "unlocked" olduğunu kontrol et, ardından tekrar dene.

**Credential çekme workflow'u (BWS → BW CLI):**
`bw serve` API'si item listeleme endpoint'i sunmadığı için, credential'lar `bw` CLI ile BWS master password yardımıyla alınır:

```bash
# 1. BWS'den master password'ü al
export BW_PW=$(~/.hermes/bin/bws secret list | python3 -c "
import json,sys
data = json.load(sys.stdin)
for s in data:
    if s['key'] == 'BW_MASTER_PASSWORD':
        print(s['value'], end='')
")

# 2. CLI'ı unlock et (--passwordenv ile, şifre stdout'a yazılmaz)
SESSION_KEY=$(~/.hermes/bin/bw unlock --passwordenv BW_PW --raw 2>&1)
unset BW_PW

# 3. Session ile item'ları listele
BW_SESSION="$SESSION_KEY" ~/.hermes/bin/bw list items --search "ARA"
```

**Pitfall — Session key çalışmazsa:** `bw unlock` çıktısındaki session key bazen CLI tarafından kabul edilmez. Bu durumda alternatif olarak önce `bw serve`'ün `/unlock` endpoint'ine password'ü POST et (vault'u açar), ardından CLI'ı `--session` ile kullan. Veya tamamen `bw` CLI'ın foreground modunda `--passwordfile` ile unlock dene.

**Pitfall — `bw: command not found`:** Binary `/home/ubuntu/.hermes/bin/bw` yolunda. PATH'te yoksa CLI çalışmaz. Çözüm: REST API kullan (serve zaten çalışıyor).

**Pitfall — `bw serve`'ün çalıştığını doğrulama:** `bw: command not found` alınca hemen "bw yok" deme. `ps aux | grep 'bw serve'` ile arka planda serve process'ini kontrol et. Eğer çalışıyorsa (port 8087), `curl -s http://127.0.0.1:8087/status` ile "unlocked" olduğunu doğrula ve REST API'yi direkt kullan — CLI'a hiç ihtiyaç yok. CLI gerekliyse `export PATH="$HOME/.hermes/bin:$PATH"`.

**Pitfall — Stale cache:** Yeni eklenen öğe listede yoksa önce `/sync` endpoint'ine POST at, ardından tekrar listele.

## Sorun Giderme

| Belirti | Çözüm |
|---------|-------|
| `bw: command not found` | `bw serve` çalışıyorsa REST API kullan. CLI gerekliyse `export PATH="$HOME/.hermes/bin:$PATH"` |
| `bws: not found` | `hermes secrets bitwarden install` veya elle indir |
| `bws` binary var ama `command not found` | PATH'e `/home/ubuntu/.hermes/bin` ekle: `export PATH="$PATH:/home/ubuntu/.hermes/bin"` — Hermes Docker container'ında PATH otomatik eklenir ama WSL/local shell'de eklenmez |
| "Doesn't contain a decryption key" | Token formatı bozuk. `--access-token` flag dene, env var yerine |
| "device_error" | Device bilgilerini BODY'de gönder, header'da değil |
| "version_header_missing" | `Bitwarden-Client-Version: 2025.1.0` header'ı ekle |
| "401 Unauthorized" | Token geçersiz, yenile |
| 429 rate limit | Batch arası 3sn bekle |
| Proje bulunamadı | Org'da Secrets Manager aktif değil |

## Referanslar
