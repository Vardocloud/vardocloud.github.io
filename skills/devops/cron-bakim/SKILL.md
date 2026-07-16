---
name: cron-bakim
description: "Hermes cron job'larının toplu bakım ve onarım prosedürü — 30+ job'ı tarama, hata teşhisi, script düzeltme, pause/resume kararları."
version: 2.5.0
metadata:
  hermes:
    tags: [cron, maintenance, bakim, server, hermes, job-management]
    category: devops
---

# Cron Bakım Prosedürü — Toplu Sağlık Taraması

## Tetikleyici
Edel "tüm cronların bakım onarımını yap" dediğinde, cron sağlık monitörü hata bildirdiğinde, veya Edel "bunu ben bildiriyorum, sen fark etmiyorsun" dediğinde.

## ÖNEMLİ: Proaktif Monitoring (Edel'in beklentisi)

Edel cron hatalarını kendisi bildirmek zorunda kalmamalı. Aşağıdaki sistem otomatik tespit yapar:

### Otomatik Cron Sağlık Monitörü (v2 — 1 Temmuz 2026)
- **Script:** `~/.hermes/scripts/cron-health-check.py` (no_agent, v2)
- **Schedule:** Her 4 saatte bir (cron job ID: `917fd839a746`)
- **Çalışma prensibi:** `~/.hermes/cron/jobs.json` dosyasını okur, `last_status`, `last_error`, `last_delivery_error` alanlarını kontrol eder
- **Sessiz mod:** Sorun yoksa `[SILENT]` çıktısı verir
- **Aktif mod:** Sorun varsa Home kanala (topic 12) düzenli rapor gönderir

**v2 Yenilikleri:**
- **Deduplication:** Aynı hata iki rapor üst üste görünürse "🔁 Tekrarlanan" kategorisine düşer. State dosyası: `~/.hermes/data/cron_health_state.json` — her hatanın ilk 500 karakterlik hash'ini tutar.
- **Zaman filtresi:** 24 saatten eski hatalar otomatik "geçmiş" olarak işaretlenir, öncelik sırasında alta düşer.
- **Traceback kısaltma:** Ham stderr/stdout çıktısı yerine sadece anlamlı hata satırı (son `PermissionError`, `RuntimeError`, `Script timed out` vb.) gösterilir. Traceback, File satırları, import satırları otomatik atlanır.
- **Paused job'lar:** Hiç gösterilmez (bilinçli durdurma, gürültü yapmaz).
- **Temiz format:** Emoji + job adı + kısa hata + zaman etiketi. Her hata tek satır, alt satırda kısa açıklama.

**Tespit ettiği sorun tipleri:**
  - `last_status = "error"` olan job'lar
  - `last_delivery_error` dolu olan job'lar
  - 24 saatten eski hatalar "geçmiş" olarak işaretlenir

### Agent'ın Sorumluluğu
Edel bir cron hatası bildirdiğinde:
1. Önce monitörün tespit edip etmediğini kontrol etme — **monitör bağımsız çalışır, her oturumda cronjob(action='list') ile güncel durumu al**
2. Hatayı teşhis et ve düzelt (aşağıdaki akışı izle)
3. Monitörün bir sonraki çalışmasında hatanın düzeldiğini teyit etmesini bekleme — hemen bildir
4. Yeni bir hata türü keşfettiysen, monitör script'ine ekle veya bu skill'in pitfall'larını güncelle

## Akış

### 1. Envanter Çıkar
```bash
cronjob(action='list')
```
Tüm job'ları listele. 30+ job olabilir — tek tek incele.

Her job için şu alanlara bak:
- `last_status`: ok mi, error mu?
- `state`: scheduled mi, paused mi?
- `last_run_at`: Ne zaman çalıştı? Çok eskiyse sorun var.
- `enabled`: Aktif mi?
- `last_delivery_error`: Teslimat hatası var mı?
- `no_agent`: Script tabanlı mı, LLM-driven mı?

### 2. Hata Verenleri Sınıflandır

**Hata Türleri ve İlk Tepki:**

| Hata | Kök Neden | Aksiyon |
|------|-----------|---------|
| `script failed` (exit code ≠ 0) | Dosya yolu, env var, binary eksik | Script'in içini oku, hata satırını bul |
| `LLM-driven job error` | Model/provider, tool limit, context overflow, proxy/auth sorunu | Prompt + model uyumunu kontrol et. **Pollinations kaynaklıysa** önce cron output dosyasını oku (`~/.hermes/cron/output/<job_id>/`), `## Error` bölümündeki hatayı tespit et: |
| `403 Rate limit exceeded (LiteRouter)` | Provider LiteRouter 7sn rate limit — job'lar arası yeterli boşluk yok | Provider'ı değiştir: `LiteRouter` → `opencode-zen` (deepseek-v4-flash-free). Diğer job'lar opencode-zen'de sorunsuz çalışır. |
| `LiteRouter rate limit (mixed job)` | **Script tabanlı cron + LLM provider.** Script (`pm_master_scan.py` gibi) kendi API çağrılarını yapıp 429 alır. Retry'ler bittikten sonra hatalı çıktı → agent hatası → last_status=error | **Kök neden ayrımı:** Script'in kendi API 429'u mu? Yoksa provider'ın rate limit'i mi? Kontrol: script'i elle çalıştır (`timeout 60 python3 script.py`). Script başarılıysa sorun provider'dadır → provider değiştir. Script 429 alıyorsa API'nin kendi limitidir → retry sayısını artır veya schedule'ı seyrelt. |
| `RuntimeError: HTTP 429: Weekly usage limit reached` | OpenCode model kotası doldu (deepseek-v4-flash-free vb. haftalık limit) | Bekle — ertesi gün kendiliğinden düzelir. **Kalıcı çözüm:** Script tabanlı işse cron'u `no_agent: true` yap, LLM katmanını kaldır. Modeli limitsiz bir provider'a (LiteRouter llama-3.3-70b:free) taşı. |
| `401 Authentication required` | `.env`'de `POLLINATIONS_API_KEY` eksik | MCP tool'ları çalışsa bile (setApiKey bellekte) `.env` ayrı mekanizmadır. `.env`'ye key ekle, proxy'yi restart et. |
| `402 Insufficient Balance / PAYMENT_REQUIRED` | Pollinations API bakiyesi tükenmiş — **Pollinations kapalıdır (16 Tem 2026), kullanılmaz.** | Job'ı farklı bir provider'a taşı (NVIDIA Mistral Small 4 veya MiniMax M3). Tüm Pollinations referanslarını temizle. |
| `FileNotFoundError: [Errno 2] ... '/usr/local/bin/nlm'` | Script içinde hardcoded binary path, sistemde o yolda binary yok. | Path'i gerçek binary neredeyse onunla değiştir (`/home/ubuntu/node_modules/.bin/nlm`). İki script'te bu sorun yaşandı: `nb_autologin.py` ve `restore_config.py`. **Kalıcı çözüm:** Script'i `subprocess.run(["nlm", ...])` ile PATH üzerinden çalışacak şekilde güncelle. |
| `Camoufox is not installed at ...` (exit code 1) | `upw_session_refresh.cjs` için Camoufox npm paketi veya binary'si yüklü değil. | **Üç adım:** (1) `npm install camoufox` (2) `npx camoufox fetch` (3) `chmod +x ~/.cache/camoufox/camoufox-bin` |
| `pending_approval` | Cron'da onay gereken komut | approvals.cron_mode: deny var mı kontrol et |
| `PermissionError: [Errno 13] Permission denied: '...sentez_state.json'` | Dosya veya dizin **root** tarafından oluşturulmuş (örn. container init sırasında). ubuntu kullanıcısı yazamaz. | **Çözüm:** Dosyayı sil (`rm` işe yarar çünkü üst dizin ubuntu'ya ait). Silinemiyorsa script'in output path'ini `/tmp/` altına taşı (world-writable). **Koruyucu önlem:** Script'in başına `rm -f + touch` ekle. |
| `tee: /tmp/...: Permission denied` (stderr'de) | Cron runner no_agent script'in stdout'unu `tee /tmp/<dosya>` ile yakalar. Eğer dosya önceden root tarafından oluşturulduysa permission hatası alınır. Script'in kendisi sorunsuz çalışır — hata tee'den gelir. | Wrapper script'in başına `rm -f /tmp/<dosya> && touch /tmp/<dosya>` ekle. Böylece her çalışmada temiz dosyayla başlanır. |
| **Düzeltme sonrası hâlâ raporda görünüyor** | `last_error` ve `last_status` alanları jobs.json'da eski değerlerini korur. Script düzelse bile cron'da error kaydı kalır. | Düzeltme yapıldıktan sonra jobs.json'dan ilgili job'ın `last_error` ve `last_status` alanlarını temizle: `python3 -c \"import json; d=json.load(open('...')); [j.update({'last_error':None,'last_status':None}) for j in d['jobs'] if j['id'] in [...]]; json.dump(d,open('...','w'),indent=2)\"` |
| `git push` — remote rejected (push declined due to repository rule violations) | GitHub Push Protection — bir commit'te hardcoded API key/secret tespit edildi | **Teşhis:** `git push` çıktısında `GITHUB PUSH PROTECTION` ve `secret` ibaresini ara. Hangi dosya + hangi secret olduğunu belirle. **Çözüm sırası:** (1) Secret'ı source file'dan kaldır (env var / BWS / credentials file'a taşı) (2) `.gitignore`'a ilgili dosyayı ekle (3) Git history'den secret'ı temizle (amend/reset/rebase) (4) Force push ile yayınla. Detaylı prosedür: `references/git-push-protection-fix.md` |

### 3. Script Hatalarını Debug Et

**no_agent script'lerinde timeout debugging:**

Önce script'i elle çalıştır (`timeout ile`) ve hangi aşamada takıldığını bul.

> 🔍 Referans: Bu debug akışının adım adım uygulandığı gerçek vaka için `references/noagent-sqlite-timeout-debug.md` dosyasına bak.

```bash
# script'in toplam çalışma süresini ölç
timeout <sn> python3 scripts/problemli_script.py 2>&1
echo "EXIT: $?"
```

Tek tek fonksiyonları import ederek test et:

```bash
timeout 30 python3 -c "
import os, sys, time
sys.path.insert(0, os.path.expanduser('~/.hermes/scripts'))
from script_adi import *

t0 = time.time()
result = fonksiyon_adi()
print(f'Fonksiyon: {time.time()-t0:.2f}s')
"
```

Timeout çıkarsa (exit 124), script'in çıktısı olmaz — sadece sessiz kalır. Bu durumda teker teker her fonksiyonu dene.

**Yaygın no_agent script timeout nedenleri:**

| Neden | Teşhis | Çözüm |
|-------|--------|-------|
| SQLite full table scan (index yok) | `datetime('now', '-7 days')` → string karşılaştırma index kullanamaz | Index ekle: `CREATE INDEX idx_messages_role_ts ON messages(role, timestamp)` |
| `GROUP BY content` veya `GROUP BY substr(...)` | content kolonu büyük, full scan + sort | Index ekle veya sorguyu basitleştir, timeout ile çalıştır |
| `Path.rglob('SKILL.md')` | WSL/Docker'da recursive glob çok yavaş | `iterdir()` + `exists()` ile değiştir |
| `length(content) > 10` gibi fonksiyonlu WHERE | Index kullanamaz, her satırı okur | Emin değilsen sorguyu basitleştir veya LIMIT ekle |
| Eksik binary (`ss`, `free`, `df`) | subprocess.run FileNotFoundError | Önce `shutil.which('komut')` ile kontrol et, yoksa fallback kullan |
| Log dosyası çok büyük | `f.read()[-50000:]` 3MB+ log'u tamamen okur | `f.seek()` ile sonda oku veya `tail` kullan |

**SQLite optimizasyonu püf noktaları:**

- **PRAGMA** ekle: `journal_mode=WAL` (concurrent okuma), `query_only=1`
- **Zaman damgasını Python'da hesapla**, SQL'de string karşılaştırma yapma:
  ```python
  cutoff = (datetime.now() - timedelta(days=7)).timestamp()
  cur.execute("... WHERE m.timestamp > ?", (cutoff,))
  ```
  Bunun yerine ASLA:
  ```python
  cur.execute("... WHERE m.timestamp > datetime('now', '-7 days', 'unixepoch')")
  ```
- **Index eklemeden önce** sorgu planını kontrol et: `EXPLAIN QUERY PLAN SELECT ...`
- **safe_db_query wrapper**: her sorguyu SIGALRM ile timeout korumasına al:
  ```python
  def safe_db_query(query, params=(), timeout=10):
      conn = sqlite3.connect(DB_PATH)
      conn.execute("PRAGMA journal_mode=WAL")
      conn.execute("PRAGMA query_only=1")
      result = []
      signal.alarm(timeout)
      try:
          cur = conn.cursor()
          cur.execute(query, params)
          result = cur.fetchall()
          signal.alarm(0)
      except:
          signal.alarm(0)
          return {"error": "timeout or error"}
      finally:
          conn.close()
      return result
  ```

### 4. Paused Job'ları Değerlendir

| Durum | Aksiyon |
|-------|---------|
| < 1 hafta paused | Hatayı düzelt, resume |
| > 1 hafta paused, hata biliniyor | Düzelt + resume |
| > 1 ay paused | Edel'e sor: "Hala ihtiyaç var mı?" |
| Adında "DISABLED" geçiyor | Muhtemelen kaldırılabilir |

### 5. Schedule Çakışmalarını Kontrol Et

Aynı saatte çalışan job'ları tespit et. no_agent script'ler çakışmaz (kısa süreli).
LLM-driven job'lar aynı provider'da aynı anda çalışırsa proxy darboğazı olabilir.

Kontrol: `cronjob list` → aynı schedule değerini ara.

### 5b. LLM-driven Job'lar İçin Provider Seçimi

Cron job oluştururken/kontrol ederken provider seçimine dikkat et:

| Provider | Ne Zaman Kullanılır | Risk |
|----------|---------------------|------|
| `opencode-zen` | **Varsayılan.** deepseek-v4-flash-free, mimo-v2.5-free modelleri sorunsuz çalışır. Çoğu cron job için idealdir. | ⚠️ **Günlük rate limit paylaşımlıdır.** Aynı free tier'ı kullanan **tüm cron job'lar + Hermes yardımcı sistemleri** (compression, curator, session_search, skills_hub, title_generation, mcp vb.) ortak bir günlük kotayı tüketir. 5+ cron job aynı anda bu provider'ı kullanıyorsa günün ilerleyen saatlerinde 429 almaya başlarsınız. **Dağıtma stratejisi:** Kritik job'ları NVIDIA free tier veya opencode-go (ücretli proxy) gibi alternatif provider'lara taşı. opencode-zen'i az sayıda düşük öncelikli job'a ve yardımcı sistemlere bırak. |
| ~~`custom:Pollinations`~~ | **KALICI OLARAK KAPANDI** (16 Tem 2026, Edel bildirdi) — tüm job'lar başka provider'a taşındı, config'den kaldırıldı | Referans kalırsa temizle |
| `LiteRouter` | **Kullanma.** 7sn rate limit var, cron job'larında garantili hata alırsın. | 403 Rate limit |

**Kural:** LLM-driven bir cron job'ı hata veriyorsa ilk bakılacak şey provider seçimidir. Özellikle LiteRouter'dan opencode-zen'e geçiş çoğu sorunu çözer.

**⚠️ no_agent pattern:** Eğer LLM-driven job sadece bir script çalıştırıp çıktısını yolluyorsa (YouTube taraması gibi) ve sürekli provider limitine takılıyorsa, LLM katmanını tamamen kaldırıp `no_agent: true` yapmak en temiz çözümdür. Script kendi kendine yeterli çıktı üretiyorsa LLM'e gerek yok.

### 6. jobs.json'dan Derinlemesine Kontrol

`cronjob action='list'` her zaman güncel durumu göstermez. **Özellikle:**
- `last_delivery_error` alanı cronjob list'te görünmeyebilir (boş/None sanılır)
- Eski `last_error`'lar (script çalıştıktan sonra düzeltilmiş olsa bile) jobs.json'da kalabilir
- no_agent script hataları LLM-driven hatalardan farklı kaydedilir
- **Prompt preview truncate edilir** — cron list'teki `prompt_preview` kısaltılmıştır. Tam prompt sadece jobs.json'dadır.
- **Model/provider bilgisi cron list'te gösterilir ama ilk elden güvenilmemelidir** — jobs.json'daki `model` ve `provider` alanları source of truth'tir. Cron list'te doğru görünse bile job'ın prompt'unda o model referans edilmeyebilir (job'a atanmış ama kullanılmayan model olabilir).

**Her zaman jobs.json'ı da kontrol et:**

```bash
# Tüm error'leri hızlıca listele
python3 -c "
import json
with open('/home/ubuntu/.hermes/cron/jobs.json') as f:
    data = json.load(f)
for j in data['jobs']:
    if j.get('last_status') == 'error' or j.get('last_delivery_error'):
        print(f\"{j.get('name')}: {j.get('last_status')} | {j.get('last_error', '')[:200]}\")
"
```

**Belirli bir job'ı JSON'da bulmak için:**
```bash
# Job adıyla ara (Unicode karakterleri escape edilmiş olabilir)
grep -n "Bundle\|Gündem" ~/.hermes/cron/jobs.json

# Bulunan satır numarasından itibaren oku
# Jobs.json'da her job ~50-80 satır kaplar — grep sonucu size başlangıcı verir
read_file ~/.hermes/cron/jobs.json offset=<grep sonucu -2> limit=60
```

**Teşhis akışı (3 Temmuz 2026 vakasından — Bundle Gündem İşleme):**
1. Cron list'te `model: "glm-5.1"`, `provider: "custom:opencode-go"` görünür
2. Prompt preview'da model adı geçmez (sadece web_extract + 5N1K formatlama)
3. jobs.json kontrolü: model/ provider alanları cron list ile aynıdır ama prompt'ta hiçbir model referansı YOKTUR
4. Hata: OpenCode Go aylık limiti doldu (17 gün kalan)
5. **Sonuç:** Bu job modelden bağımsız bir iş yapıyor (haber toplama + formatlama). Model sadece formatlama için. opencode-zen (deepseek-v4-flash-free) fazlasıyla yeterli.

**Kural:** Model/provider sorgularken cron list'te gördüğünü değil, jobs.json'daki `model` ve `provider` alanlarını referans al. Prompt'u da oku — job'ın o modele gerçekten ihtiyacı var mı, yoksa atanmış ama kullanılmıyor mu?

### 7. Rapor Formatı

**Cron Sağlık Monitörü çıktı formatı (v2):**

Rapor iki kategoriye ayrılır:

1. **🔴 Yeni Hatalar** — İlk kez görülen veya state'te hash'i bulunmayan hatalar. Öncelikli.
2. **🔁 Tekrarlanan / Geçmiş Hatalar** — Aynı hash daha önce de raporlanmışsa buraya düşer. 24s+ eski hatalar "⏳" ile işaretlenir.

Her hata girişi şu formatta:
```
• **Job Adı** — 2s 15dk once
    └ Kısa hata mesajı (traceback kırpılmış)
```

Başlık satırı:
```
**🩺 Cron Sağlık** — X yeni, Y tekrar | Z/38 çalışıyor
```

En altta paused job sayısı (varsa):
```
⏸️ 3 job paused (bilinçli durdurma)
```

Sorun yoksa sadece `[SILENT]` çıktısı verilir, hiçbir mesaj gitmez.

**Manuel bakım sonrası Edel'e rapor formatı:**

```
🛠️ Yapılan Düzeltmeler:
• [düzeltme 1] — [ne yapıldı]
• [düzeltme 2] — [ne yapıldı]

✅ Sağlıklı Çalışanlar (X/30):
[...]

❓ Sana danışmam gerekenler:
1. [soru 1]
2. [soru 2]
```

## Proaktif Onarım (Otomatik Hata Düzeltme)

Edel cron hatalarını bildirmek zorunda kalmamalı. Cron Sağlık Monitörü tespit eder, **sen düzeltirsin**. Aşağıdaki sistemler birlikte çalışır:

### Otomatik Onarım Job'ı (6 Temmuz 2026 — v2 Prompt)
- **Job ID:** `eb8aa9f5ed25`
- **Schedule:** Her gün 09:30
- **Tetikleyici:** "🛠️ Cron Otomatik Onarım"
- **Çalışma prensibi:** LLM-driven job. Tüm cron job'larını tarar, son 24 saatte error almış job'ları bulur, aşağıdaki 6 pattern'i tanır ve düzeltir:
  1. **Script not found** — script parametresinde `python3 /path/` ön eki
  2. **Script timed out** — no_agent script cron'un 120sn limitini aştı
  3. **Auth expired / exit code 4** — NotebookLM/Google auth hatası
  4. **File not found / Errno 2** — script'in okuduğu dosya yok
  5. **HTTP 4xx/5xx** — API çağrısı hata döndü
  6. **Connection/Network error** — ağ bağlantı sorunu
  7. **402 Insufficient Balance / PAYMENT_REQUIRED** — Pollinations API bakiyesi tükendi. Sık görülür, otomatik düzeltilemez ama raporlanmalı.
  8. **Camoufox binary / npm package missing** — `upw_session_refresh.cjs` bağımlılıkları yüklü değil (`npm install camoufox` + `npx camoufox fetch` + `chmod +x ~/.cache/camoufox/camoufox-bin`).
  9. **Hardcoded binary path FileNotFoundError** — Script içinde `/usr/local/bin/nlm` gibi var olmayan bir yol. **⚠️ Kritik:** Sistemde `nlm` adında İKİ farklı npm paketi var: (a) **groupon/nlm** (v5.8.0) — Node.js lifecycle manager, `changelog/release/verify` komutları. (b) **jacob-bd/notebooklm-mcp-cli** (v0.8.1) — NotebookLM MCP CLI, binary adı `notebooklm-mcp`. `nlm` komutu artık NotebookLM MCP'ye ait DEĞİL. **Doğru binary:** `notebooklm-mcp` (PATH'te). Çözüm: script'in içindeki `NLM_BIN` değişkenini sil veya `notebooklm-mcp` olarak değiştir. `subprocess.run` çağrılarında tam path yerine komut adını kullan (PATH üzerinden çözülsün). NotebookLM auth'u CDP + cookie-based olduğu için `nlm` binary'sine hiç ihtiyaç yok — `nb_keepalive.py` v4.0 MCP-native. **Etkilenen script'lerin durumu (11 Tem 2026 sonrası — hepsi düzeltildi ✅):**
   - `nb_keepalive.py` — v4.0 MCP-native, nlm bağımlılığı tamamen kaldırıldı ✅
   - `nb_autologin.py` — NLM_BIN değişkeni ve nlm cookie update adımı kaldırıldı ✅
   - `refresh_google_token.sh` — NotebookLM kontrolü (`nlm list notebooks`) tamamen kaldırıldı ✅
   - `restore_config.py` — `'nlm': '/usr/local/bin/nlm'` referansı kaldırıldı ✅
- **Kök neden analizi ZORUNLU:** Her hata için script'in kodunu okur, hangi satır/hangi yapının soruna yol açtığını belirler, çözüm önerisi üretir.
- **Yetki:** Sadece bilinen pattern'leri düzeltir. Yeni hata türlerini raporlarken script iç mantığını analiz edip nedenini belirtir.
- **Kısıtlama:** Kendi job'ını asla değiştirmez.
- **Prompt güncelleme:** Yeni bir hata türü keşfedildiğinde bu job'ın prompt'una yeni pattern eklenmeli. Agent'ın sorumluluğu: `cronjob(action='update', job_id='eb8aa9f5ed25', prompt=...)` ile güncelle.

### Agent'ın Sorumluluğu (Proaktif Düzeltme)

**KRİTİK KURAL: Edel asla cron hatası bildirmek zorunda kalmamalıdır.** "Bunu düzelt" demesini bekleme — Cron Sağlık raporu sohbete düştüğü an harekete geç.

1. Cron Sağlık raporunu gördüğünde (Edel forward etmiş olsa bile) **hemen** cronjob(action='list') ile güncel durumu al
2. Hataları **kendin teşhis et ve düzelt** — Edel'in "bunu gördün mü?" demesini dahi bekleme
3. Otomatik Onarım job'ının bir sonraki çalışmasını bekleme — anlık müdahale et
4. Yeni bir hata türü keşfettiysen: bu skill'in pitfall'larını güncelle VE Otomatik Onarım job'ının prompt'una yeni pattern'i ekle (`cronjob action=update job_id=eb8aa9f5ed25 prompt=...` ile)
5. Düzeltme sonrası Edel'e sadece ne yaptığını bildir, onay bekleme

**⚠️ ÖZEL KURAL — Edel bir cron hatasını bildirdiğinde soru sorma, düzelt:**
Edel "günlük sentez çalışıyor mu?" diye sorduğunda veya cron hatasını bildirdiğinde, hatanın kök nedeni netse (ör. rate limit + timeout 2+ gündür tekrarlıyor) çözüm için izin isteme. Doğrudan düzelt:
  - rate limit → daha güvenilir bir provider'a geç (NVIDIA Mistral Small 4, Llama 3.3 70B veya NVIDIA deepseek-v4-flash)
  - timeout → script içi timeout'u düşür, retry'leri kaldır
  - Pollinations hatası → başka provider'a geç (Pollinations kapalı)
Düzeltme sonrası "şunu yaptım, bu gece 23:00'te dener" diye bildir. Onay beklemek yerine çözümü gösterip devam et.

### Cron Sağlık + Otomatik Onarım İş Birliği
```
Cron Sağlık Monitörü (4 saatte bir)  →  Hata tespit + rapor
Otomatik Onarım Job'ı (günde 1 kez)  →  Bilinen hataları düzelt
Sen (anlık)                           →  Bilinmeyen hataları teşhis + düzelt
```

## Lighthouse Uyumlu Not Düşme

Cron işlemleri sonrası notları MEMORY.md'ye TTL'ine göre yaz:

| Veri Türü | TTL | Nereye |
|-----------|-----|--------|
| Hata sebebi, geçici pause | short/7d | MEMORY.md |
| Provider değişikliği, yeni cron | medium/60d | MEMORY.md |
| Kalıcı prosedür değişikliği | long/365d | MEMORY.md → auto-archive wiki |
| Tekrarlayan iş akışı | kalıcı | skill olarak kaydet |

Plan yaparken her maddeyi bir Lighthouse katmanına oturt:
- "Bu hemen çözülmeli" = short
- "Bu önümüzdeki ay geçerli" = medium
- "Bu mimari karar" = long

## Provider Rate Limit Yönetimi

Bir cron job provider rate limit'ine takıldığında:

1. **Teşhis**: Hangi provider + model'in 429 döndüğünü bul
2. **Pause**: Job'ı silme, `cronjob action=pause` ile durdur
3. **Not Düş**: MEMORY.md'ye short TTL ile sebebi kaydet (job_id, tarih, provider)
4. **Alternatif Plan**:
   - Sıklığı azalt (her 30dk → saatlik)
   - Provider failover ekle (aşağıdaki 3 kademeli yapı)
   - Job'ı farklı bir provider/model ile yeniden yapılandır

### 3 Kademeli Fallback Yapısı (16 Tem 2026 — Pollinations çıkarıldı, NVIDIA güncellendi)

Ana provider (`opencode-go`) rate limit yediğinde otomatik devreye giren fallback zinciri:

```
opencode-go (deepseek-v4-flash)
  ├─ opencode-zen (deepseek-v4-flash-free) — ücretsiz
  ├─ NVIDIA (mistralai/mistral-small-4-119b-2603) — ücretsiz, hızlı ✅
  └─ NVIDIA (minimaxai/minimax-m3) — ücretsiz, yavaş ama Edel onaylı
```

❌ Çalışmayan NVIDIA modelleri (kullanma):
- `meta/llama-3.3-70b-instruct` — timeout, Türkçesi zayıf
- `z-ai/glm-5.2` — timeout

**Kurulum:**
```bash
hermes config set fallback_providers '[
  {"model":"deepseek-v4-flash-free","provider":"opencode-zen"},
  {"model":"mistralai/mistral-small-4-119b-2603","provider":"NVIDIA"},
  {"model":"minimaxai/minimax-m3","provider":"NVIDIA"}
]'
```

**Test sonuçları ve bilinen sorunlar:** `references/provider-fallback-testing.md`

**Önemli:** opencode-zen dışarıdan 403 verse de Hermes üzerinden cron job'larında çalışır. NVIDIA'da Mistral Small 4 en güvenilir modeldir. MiniMax M3 sadece dar context'li işlerde kullanılır (ekonomi bültenleri).

## Aylık Tarama Cron Pattern

Uzun aralıklı (aylık) tarama cron'ları için:

```yaml
schedule: "0 6 1 * *"
deliver: "home-kanal"
```

Prompt'a ekle: "Değişiklik yoksa sessiz geç. Sadece farklılık varsa raporla."

## One-Shot Retry Pattern (30 Haz 2026)

Bir cron job'ı bir koşul sağlanmadığı için tamamlayamazsa (örneğin, Zoom kaydı devam ediyor) ve tekrar denemek istiyorsan, bir sonraki denemeyi relative time ile planla:

```bash
# 30 dakika sonra tekrar dene
hermes cron create \
  --name "Retry - Task Adı" \
  --deliver origin \
  "30m" \
  "Aynı görevi tekrar dene: [görev açıklaması]"

# 2 saat sonra tekrar dene
hermes cron create \
  --name "Retry - Task Adı" \
  --deliver origin \
  "2h" \
  "Aynı görevi tekrar dene: [görev açıklaması]"

# Exact time ile (bugün saat 23:00'de)
hermes cron create \
  --name "Retry - Task Adı" \
  --deliver origin \
  "2026-06-30T23:00:00" \
  "Aynı görevi tekrar dene: [görev açıklaması]"
```

**Kurallar:**
- `"30m"` = 30 dakika, `"2h"` = 2 saat, `"90s"` = 90 saniye, `"1d"` = 1 gün
- Exact time ISO format: `"2026-06-30T23:00:00"` (yerel saat — Europe/Istanbul)
- Relative time job'ları `once` olarak planlanır (tek seferlik)
- Maksimum retry sayısı için `--repeat N` ekle (N denemeden sonra sessizce durur)
- Her retry kendi bağımsız job ID'sini alır — önceki job'ın durmasını engellemez
- LLM-driven job retry'i için mutlaka `--skill` ile ilgili skill'i ekle, aksi halde agent bağlamı boş olur

## Pitfalls

### Template: API Retry & Backoff
Script-tabanlı cron job'larda API 429 rate limit'i için şu template'i kullan (`templates/api-retry-backoff.py`):
```
call_with_retry(client, model, messages, retries=5, base_delay=30)
```
Özellikler: 5 deneme, exponential backoff (60s-120s-240s-480s-600s), rate limit dışı hatalarda anında fırlat.

### Genel Pitfall'lar

- **Tüm cron'ları aynı anda resume etme.** Önce düzelt, sonra resume et.
- **Script hatasında direkt "kaldır" deme.** Önce düzeltmeyi dene.
- **no_agent script output'u okurken** içerideki çıktının hassas veri (token, key) içerebileceğini unutma.
- **Env var eksikliğinde Bitwarden'ı kontrol et** ama `bw serve` kapalı olabilir. Alternatif: eski `.env` yedekleri.
- **LinkedIn token refresh gibi ayda 2 kere çalışan cron'lar** gözden kaçabilir. Son çalışma tarihi > 2 haftaysa mutlaka kontrol et.
- **Cron schedule'ı prompt'ta yazandan farklı olabilir** — cronjob'daki schedule doğrudur.
- **"once at DATE TIME" formatı çalışmaz:** `"once at 2026-07-05 20:25"` yazarsan `next_run_at: null` olur, cron hiç tetiklenmez. **Doğru format ISO 8601:** `"2026-07-05T20:25:00+03:00"`. Relative format (örn. `"30m"`, `"2h"`) da güvenlidir, exact schedule her zaman ISO kullan.
- **opencode-zen free tier günlük limiti tüm job'lar arasında paylaşılır.** 5+ cron job + Hermes yardımcı sistemleri aynı free API'yi kullanıyorsa gün ortasında 429 almaya başlarsınız. Çözüm: kritik job'ları NVIDIA free tier (`nvidia-free-deepseek-flash`) veya opencode-go (ücretli proxy, port 19998) gibi alternatif provider'lara dağıt. Günlük Sentez gibi script-tabanlı job'lara retry + exponential backoff ekle (5 deneme, 60-600s).
- **Edel'e hata bildirimi gelmesi = cron sistemi hatayı zaten bildirmiş.** Sen oturumunda cronjob list ile kontrol et, monitörün tespit etmesini bekleme.
- **Mixed job'lar (script + LLM provider):** Script başarılı olsa bile provider rate limit'e takılırsa cron error gösterir. Kök neden ayrımı için script'i elle çalıştır.
- **MCP server crash sonrası MCP tool'ları kullanılamaz hale gelir.** Detaylı kurtarma adımları: `references/mcp-crash-recovery.md`
- **"[SILENT]" çıktısı veren cron job'lar hâlâ API çağrısı tüketir.** Bir agent job (LLM-driven) [SILENT] çıktısı verse bile, prompt'u işlemek için 1 API çağrısı yapar. Kuyruğu dolu olan karusel gibi job'lar her gün 2 boş API çağrısı yaparak free tier limitini gereksiz tüketir. Çözüm: kuyruk limitine ulaşmış job'ları **pause'a al**, sadece [SILENT] çıktısı vermeye bırakma. Tüketici olmayan job'lar çalışmaya devam etsin diye düşünme — her çağrı sayılır.
- **"Script timed out" — no_agent script cron'un 120sn timeout sınırı:** Cron no_agent=true script'leri çalıştırırken **built-in 120 saniye timeout** uygular. Script bu sürede tamamlanmazsa cron "Script timed out after 120s" hatası verir ve script'i SIGTERM ile öldürür. **Bu cron seviyesinde yapılandırılabilir bir parametre DEĞİLDİR — değiştirilemez.** Çözüm:
  - Script içi API timeout değeri **110sn veya altı** olmalı (cron'a 10sn marj bırak)
  - Script içi retry mekanizması (tenacity, urllib retry vb.) varsa **toplam süre 110sn'yi geçmemeli**
  - Retry'ler toplam süreyi şişiriyorsa retry'leri kaldır veya timeout'u düşür
  - Örnek: `urllib.request.urlopen(req, timeout=120)` + 3× tenacity retry = ~400sn → cron 120sn'de öldürür. Çözüm: timeout=110, retry kaldır
  - **Teşhis:** Script'i elle `timeout 120 python3 script.py` ile çalıştır, hangi aşamada takıldığını bul
- **Cron list'te görünen model/provider'a güvenme — jobs.json'dan doğrula.** `cronjob(action='list')` çıktısındaki `model` ve `provider` alanları bazen yanıltıcı olabilir (job'a atanmış ama kullanılmayan model). Her zaman `~/.hermes/cron/jobs.json` dosyasını oku, prompt'u kontrol et — job gerçekten o modeli kullanıyor mu, yoksa sadece atanmış mı?
- **`--cron` gibi script argümanları no_agent=true'da geçirilemez:** no_agent=true job'larda `script` parametresi sadece dosya adı alır, argüman geçirilmez. Script'e argüman gerekiyorsa ya script içinde default davranışa ekle ya da job'ı no_agent=false LLM-driven yap.
- **Hardcoded binary path'ler script içinde bozulabilir:** `nb_autologin.py`'de `NLM_BIN = "/usr/local/bin/nlm"` yazıyordu ama gerçek nlm binary'i `/home/ubuntu/node_modules/.bin/nlm`'de. Sistem değişikliklerinde (npm update, pip install, symlink yeniden yapılandırma) binary yolları değişebilir. Script'lerin içindeki hardcoded path'leri `which nlm` veya `readlink -f $(which nlm)` ile doğrula. **Kalıcı çözüm:** `subprocess.run` çağrılarında tam path yerine komut adını kullan (PATH üzerinden çözülsün). Aynı hata `restore_config.py`'de de mevcut.
