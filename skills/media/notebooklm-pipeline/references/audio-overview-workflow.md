# Audio Overview (Podcast) Oluşturma Workflow'u

Transkript veya kaynak materyalden NotebookLM Studio Audio Overview (podcast) oluşturma.

## Kullanım Senaryosu

Edel bir seminere katılır → kaydederiz → Groq Whisper ile transkript çıkarırız → transkripti NotebookLM'e yükleriz → Audio Overview oluştururuz → Edel dinler.

## Adımlar

### 1. Auth Kontrolü

```bash
nlm login --check
# ✓ Authentication valid!
# Account: isimgorulsunn@gmail.com
```

### 2. Notebook Oluştur

Her seminer için ayrı notebook. İsim formatı: `"KONU - Seminer Adı (TARİH)"`

```bash
nlm notebook create "APA - Mentoring as Networking (30 Haz 2026)" --json
# {"notebook_id": "f24a58e3-...", "title": "APA - Mentoring as Networking (30 Haz 2026)"}
```

Notebook ID not edilir — sonraki adımlarda kullanılır.

### 3. Kaynak Ekle

Üç yöntemle kaynak eklenebilir:

**A) Yerel dosya yükleme (`--file`):**

```bash
nlm source add <NOTEBOOK_ID> \
  --file /home/ubuntu/recordings/transkript_apa.md \
  --title "APA Mentoring as Networking Transkripti" \
  --wait
# ✓ Added source: APA Mentoring as Networking Transkripti (ready)
# Source ID: ac55032c-...
```

- `--wait`: İşleme tamamlanana kadar bekler (varsayılan timeout 600s)
- `--title`: Kaynağa anlamlı bir isim ver
- Desteklenen dosya türleri: PDF, TXT, MD, DOCX, MP3, MP4, WAV, vb.

**B) Web sayfası URL'si (`--url`):**

```bash
nlm source add <NOTEBOOK_ID> \
  --url "https://ornek.com/kaynak-sayfasi" \
  --title "Kaynak Başlığı" \
  --wait
# ✓ Added source: Başlık (ready)
```

- NotebookLM sayfanın içeriğini çeker ve indeksler
- Tracking/redirect linkleri de çalışır (APA click tracking üzerinden yönlenen sayfalar gibi)
- `--wait` ile işlemenin tamamlanmasını bekle

**C) YouTube videosu (`--youtube`):**

```bash
nlm source add <NOTEBOOK_ID> \
  --youtube "https://youtu.be/VIDEO_ID"
```

### 4. Audio Overview (Podcast) Oluştur

```bash
nlm audio create <NOTEBOOK_ID> \
  --format deep_dive \
  --length long \
  --confirm
# ✓ Audio generation started
# Artifact ID: 48085236-...
```

**Format seçenekleri:**
| Değer | Açıklama |
|-------|---------|
| `deep_dive` | Derinlemesine analiz, iki sunucu sohbeti (varsayılan) |
| `brief` | Kısa özet |
| `critique` | Eleştirel bakış |
| `debate` | Tartışma formatı |

**Length seçenekleri:** `short`, `default`, `long`

**Dil kontrolü:** `--language tr` ile Türkçe audiobook dene. Transkript İngilizce ise dil parametresi verme (varsayılan İngilizce).

### 5. İlerleme Takibi (Polling YAPMA — Cron Kullan)

Edel sürekli polling mesajı istemez. Bunun yerine:

1. Audio generation başlat
2. 10 dakika sonra kontrol edecek **tek seferlik cron job** kur (repeat=1)
3. Cron job:
   - `nlm studio status <NOTEBOOK_ID>` ile kontrol et
   - Hazırsa: `nlm download <ARTIFACT_ID>` ile indir
   - Telegram'a MEDIA ile gönder
   - Hazır değilse: kendini yeniden 10dk'ya planla

```bash
nlm studio status f24a58e3-a613-468d-825f-ef8ac9579d98
# Artifact ID: 48085236-... | Status: completed
```

### 6. İndirme

```bash
nlm download <ARTIFACT_ID>
# Audio dosyasını indirir (genellikle .mp3 veya .wav)
```

## Background + Notify Pattern

Audio generation 5-15 dk sürebilir. Edel sürekli polling mesajı istemez (SIN #10).

**DOĞRU YÖNTEM:** `terminal(background=true, notify_on_complete=true)` ile çalıştır.

```python
# Agent şöyle çağırır (direkt terminal tool):
terminal(
  command="~/.local/bin/nlm audio create NOTEBOOK_ID --format deep_dive --confirm -y",
  background=True,
  notify_on_complete=True,
  timeout=300
)
# → session_id döner, işlem bitince bildirim gelir
```

Bu pattern:
- İşlem başlar başlamaz döner (bekleme yok)
- Aradaki her "hâlâ işleniyor" mesajını engeller
- Bitince tek bildirim: "Session completed"
- Cron job'a gerek kalmaz (ama çok uzun sürecekse cron da kullanılabilir)

### 7. Edel'e İletme

Audio hazır olduğunda Telegram'a MEDIA yoluyla gönder:
```
MEDIA:/path/to/downloaded/audio.mp3
```

## Bilinen Çalışma Durumu

| Adım | Durum | Not |
|------|-------|-----|
| `nlm login --check` | ✅ Çalışıyor | Auth sürekli valid (Chrome profili) |
| `nlm notebook create` | ✅ Çalışıyor | --json ile ID al |
| `nlm source add --file` | ✅ Çalışıyor | --wait ile bekle |
| `nlm audio create` | ✅ Çalışıyor | deep_dive + long önerilen |
| `nlm studio status` | ✅ Çalışıyor | Polling yerine cron |
| `nlm download` | ✅ Çalışıyor | Artifact ID gerekli |

## Pitfall'lar

- **Audio generation süresi:** 5-15 dakika arası. Hemen bitmez, cron ile kontrol et.
- **Session timeout:** Uzun beklemelerde cron job'ın kendini yeniden planlaması gerekebilir (30dk'ya kadar).
- **Dil seçimi:** Transkript İngilizce ise `--language tr` koyma — NotebookLM karışık dilde audio üretebilir.
- **--confirm bayrağı:** Onay sorusunu atlar, headless ortamda gerekli.
- **"unknown" status limbo (MCP):** `mcp_notebooklm_studio_create(artifact_type="audio")` bazen hemen "status: unknown" (not "in_progress") döner ve artifact saatlerce bu durumda kalır. Bu, generation'ın hiç başlamadığı anlamına gelir — ne iptal ne tamamlanma. **Doğru müdahale:** (1) Polling yapma — status değişmez. (2) Download deneme — URL yok, boş döner. (3) Aynı artifact ID ile yeniden create çağırma — rate-limit'e takılırsın. (4) Bir sonraki cron çevriminde auth tazele + yeni artifact ID ile yeniden dene. (5) Art arda 2 cron çevrimi "unknown" alırsan, pipeline'a "⚠️ NBLM audio: persistent unknown status" notu ekle ve podcast'i atla.
