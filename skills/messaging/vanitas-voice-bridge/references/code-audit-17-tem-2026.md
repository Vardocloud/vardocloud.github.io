# Code Audit — 17 Temmuz 2026

## Kapsam
Vanitas Voice v16 full-duplex projesinin 7 hata/eksik noktasının tespiti ve çözüm stratejileri.

## Bulgular

| # | Hata | Tür | Kod Dosyası | Durum |
|---|------|-----|-------------|-------|
| 1 | VAD Türkçe parametreleri koda uygulanmamış | 🔴 KRİTİK | `soniox-server/main.py` → VADProcessor çağrısı | ❌ AÇIK |
| 2 | Dual-prompt senkronizasyon riski | 🟡 ORTA | `server.mjs` L112 vs `tools.py` L7 | 🔄 İZLENİYOR |
| 3 | LLM model optimizasyonu (70B yavaş) | 🟡 ORTA | `main.py` L37 | 🔄 BEKLEMEDE |
| 4 | Session hafıza yok (bağlam kaybı) | 🟡 ORTA | `llm.py` messages listesi | 🔄 PLANLANDI |
| 5 | GET / flood (log şişmesi) | 🟢 DÜŞÜK | `server-output.log` | ❌ AÇIK |
| 6 | Keeper timeout (30sn yetmiyor) | 🟢 DÜŞÜK | `start_vanitas_server.sh` | ❌ AÇIK |
| 7 | AudioWorklet → çalışıyor | ✅ ÇÖZÜLDÜ | `full-duplex.html` | ✅ |

## Detay

### 1. VAD Türkçe Parametreleri Koda Uygulanmamış

**Skill'de yazılan:** threshold=0.4, min_silence_duration_ms=600
**Kodda olan:** VADProcessor() — hiç parametre geçilmemiş, varsayılanlar (0.5/300ms)

**Teşhis komutu:**
```bash
grep -n "VADProcessor\|threshold\|min_silence" ~/vanitas-web/soniox-server/main.py
# Beklenen: VADProcessor(threshold=0.4, min_silence_duration_ms=600, ...)
# Mevcut:  VADProcessor()  ← parametre yok!
```

**Düzeltme:** main.py'de VADProcessor çağrısına parametre ekle + server restart.

### 2. Dual-Prompt Karşılaştırması

**server.mjs L112** (REST fallback — half-duplex):
```
Senin adin Vanitas. Karsindaki kisi Edel. Sicak, samimi, biraz muzip konusursun.
Edel'e hitap ederken 'canim' kelimesini COK NADIREN kullan, belki 5 konusmada bir.
Hic kullanmasan da olur. Cevaplarin KISA ve dogal olmali - maksimum 2-3 cumle.
Bilmedigini uydurma, 'bilmiyorum' de, 'canim' ekleme. Sesli gorusmedesin, emoji
kullanma. Turkce konus.
```

**tools.py** (WebSocket full-duplex):
```
Senin adin Vanitas... (detaylı: KONUSMA TARZI + KISILIK + BILGI SINIRI
alt başlıklarıyla, tarih+dil parametreleri)
```

İkisi de "canim COK NADIREN" ve "kisa cevap" kurallarını içeriyor. tools.py daha detaylı.
**Risk:** Biri güncellenince diğeri unutulursa tutarsız davranış.

### 3. LLM Model Hız Karşılaştırması

| Model | TTFB | Türkçe | Not |
|-------|------|--------|-----|
| llama-3.3-70b-versatile (mevcut) | ~500ms | 🟢 iyi | Mevcut |
| llama-4-scout-17b-16e-instruct | ~150ms | 🟡 orta | 3x hızlı |
| llama-3.1-8b-instant | ~100ms | 🟡 orta | 5x hızlı |

### 5. GET / Flood Analizi

```
$ grep -c "^GET /$" /home/ubuntu/vanitas-server-output.log
70+  (tahmini: dakikada 1-2 istek)
```

**Olası kaynaklar:**
- Cloudflared health check
- Açık browser sekmesi (auto-reload)
- Tailscale funnel proxy check
- Bot taraması (düşük ihtimal)

### 6. Keeper Timeout

Script'te `for i in $(seq 1 30)` — 30sn timeout.
VAD warmup (Silero torch.hub.load) soğuk başlangıçta 15-30sn.
Node.js başlatma ~5sn + Python başlatma ~3sn = toplam ~38sn → timeout.
**Düzeltme:** `seq 1 60` yap.
