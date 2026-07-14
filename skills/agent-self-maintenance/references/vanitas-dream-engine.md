# Vanitas 8-Boyutlu Rüya Motoru

## Nedir

Her gece 04:00'te çalışan bir Python script'i (`~/.hermes/scripts/vanitas_dream.py`). Vanitas'ın kendi kendine check-up yaptığı, 8 boyutta sistem sağlığını değerlendirdiği bir öz-diagnostik aracı.

**Dağıtım:** Hermes cron job — "Vanitas 8-Boyutlu Rüya" (job_id: `f9ddbe495a13`)
**Schedule:** `0 4 * * *` (her gün 04:00)
**Rejim:** `no_agent=true` — doğrudan Python script'i çalışır, LLM çağrısı yok, maliyet $0
**Script konumu:** `~/.hermes/scripts/vanitas_dream.py`

## 8 Boyut

| # | Boyut | Fonksiyon | Ne Yapar |
|---|-------|-----------|----------|
| 1 | **CQS** | `evaluate_cqs()` | Son 24 saatteki konuşma yoğunluğu (0-1) |
| 2 | **Maliyet** | `analyze_costs()` | 7 günlük token tüketimi ve USD maliyet |
| 3 | **Skill** | `analyze_skills()` | Skill kullanım istatistikleri (cron/jobs.json + tool_usage) |
| 4 | **Güvenlik** | `security_summary()` | Açık port sayısı, fail2ban durumu |
| 5 | **Sızıntı** | `leak_check()` | Log'larda API key sızıntısı kontrolü |
| 6 | **Pattern** | `workflow_patterns()` | Tekrar eden kullanıcı mesajları (exact + prefix) |
| 7 | **Fırsat** | `new_opportunities()` | Disk trendi, hatalı cron'lar, atıl skill'ler, RAM uyarısı |
| 8 | **İş Çıktısı** | `job_outputs()` | Cron health check (jobs.json bazlı, OK/ERR sayısı) |

## Çıktı Formatı (10 Haz 2026 itibarıyla güncellendi)

Log'lar `~/wiki/concepts/vanitas-dream-log.md` dosyasına yazılır. Telegram'a özet satır:

```
🌙 Rüya tamamlandı: 2026-06-10 19:15
   CQS: 0.9 | Maliyet: $0
   Skill: 9/141 | Sızıntı: temiz
   Cron: 20OK/3ERR | 3 firsat
```

Detaylı log formatı:
```
## 🌙 Rüya: 2026-06-10 19:15
- **CQS:** 0.9
- **Maliyet (7 gün):** $0 (günlük ~$0.0)
- **Skill:** 9/141 (kaynak: cron_jobs+tool_usage)
- **Kullanılan skill'ler:** browser-debugging, google-workspace, sohbet, ...
- **Kullanılmayan:** agent-self-maintenance, vllm, ...
- **Güvenlik:** {'open_ports': 19, 'fail2ban': 'active'}
- **Sızıntı:** temiz
- **Pattern (exact):** 0 tekrar
- **Pattern (prefix):** 0 grup
- **Fırsatlar (3):** ⚠️ Disk 84% dolu | 🔴 3 cron job hatalı | 💤 132 skill kullanılmıyor
- **Cron:** 20/23 başarılı, 3 hatalı
- **Hatalı cron'lar:** 🔴 Tam Güvenlik: HTTP 429; Skool: RuntimeError; Model Watchdog: NameError
```

## Veri Kaynağı

Script iki ana veri kaynağı kullanır:

### Hermes State DB (`~/.hermes/state.db`)
- **sessions** tablosu: model, token sayıları, maliyet, zaman bilgisi
- **messages** tablosu: rol, içerik, tool_name, timestamp
- Telegram mesajları `source='telegram' AND user_id LIKE '%6306976553%'` filtresiyle bulunur

### Cron Jobs JSON (`~/.hermes/cron/jobs.json`)
- Her cron job'ın: id, name, skills[], enabled, last_status, last_error
- Skill kullanımı buradan çözülür (mesaj içeriği aramak yerine)
- İş çıktısı kontrolü buradan yapılır (subprocess çağrısı yerine)

## Dimension Detayları ve Güncelleme Geçmişi

### 3️⃣ Skill — Cron/Jobs.json Bazlı Ölçüm
**Güncelleme (10 Haz 2026):** Mesaj içeriğinde skill adı arama yöntemi terk edildi, yerine cron/jobs.json + tool_usage bazlı ölçüm geldi.

**Mevcut yaklaşım:**
1. Dosya sistemindeki tüm skill'leri listele (`Path().rglob("SKILL.md")`)
2. `cron/jobs.json`'ı parse et → enabled job'ların `skills[]` listesini oku
3. Ayrıca son 7 gündeki session'lardan `tool_name` sütununu tara → skill adlarıyla eşleştir
4. Kullanılan = cron'da referans verilen + tool kullanımında görülen skill'ler

**Önceki yaklaşım (çalışmıyordu):**
`WHERE content LIKE '%skill_adi%'` — no_agent'da hiçbir skill yüklenmediği için her zaman 0/141 çıkardı.

### 6️⃣ Pattern — Exact + Prefix Gruplama
**İyileştirme (10 Haz 2026):** Prefix match eklendi.
- Exact match: `GROUP BY content HAVING cnt > 1` (korundu)
- Prefix match: `GROUP BY substr(content, 1, 50) HAVING cnt > 2` (yeni)
- İkisi de döndürülür, prefix match aynı konunun farklı ifadelerini yakalar

### 7️⃣ Fırsat — 4 Alt Kontrol
**Hayata geçirildi (10 Haz 2026):** Placeholder kaldırıldı, 4 gerçek kontrol eklendi:
1. **Disk trendi:** `df -h /` → yüzde >80 uyarı, >60 bilgi
2. **Başarısız cron'lar:** `cron/jobs.json`'da `enabled=true AND last_status=error` olanları listele
3. **Atıl skill'ler:** Tüm skill'ler - cron'da kullanılanlar = kullanılmayanlar
4. **RAM uyarısı:** `free -m` → kullanım >85% kritik, >70% uyarı

**Önceki yaklaşım (boştu):**
`return {"note": "Web search ile derinleştirilecek (ayrı cron)"}` — placeholder

### 8️⃣ İş Çıktısı — Jobs.json Bazlı Kontrol
**Düzeltildi (10 Haz 2026):** Subprocess+hermes_tools çağrısı terk edildi.
1. `cron/jobs.json`'ı oku
2. Enabled job'ları filtrele
3. Her job için `last_status` ve `last_error`'u raporla
4. OK sayısı / Error sayısı / toplam job sayısı

**Önceki yaklaşım (güvenilmezdi):**
```python
subprocess.run(["python3", "-c", "from hermes_tools import terminal; ..."])
```
`hermes_tools` Hermes agent ortamı dışında import edilemez.

## no_agent Modu Kısıtlamaları

Script `no_agent=true` cron job olarak çalışır. Bu şu anlama gelir:
- LLM çağrısı yok (0 token harcanır)
- Skill'ler yüklenmez
- `hermes_tools` kullanılamaz (import hatası)
- Sadece Python stdlib + SQLite + subprocess mevcuttur
- Çıktı stdout'a yazılır → Telegram'a iletilir

## Bakım Prosedürü

1. **Script'i çalıştır:** `cd ~/.hermes && python3 scripts/vanitas_dream.py`
2. **Log'u kontrol et:** `~/wiki/concepts/vanitas-dream-log.md` — son girişi oku
3. **Cron job verisini doğrula:** `cron/jobs.json`'da enabled job'ların `last_status` ve `last_error` alanlarını kontrol et
4. **Bir boyutu ayrı test et:** Her fonksiyon bağımsız çalışır — `analyze_skills()`, `new_opportunities()`, `job_outputs()` doğrudan `cron/jobs.json`'a bağlıdır
5. **Değişiklik sonrası:** `python3 scripts/vanitas_dream.py` ile test et, çıktıyı doğrula
6. **Eğer `cron/jobs.json` bozulursa:** `cronjob action=list` ile geçici liste alınabilir — format: `id`, `name`, `skills[]`, `enabled`, `last_status`, `last_error`
7. **Çıktı formatı değişirse:** Hem stdout özeti hem log dosyası formatı ayrı ayrı güncellenmeli — ikisi farklı yapıda (stdout kısa özet, log detaylı)
