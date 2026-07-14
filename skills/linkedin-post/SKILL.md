---
name: linkedin
description: "LinkedIn post otomasyonu — psikoloji içerik üretimi. Firecrawl + Gemini 3.1 Flash Lite pipeline. Hakan Türkçapar üslubunda blog yazıları. Duplicate kontrolü (JSON + NotebookLM RAG)."
version: 1.0.0
metadata:
  hermes:
    tags: [linkedin, post, psikoloji, blog, otomasyon, content]
    category: productivity
---

# LinkedIn Post Otomasyonu

## 🔑 ZORUNLU: Token Kontrol Adımı (Her İşlem Öncesi)

**ÖNCE token durumunu kontrol et:**

```bash
cd ~/.hermes/linkedin-poster && python3 -c "
from linkedin_client import LinkedInClient
import os, json, time
client = LinkedInClient()
if os.path.exists(client.token_path):
    with open(client.token_path) as f:
        data = json.load(f)
    remaining = data.get('expires_in', 0) - (time.time() - data.get('created_at', 0))
    print(f'Token: {\"✅\" if remaining > 0 else \"❌\"} ({remaining/86400:.1f} gün kaldı)')
else:
    print('Token: ❌ Dosya yok')
```

**Karar:**
- `expires_in_days > 7` → ✅ **Token geçerli, OAuth gerekmez.** Direkt post akışına geç.
- `expires_in_days <= 7` → ⚠️ **Token yakında bitecek.** Refresh dene, olmazsa OAuth başlat.
- Token yok / hata → 🔄 **OAuth akışı başlat** (auth URL + callback server).

**Önemli:** Token dosyası `~/.hermes/secrets/linkedin_token.json` içinde, `linkedin-poster/` altında değil!

## Ne Zaman Kullanılır (Trigger Conditions)

Bu skill aşağıdaki durumlarda otomatik yüklenir:

1. Kullanıcı "post yaz", "LinkedIn post", "içerik yaz" dediğinde
2. Kullanıcı bir URL verip "bunu post yap" dediğinde
3. Kullanıcı "haber kaynağı ekle", "site ekle" dediğinde
4. Kullanıcı "haber kaynaklarını göster", "kaynakları listele" dediğinde
5. Cron job tetiklendiğinde (09:00, 20:30)

## Komut Adları

- `/linkedin` — Post yaz (ana komut)
- `/kaynak` — Kaynak ekle veya listele
- `/gecmis` — Son postları göster
- `/kontrol "konu"` — Duplicate kontrolü yap
- `/istatistik` — Post istatistiklerini göster
- `/linkedin-durum` — LinkedIn OAuth durumunu kontrol et

## Temel Bilgiler

| Özellik | Değer |
|---------|-------|
| **İçerik Modeli** | Gemini 3.1 Flash Lite (Pollinations) |
| **Araştırma** | Firecrawl (search + scrape) |
| **Duplicate Kontrolü** | JSON + NotebookLM RAG |
| **Üslup** | Hakan Türkçapar blog yazıları |
| **Post Limiti** | Max 3000 karakter, 5 hashtag |
| **Zamanlama** | 09:00 + 20:30 (cron) |
| **Platform** | Kişisel LinkedIn hesabı |

## Dosya Konumları

```
~/.hermes/skills/linkedin-post/
├── SKILL.md                    # Bu dosya
├── references/
│   ├── turkcapar_style.md      # Üslup referansı
│   ├── usage-guide.md          # Pipeline kullanım kılavuzu
│   └── api-capabilities.md     # API yetenekleri ve kısıtlamalar (profil okuma/yazma)
├── news_sources.yaml           # Haber kaynakları
└── post_history.json           # Post geçmişi

~/.hermes/linkedin-poster/
├── linkedin_client.py          # LinkedIn API
├── content_pipeline.py         # Firecrawl + Gemini
├── duplicate_checker.py        # Duplicate kontrol
└── news_manager.py             # Haber kaynağı CRUD
```

## Komutlar

### 1. Post Yaz (`/linkedin`)

```
/linkedin
"Bugün psikoloji postu yaz"
"Bu linki post yap: https://..."
```

**Akış:**
1. `content_pipeline.search_and_write()` — Otomatik konu araştırması
2. `duplicate_checker.check()` — Duplicate kontrolü
3. Kullanıcıya onay gönder (clarify)
4. Onaylanırsa → LinkedIn paylaş + geçmişe ekle

### 2. Kaynak Yönetimi (`/kaynak`)

```
/kaynak                          → Tüm kaynakları listeler
/kaynak https://example.com      → Yeni kaynak ekler
"Şu siteyi ekle: https://..."    → Yeni kaynak ekler
```

**Akış:**
- Listeleme: `news_manager.list_sources()` → Formatlı çıktı
- Ekleme: URL'yi parse et → `news_manager.add_source()` → Onay mesajı

### 3. Post Geçmişi (`/gecmis`)

```
/gecmis                          → Son 10 postu listeler
"Son postları göster"            → Son 10 postu listeler
```

**Akış:**
1. `duplicate_checker.get_history(10)` — Son 10 postu al
2. Formatlı çıktı: tarih, konu, kaynak URL

### 4. Duplicate Kontrolü (`/kontrol`)

```
/kontrol "sınav anksiyetesi"     → Konu için duplicate kontrolü
"Bu konu yazılmış mı?"           → Duplicate kontrolü
```

**Akış:**
1. `duplicate_checker.check(topic)` — Duplicate kontrolü yap
2. Sonuç: ✅ yazılabilir veya ❌ atlanır (nedeni ile)

### 5. İstatistikler (`/istatistik`)

```
/istatistik                      → Post istatistiklerini göster
"Kaç post yazıldı?"              → Post istatistiklerini göster
```

**Akış:**
1. `duplicate_checker.get_stats()` — İstatistikleri al
2. Formatlı çıktı: toplam, bu ay, kategoriler, son post tarihi

### 6. LinkedIn Durumu (`/linkedin-durum`)

```
/linkedin-durum                  → OAuth ve bağlantı durumu
"LinkedIn bağlı mı?"             → OAuth ve bağlantı durumu
```

**Akış:**
1. `linkedin_client.get_status()` — Durum bilgisini al
2. Formatlı çıktı: authenticated, token_path, redirect_uri

## Duplicate Kontrol Mantiği

```
Yeni konu geldi
  ↓
JSON kontrolü (hızlı)
  ├─ Aynı topic + 30 gün içinde → ATLA
  ├─ Aynı topic + 30 gün geçmiş → YENİDEN YAZ
  └─ Farklı topic → NotebookLM kontrolü
  ↓
NotebookLM RAG (akıllı)
  ├─ Semantic benzerlik > %70 + 30 gün → ATLA
  ├─ Semantic benzerlik ≤ %70 → YAZ (farklı açı)
  └─ Bulunamadı → YAZ
  ↓
İçerik karşılaştırma (key_points)
  ├─ Benzerlik > %70 → ATLA
  └─ Benzerlik ≤ %70 → YAZ
```

## Cron Job Akışı

### 09:00 Sabah Postu

```
1. Firecrawl search → Güncel haberler
2. Duplicate kontrolü → JSON + NotebookLM
3. Gemini yazım + inceleme
4. Telegram'a gönder → clarify ile onay
5. Edel cevap verene kadar bekle
6. Onay → LinkedIn paylaş + arşivle
7. 20:30'a kadar cevap gelmezse → iptal
```

### 20:30 Akşam Postu

```
1-6: Aynı akış
7. Ertesi gün 09:00'a kadar cevap gelmezse → iptal
```

## execute_code Pipeline

```python
from hermes_tools import terminal
import httpx, json

POLLINATIONS_KEY = "sk_8591wAiXFI5X417Rboh51kLFhpToSqq9"
FIRECRAWL_KEY = "fc-64e6e5d126a84c9a8f856253e86d4eec"
BASE_URL = "https://gen.pollinations.ai/v1/chat/completions"

# 1. ARAŞTIRMA (Firecrawl)
search_response = httpx.post(
    "https://api.firecrawl.dev/v2/search",
    headers={"Authorization": f"Bearer {FIRECRAWL_KEY}"},
    json={
        "query": "güncel psikoloji araştırma haber 2026",
        "limit": 5,
        "scrape_options": {"formats": ["markdown"]}
    },
    timeout=30.0
)
results = search_response.json()["data"]["web"]

# 2. İÇERİK YAZIMI (Gemini)
source_text = "\n\n".join([
    f"Kaynak: {r['title']}\nURL: {r['url']}\nİçerik: {r.get('markdown', '')[:3000]}"
    for r in results[:3]
])

write_response = httpx.post(BASE_URL,
    headers={"Authorization": f"Bearer {POLLINATIONS_KEY}"},
    json={
        "model": "gemini-flash-lite-3.1",
        "messages": [
            {"role": "system", "content": "Üslup prompt buraya"},
            {"role": "user", "content": f"Bu kaynaklardan LinkedIn postu yaz:\n\n{source_text}"}
        ],
        "max_tokens": 1500
    },
    timeout=60.0
)
post_draft = write_response.json()["choices"][0]["message"]["content"]
print(post_draft)
```

## Onay Akışı

```
Gemini post taslağı üretir
  ↓
Vanitas clarify() çağırır
  ↓
┌─────────────────────────────────────┐
│ "📝 Post taslağı hazır:"           │
│ [İçerik]                            │
│                                     │
│ 1 ✅ Onayla ve paylaş               │
│ 2 ❌ İptal                          │
│ 3 ✏️ Revize iste                    │
│ 4 🔄 Yeniden üret                   │
└─────────────────────────────────────┘
  ↓
Edel "1" yazar → LinkedIn paylaşılır
```

## Hata Yönetimi

| Durum | Aksiyon |
|-------|---------|
| Firecrawl hatası | Farklı kaynak dene |
| Gemini hatası | Tekrar dene (max 2) |
| NotebookLM hatası | Sadece JSON kontrolü ile devam et |
| LinkedIn API hatası | Hata detayını göster |
| Duplicate tespit edildi | Farklı haber seç |

## Dosya Yapısı (Güncel)

```
~/.hermes/skills/linkedin-post/
├── SKILL.md                    # Bu dosya
├── references/
│   ├── turkcapar_style.md      # Üslup referansı
│   └── usage-guide.md          # Pipeline kullanım kılavuzu ⚠️ OKUMA
├── news_sources.yaml           # Haber kaynakları
└── post_history.json           # Post geçmişi

~/.hermes/linkedin-poster/
├── linkedin_client.py          # LinkedIn API
├── content_pipeline.py         # Firecrawl + Gemini
├── duplicate_checker.py        # Duplicate kontrol
└── news_manager.py            # Haber kaynağı CRUD
```

## Önemli Notlar

- **Profil düzenleme:** About bölümü güncellemesi mevcut token ile yapılamaz. Detaylar: `references/api-capabilities.md`
- **Üslup:** Tüm postlar Hakan Türkçapar üslubunda, edilgen/üçüncü şahıs dilde yazılır
- **Etik:** Bilimsel doğruluk, mahremiyet, zarar vermeme, kanıta dayalı
- **Şahıs:** Birinci tekil şahıs ("ben", "gördüğüm", "danışanlarım") KULLANILMAZ
- **Hashtag:** Her post 5 hashtag içerir
- **Emoji:** Postlarda emoji kullanılmaz
- **Kaynak:** Link zorunlu değil; verilecekse en alt satırda
- **Telif:** Doğrudan alıntı yapılmaz, kendi kelimelerle yazılır
- **Duplicate:** Aynı konu 30 gün içinde tekrar yazılmaz
- **Arşiv:** Tüm postlar tarihli olarak arşivlenir

---

*Skill version: 1.0.0*
*Created: 2026-05-21*
*Pipeline: Firecrawl + Gemini 3.1 Flash Lite*
