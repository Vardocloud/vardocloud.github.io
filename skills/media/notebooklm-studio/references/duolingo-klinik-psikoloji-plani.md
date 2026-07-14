# Klinik Psikoloji Duolingo-Tarzı Çalışma Planı (1 Temmuz 2026)

**Notebook:** BDT (ID: a4fe729d-c561-4238-9bea-81bea8e3dcbc) — 256 kaynak  
**Plan:** 10 gün × 2 oturum/gün = 20 oturum  
**Başlangıç:** 2 Temmuz 2026 Perşembe — **Bitiş:** 11 Temmuz 2026 Cumartesi  
**Saatler:** Öğlen 12:00-12:10, Akşam 18:00-18:10  
**Bildirim:** Etkinlikten 30dk ve 2 saat önce popup  

## Studio Artifact'leri

Her oturum için NotebookLM Studio'da oluşturulan artifact'ler:

### Gün 1 — 2 Tem Perşembe — YAB Tanı Kriterleri
| Oturum | Tür | Artifact ID | Açıklama |
|--------|-----|-------------|----------|
| 12:00 | Briefing Doc | 98b0f6e8-05a4-40cf-a5f9-c017aaa1c07e | YAB DSM-5 6 kriter |
| 18:00 | Quiz | 5253911a-de13-4b36-99ba-72a2de4da29f | 5 soru, kriter sınama |

### Gün 2 — 3 Tem Cuma — YAB Vaka
| Oturum | Tür | Artifact ID | Açıklama |
|--------|-----|-------------|----------|
| 12:00 | Flashcards | 94c84536-8217-4136-8bc3-ba90186daa31 | YAB vaka örnekleri |
| 18:00 | Infographic | 96bbc928-8eec-42d0-9359-ddd983dc5e8e | YAB görsel özet |

### Gün 3 — 4 Tem Cmt — Panik: Atak
| Oturum | Tür | Artifact ID | Açıklama |
|--------|-----|-------------|----------|
| 12:00 | Briefing Doc | c72336ef-e0b8-4f0d-98c7-9c01ed4b11e0 | Panik atak kriterleri (audio rate limit → briefing ile değiştirildi) |
| 18:00 | Quiz | b03d0f7d-c13c-472c-bcf0-caa78d8b8881 | Panik semptom/test |

### Gün 4 — 5 Tem Paz — Panik: Atak vs Bozukluk
| Oturum | Tür | Artifact ID | Açıklama |
|--------|-----|-------------|----------|
| 12:00 | Briefing Doc | c72336ef-e0b8-4f0d-98c7-9c01ed4b11e0 | Atak vs bozukluk ayırıcı tanı |
| 18:00 | Quiz | b03d0f7d | Panik vaka soruları |

### Gün 5 — 6 Tem Pzt — YAB + Panik Karma
| Oturum | Tür | Artifact ID | Açıklama |
|--------|-----|-------------|----------|
| 12:00 | Mind Map | f217a2a0-86e4-4897-ab9b-792cff552c9b | Karşılaştırma |
| 18:00 | Quiz | 3e6ee269-9f88-4da9-a242-b672c6231f31 | 10 karma soru |

### Gün 6 — 7 Tem Sal — BDT Bilişsel Model
| Oturum | Tür | Artifact ID | Açıklama |
|--------|-----|-------------|----------|
| 12:00 | Slide Deck | d3a467d3-8e1a-4a53-8d38-f2d7c640cb65 | BDT model şeması |
| 18:00 | Flashcards | 284599a6-6815-4c6d-8d2a-119ea9038d8e | BDT kavram kartları |

### Gün 7 — 8 Tem Çar — BDT Vaka
| Oturum | Tür | Artifact ID | Açıklama |
|--------|-----|-------------|----------|
| 12:00 | Audio (mevcut) | 56979d94-ac64-490c-880f-fae4d9568588 | Hakan Türkçapar BDT sesli özet |
| 18:00 | Quiz | b2db942e-7735-49ea-a63c-d0b220636e99 | BDT vaka soruları |

### Gün 8 — 9 Tem Per — Depresyon DSM
| Oturum | Tür | Artifact ID | Açıklama |
|--------|-----|-------------|----------|
| 12:00 | Briefing Doc | 8da9e58b-3506-451a-9708-2d929de027f3 | 9 kriter |
| 18:00 | Flashcards | 9a097017-cad1-4cb2-9d0e-a10edac4a73e | Semptom kartları |

### Gün 9 — 10 Tem Cum — Depresyon Vaka
| Oturum | Tür | Artifact ID | Açıklama |
|--------|-----|-------------|----------|
| 12:00 | Infographic | 77cb9cfc-fc56-4ecf-af4a-604a65150021 | Şiddet ayrımı |
| 18:00 | Quiz | a745eea9-719e-4706-aa56-33e2b3b7d75e | Depresyon vakaları |

### Gün 10 — 11 Tem Cmt — Full Tekrar
| Oturum | Tür | Artifact ID | Açıklama |
|--------|-----|-------------|----------|
| 12:00 | Audio/Özet | — | Mevcut audio (217a473f) veya Full Karma Quiz |
| 18:00 | Quiz | 93407a68-26af-495c-a3b6-d0789970b310 | 20 soru kapsamlı |

## Çalışma Materyali Oluşturma Komutları (Referans)

```bash
# YAB Briefing Doc
nlm create report a4fe729d... -f "Briefing Doc" \
  -s "2560aec8...,09a8bc05...,154c1b15...,9ebe0886..." -y

# Quiz
nlm create quiz a4fe729d... -c 5 -d 3 \
  -s "2560aec8...,09a8bc05...,9ebe0886..." -y

# Flashcards (sadece PDF kaynaklarıyla!)
nlm create flashcards a4fe729d... -d easy \
  -s "2560aec8...,9ebe0886..." -y

# Infographic
nlm create infographic a4fe729d... -o landscape -d concise \
  -s "2560aec8...,09a8bc05..." -y

# Slide Deck
nlm create slides a4fe729d... -f presenter_slides -l short \
  -s "c3cad24b...,2560aec8..." -y

# Mind Map
nlm create mindmap a4fe729d... -t "Başlık" \
  -s "id1,id2,..." -y
```

## Google Calendar Oluşturma (Python)

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN = '/home/ubuntu/.hermes/google_token.json'
creds = Credentials.from_authorized_user_file(
    TOKEN, ['https://www.googleapis.com/auth/calendar'])
service = build('calendar', 'v3', credentials=creds)

# Token root sahipliğindeyse google_token_ubuntu.json'ı kullan
# cp /home/ubuntu/.hermes/google_token_ubuntu.json /home/ubuntu/.hermes/google_token.json

for start_time, summary, desc in sessions:
    dt = datetime.fromisoformat(start_time)
    end_dt = (dt + timedelta(minutes=10)).isoformat() + '+03:00'
    event = {
        'summary': summary,
        'description': desc,
        'start': {'dateTime': start_time, 'timeZone': 'Europe/Istanbul'},
        'end': {'dateTime': end_dt, 'timeZone': 'Europe/Istanbul'},
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 120},
                {'method': 'popup', 'minutes': 30}
            ]
        }
    }
    service.events().insert(calendarId='primary', body=event).execute()
```

## Edel'in Tercihleri (Güncellendi — 1 Temmuz 2026)

- **"Kolay çalışma"** = sıfır üretim, sadece tüketim, 10 dk max
- **Duolingo benchmark:** 10 dakika, net başlangıç, bildirimle hatırlatma
- **Mevcut notebook kaynaklarını kullan** — sıfırdan yükleme yapma
- **10 gün × 2 oturum** = öğlen ana konu + akşam pekiştirme
- **Audio rate limit** = sık karşılaşılan sorun. Mevcut audioları kullan veya briefing ile değiştir
- **Not:** Çalışma planı oluştururken önce Edel'in "kolay" tanımını anla. "Şu adımları yap" tarzı direktifler hâlâ kolay değil — Studio'nun otomatik üretmesi gerekiyor.

## Karşılaşılan Hatalar

| Hata | Sebep | Çözüm |
|------|-------|-------|
| `INVALID_ARGUMENT` | word_doc/uploaded_file source flashcard/audio'da | PDF source kullan |
| `RESOURCE_EXHAUSTED` | Audio rate limit (3+/session) | 5dk bekle veya mevcut audio kullan |
| Authentication expired | ~20dk oturum süresi | `python3 ~/.hermes/scripts/nb_keepalive.py` |
| Token Permission denied | google_token.json root owned | `google_token_ubuntu.json` kullan veya kopyala |
