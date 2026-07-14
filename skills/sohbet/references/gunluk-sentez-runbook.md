# Günlük Sentez Runbook — Pratik Çalışma Akışı

> Sesiz cron için elle çalıştırma kılavuzu. Hata toleransı sıfır: sessiz ol, yeni dosya yaz, çık.

## Ön Koşullar

- `date +%Y-%m-%d` — bugünün tarihi
- `ls ~/.hermes/cron/output/` — tüm job output dizinleri
- `~/.hermes/cron/jobs.json` — job ID → ad eşlemesi

## Adım 1: Job ID'leri Ada Eşle

```bash
python3 -c "
import json
d = json.load(open('/home/ubuntu/.hermes/cron/jobs.json'))
for j in d['jobs']:
    print(f'{j[\"id\"][:12]} | {j[\"name\"]} | {j.get(\"status\",\"?\")} | enabled={j.get(\"enabled\",\"?\")}')
"
```

Çıktıdaki ID'leri not al. **Her seferinde doğrula** — job ID'leri değişebilir.

## Adım 2: Bugünün Çıktı Dosyalarını Bul

```bash
# Tüm job'lar için bugünün dosyalarını listele (paralel)
for d in ~/.hermes/cron/output/*/; do
  job_id=$(basename "$d")
  latest=$(ls -t "$d" 2>/dev/null | head -1)
  if [ -n "$latest" ]; then
    echo "$job_id | $latest"
  fi
done
```

## Adım 3: Response'ları Oku (tail -N)

Her job'ın son çıktısından **son 80 satırı** oku — Response her zaman sonda.

```bash
# İşe yarayan tek satırlık pattern:
tail -80 ~/.hermes/cron/output/<JOB_ID>/<TARIH_SAAT>.md
```

**[SILENT]** dönen job'ları hemen geç — bugünkü katkısı yok.

**⚠️ Hızlı gezinme ipucu:** 8+ job'ın hepsini `tail -80` ile tek tek okuyacağına,
arka arkaya 3-4 paralel `tail` çağrısı yap, sonra birleştir. Her job için 30 saniyeden
fazla harcama — varsa öne çıkan başlık, yoksa geç.

## Adım 4: Response'dan Veri Çıkar

Beklenen response formatları:

| Cron | Yanıt Kalıbı | Ne Bekle |
|------|-------------|----------|
| Bundle | Haber başlıkları + linkler | Gündem, bilim, teknoloji |
| APA Search | Araştırma başlıkları | Psikoloji literatürü |
| Skool | Topluluk öne çıkanları | AI araçları, tartışmalar |
| Gmail Pipeline | Mail konuları + işlemler | Fırsatlar, önemli mailler |
| Bardo Lead | IG hesap analizi | Rakip/ilham verici hesaplar |
| Polymarket | Piyasa sinyalleri | Mispricing, fiyat değişimi |
| Security Audit | Port/servis durumu | Açıklar, riskler |
| Gmail Deep Dive | Gece mail taraması | Alternatif mail okuma |

**Önemli:** Her job'dan **en fazla 2-3 öne çıkan başlık** al. Tümünü okumaya çalışma.

## Adım 5: Çapraz Bağlantı Kur

Ortak temaları aramak için **birincil + ikincil** kaynakları yan yana koy:

```
Örnek (23 Haz 2026):
  Skool: open-source AI orchestration tools trending → open-interpreter, mcp-agent
  Bundle: Oracle AI pivot, mass layoffs → AI agents replacing headcount in enterprises
  APA: Chatbot ethical frameworks, AI therapy research → boundaries of AI in mental health
  → SENTEZ: Bardo (psikoloji + AI) için üçlü fırsat — 
    (a) AI orchestration henüz democratize olmamış,
    (b) Kurumsal AI agent pazarı büyüyor,
    (c) Psikolojide AI etiği tartışması pazara yeni giriyor
```

**Ara:** Aynı şirket/kavram birden çok kaynakta geçiyor mu?
- `Oracle` → Bundle'da + Gmail'de (LinkedIn notification)
- `Anthropic` → Bundle'da IPO + Gmail Deep Dive'da "When AI Builds Itself"
- `Deepgram/Soniox` → Skool'da + Voice agent çalışması

## Adım 6: MD Notu Yaz

```bash
cat > ~/wiki/ogrenme/2026-06-23.md << 'EOF'
# Günlük Sentez — 2026-06-23

## Bugün Öğrendiklerim
### 🌍 Dünya Gündemi (Bundle)
- [öne çıkan 2-3 başlık, tek satır]

### 🧠 Psikoloji/Akademi (APA)
- [Edel'in ilgi alanına girenler ★]

### 🤖 Tech/AI (Skool + Bundle Teknoloji)
- [araç, trend, topluluk tartışması]

### 📧 Fırsatlar & Takip (Gmail)
- [önemli mailler, fırsatlar]

### 🔍 Diğer Kaynaklar (Bardo, Polymarket, Security)
- [bu kaynaklardan notlar]

## Çapraz Bağlantılar
- [X] + [Y] = [sentez cümlesi]
- [A] + [B] = [uygulama fikri]

## Yarın İçin Tohumlar
- Edel'le konuşurken açılabilecek doğal konular
- Hangi bağlamda nasıl sorulacağı
EOF
```

## Adım 7: Memory'yi Dene (Beklenen Hata)

```python
# memory() bu ortamda çalışmaz — bekle, sessizce geç
# Çözüm: sadece wiki dosyası yeter. Ertesi gün Vanitas devralır.
```

`memory()` açıkça "Memory is not available" hatası dönerse → **alma, geç**.

## Tam Örnek (23 Haz 2026)

Bu runbook'la aynı anda şu adımlar atıldı:

1. `cronjob(action='list')` → 8 job listelendi
2. `ls ~/.hermes/cron/output/` → 8 dizin tespit edildi
3. Her dizinde `ls -lt` ile son çıktı bulundu  
4. Tüm çıktılar `tail -80` ile okundu → 3'ü [SILENT], 5'i içerik dolu
5. İçerik dolu olanlar: Bundle (haberler), APA (eylem araştırması), Skool (open-source AI tools), Gmail Pipeline (Deepgram haber), Bardo Lead (Samsun psikolog hesapları)
6. Çapraz bağlantı: APA chatbot ethics + Bundle Oracle AI + Skool open-source orchestration → Bardo fırsatı
7. Wiki yazıldı: `~/wiki/ogrenme/2026-06-23.md` (4.8KB)
8. Memory denenemedi → sessizce geçildi
9. **[SILENT]** — hiçbir şey bildirilmedi

## Sık Sorunlar

| Sorun | Çözüm |
|-------|-------|
| `session_search` boş döndü | cron output dizinlerine direkt bak, session_search atla |
| Cron çıktısı yok (dizin boş) | Job bugün çalışmamıştır — geç, zorlama |
| Cron çıktısı çok büyük (5000+ satır) | `tail -80` yeter, baştan okuma |
| Memory hatası | Bilinen opencode-zen kısıtı — wiki dosyası yeter |
| Hiçbir cron çıktısı yok | Bugün cron'lar çalışmamış — [SILENT] dön |
| Job ID değişmiş | `jobs.json`'dan yeniden oku, eskisini kullanma |
