# Vanitas Sürekli Öğrenme Pipeline'ı (5 Haz 2026)

## Mimari

5 katmanlı bilgi işleme çerçevesi. Tüm veri kaynakları aynı boru hattından geçer:

```
TÜM KAYNAKLAR → ① TOPLA → ② ANALİZ → ③ BAĞLA → ④ KAYDET → ⑤ SENTEZ
```

| Katman | İşlev | Araç |
|--------|-------|------|
| ① Topla | Ham veriyi kaynaktan çek | web_extract, API, browser |
| ② Analiz | Kavram çıkar, kategorize et | EKİP Analist (mimo-v2.5-free) |
| ③ Bağla | Edel'in ilgi alanlarıyla eşleştir | AI ethics, psikoloji, güvenlik |
| ④ Kaydet | Wiki + NotebookLM'e yaz | llm-wiki, notebooklm-mcp |
| ⑤ Sentez | Gün sonu tüm kaynakları birleştir | Günlük Sentez cron (23:00) |

## Kaynaklar ve Cron'lar

| Kaynak | Cron ID (DOĞRULA!) | Sıklık | Alan | Model |
|--------|-------------------|--------|------|-------|
| 📰 Bundle | `~/.hermes/cron/jobs.json` kontrol et | 09/13/19 | Genel gündem | deepseek-v4-flash |
| 🧠 APA | `d4e5348f059f` | 09/15/21 | Psikoloji literatürü | deepseek-v4-flash-free (Zen) |
| 🤖 Skool | `50002951d6bc` | 09:00 | AI/yazılım toplulukları | deepseek-v4-flash |
| 📧 Gmail Pipeline | `f4ea19bb906a` | 09/15/21 | Mail akışı | deepseek-v4-flash |
| 🌙 Gmail Deep Dive | `9665eb62b757` | 02:00 | Gece keşif | deepseek-v4-flash |
| 🧬 Günlük Sentez | `3ef33fe37449` | 23:00 | Çapraz bağlantı | deepseek-v4-flash |

⚠️ **Cron ID'leri eskiyebilir:** Bundle ve diğer cron job ID'leri yeniden oluşturma veya değişiklik sonrası farklılaşabilir. `~/.hermes/cron/jobs.json` dosyasını okuyarak her seferinde DOĞRULA. (7 Haz 2026: Bundle ID `4cb28605521c` → `93582f1545d2` olarak değişmişti.)

## Sentez Formatı

Günlük Sentez (23:00) şu adımları izler:

### 1. Kaynak Çıktılarını Topla (ÖNCELİKLİ: Dosya Sistemi)

**session_search her zaman güvenilir değildir** — cron çıktıları Telegram topic'e deliver edildiğinde FTS5 indeksi kapsamayabilir.

**Öncelikli yöntem — Dosya sistemi (`~/.hermes/cron/output/`):**
```bash
# Her job için bugünün çıktı dosyasını bul
ls ~/.hermes/cron/output/<job_id>/  # timestamp'li .md dosyaları
```

**Cron çıktı dosyaları BÜYÜKTÜR** (skill içeriğini prompt olarak embed eder, 1000+ satır).
Response kısmı dosyanın sonundadır. Hızlı okuma tekniği:

```bash
# Son 60-80 satır = Response bölümü
tail -60 ~/.hermes/cron/output/<job_id>/<timestamp>.md
```

Bu yöntemle 5000 satırlık bir dosyayı okumadan sadece sonucu alırsın.
Bazı job'lar SADECE "[SILENT]" döner — o zaman o job'ın bugünkü katkısı yoktur.

### 2. Çapraz Bağlantı Kur

**Strateji — Ortak temaları ara:**
- Aynı şirket/kavram farklı kaynaklarda geçiyor mu? (Örn: Anthropic hem Bundle'da IPO haberi, hem Gmail Deep Dive'da "When AI Builds Itself" raporu olarak geçer.)
- Bundle'daki gündem maddesi, Skool'daki tartışmayı açıklıyor mu?
- APA'daki araştırma, Gmail'deki bir fırsatla bağlantılı mı?

**Her kaynağın çıktısını hızlıca tara, 1-2 öne çıkan başlık belirle, kalanını atla.**

### 3. MD Notu Yaz (`~/wiki/ogrenme/YYYY-AA-GG.md`)

```markdown
# Günlük Sentez — YYYY-AA-GG
## Bugün Öğrendiklerim
### 🌍 Dünya Gündemi (Bundle)
### 🧠 Psikoloji/Akademi (APA)
### 🤖 Tech/AI (Skool + Bundle Teknoloji)
### 📧 Fırsatlar & Takip (Gmail)
## Çapraz Bağlantılar
## Yarın İçin Tohumlar
```

### 4. Memory'ye Kaydet (⚠️ opencode-zen kısıtlaması)

**opencode-zen modeli (`deepseek-v4-flash-free`) memory tool'unu desteklemez.** `memory()` sessizce "Memory is not available" hatası döner.

**Çözüm:**
- Bu adımı atla, sadece wiki dosyasına yaz.
- Ertesi gün Vanitas (deepseek-v4-pro) dosyayı okuyarak devralır.
- `~/wiki/ogrenme/` dizini, `session_search(query="günlük sentez YYYY-AA-GG")` ile bulunabilir.

### 5. SESSİZ KAL

Edel'e hiçbir şey gönderme. Bu cron sadece Vanitas'ın iç öğrenme sürecidir.

## Edel'in Kuralları

- **ÖZET YOK** — Vanitas tüm haberleri derinlemesine okur, öğrenir, fikir çıkarır
- **Wiki'ye kaydet** — yeni kavramlar, kişiler, şirketler
- **Tekrar işleme** — önceki günlerin sentezleri kontrol edilir, aynı bilgi tekrar işlenmez
- **Tüm kaynaklar her gün** — APA, Skool, Bundle, Gmail hepsi günlük
- **Vanitas kendi kendine öğrenir** — okur, not alır, sentezler

## Edel'e Çıktı

Sentezden sonra Edel'e SADECE tek cümle rapor:
"Hafızama X yeni bilgi ekledim, Y çapraz bağlantı kurdum."

Tüm detaylar `~/wiki/ogrenme/` dizininde MD olarak saklanır.
Edel'e uzun rapor, özet, liste GÖNDERİLMEZ.

## Pratik Çalışma Örneği (7 Haz 2026)

Bu referans, 7 Haziran 2026 Günlük Sentez cron çalışmasından elde edilen
deneyimle güncellenmiştir. Doğrulanan teknikler:

1. ✅ `~/.hermes/cron/output/<job_id>/` — güvenilir kaynak, session_search'tan öncelikli
2. ✅ `tail -60` — büyük dosyalarda Response bölümünü hızlı bulma
3. ✅ [SILENT] tespiti — boş job'ları anında eleme
4. ❌ `memory()` — opencode-zen'de çalışmaz, wiki dosyasına yaz yeter
5. ✅ Çapraz bağlantı — ortak terimler (şirket adı, kavram) üzerinden kurulur
