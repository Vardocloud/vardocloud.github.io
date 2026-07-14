---
name: vanitas-voice-bridge
version: 1.32.0
title: Vanitas Voice Bridge — Multi-Backend Voice Agent
description: 'v16 (ACTIVE). AudioWorklet birincil ✅. Ses Grace. VAD Turkish tuning (600ms, 0.4th). Prompt: rol karmaşası fix ("Sen Vanitas" → "Senin adın Vanitas"). "Canım" çok nadiren. RECORD_SESSION debugging. Tünel: cloudflared quick tunnel container içi (cron keeper v2).'
tags: [voice, soniox, groq, stt, tts, cloudflared, edge-tts, soniox-client, vad, realtime-stt, websocket, heartbeat, tunnel, tailscale, v16, watchdog, keeper]
triggers:
  - tailscale
  - funnel
  - voice
  - ses
  - voice agent
  - sesli görüşme
  - vanitas voice
  - soniox
  - full-duplex
  - barge-in
  - echo
  - duymuyor
  - tepkisiz
  - mikrofon çalışmıyor
  - TTS geç
  - ses kalitesi
  - bağlamdan kopuk
  - isSpeaking
  - Maya ses
  - GainNode
  - AudioWorklet
  - audioworklet
  - ScriptProcessor
  - ses yakalama
  - PCM
  - full-duplex.html
---

# Vanitas Voice Bridge

## v16 is CURRENT (12 Tem 2026) — Soniox Full-Duplex

> **Pipeline:** PCM (16kHz mono) → Silero VAD (barge-in) → Soniox stt-rt-v5 (streaming STT) → Groq llama-3.3-70b (LLM) → Soniox tts-rt-v1 (streaming TTS, voice=Grace) → 24kHz PCM → hoparlör
> **13 Tem Güncelleme:** AudioWorklet birincil ses yakalama (ScriptProcessor fallback) ✅. Ses Grace'e geçti (Maya→Grace). "Canım" prompt iyileştirmesi (çok nadiren kullan).
> **Referanslar:** `references/soniox-voice-bot-demo.md` (mimari), `references/nodejs-integration.md` (Node.js proxy), `references/voice-quality-diagnostics-11-tem-2026.md` (teşhis)
> **⚠️ v10.10 Dual-Path HENÜZ entegre DEĞİL:** Şu an sadece tek patika (Groq direkt). Edel kararı: önce temel mekanizma tamamlanacak.

## Architecture

```
Client (Browser)
  │
  └─ WebSocket (/ws/soniox) ← Node.js (port 3005)
       └─ Proxy → Python (port 8765)
            ├─ Silero VAD (barge-in — konuşurken kesme)
            ├─ Soniox stt-rt-v5 (gerçek zamanlı transkripsiyon)
            ├─ Groq llama-3.3-70b (Vanitas cevap üretimi)
            └─ Soniox tts-rt-v1 (streaming ses çıkışı)
```

**Özellikler:**
- **Full-duplex:** Aynı anda konuşma + dinleme
- **Barge-in:** VAD konuşma başlangıcını algılar → LLM üretimini iptal eder → yeni transkripsiyon başlar
- **Düşük gecikme:** Streaming STT+TTS sayesinde half-duplex'e göre ~2s avantaj
- **Groq LLM:** `llama-3.3-70b-versatile` — hızlı inference (~250ms TTFB)

## Frontend

| Sayfa | URL | Durum |
|-------|-----|-------|
| Full-duplex (WebSocket + PCM) | `/full-duplex.html` | ✅ Ana hedef |
| Half-duplex (HTTP REST + Edge TTS) | `/index.html` | 🔄 Fallback |

**Önemli:** Ana sayfa (`/`) full-duplex `full-duplex.html`'e yönlendiriyor. Half-duplex `index.html` fallback olarak `/index.html` adresinde duruyor.

### Ses Yakalama: AudioWorklet (birincil) + ScriptProcessor (fallback)

`full-duplex.html` 13 Tem 2026 itibarıyla **AudioWorklet** kullanır:
1. **AudioWorkletProcessor** (`PCMCaptureProcessor`) — Blob URL ile inline tanımlandı, ayrı audio thread'de çalışır
2. Sesi **Float32'den PCM s16le'ye** çevirir + **downsample** yapar (native rate → 16kHz)
3. **Transferable** `postMessage` ile sıfır kopyalı gönderim (zero-copy)
4. **AudioWorklet başarısız olursa** (çok eski tarayıcı) → ScriptProcessor fallback
5. Her iki yol da aynı `handlePcmData()` fonksiyonuna gider — seviye göstergesi + byte sayacı ortak
6. Echo önleme: `GainNode(0)` ile sessiz çıkış her iki yolda da uygulanır
7. Hangi metodun aktif olduğu `captureBadge` ile gösterilir

Referans: `references/audioworklet-migration-13-tem-2026.md`

## Quick Status Check

```bash
# Port kontrolü (/proc/net/tcp — container/lsof alternatifi)
cat /proc/net/tcp | grep -E ":0BBD|:223D"

# 0BBD = port 3005 (Node.js HTTP+WS)
# 223D = port 8765 (Python Soniox server)

# Sağlık testleri
curl -sf --max-time 5 http://0.0.0.0:3005/ > /dev/null && echo "Node.js OK" || echo "Node.js DOWN"
curl -sf http://127.0.0.1:8765/health 2>/dev/null || echo "Python port 8765 — WebSocket only"

# Node.js process
ps aux | grep "node server.mjs" | grep -v grep

# Python process
ps aux | grep "python3.*soniox-server/main.py" | grep -v grep
```

## Keeper & Watchdog

**Durum (11 Tem 2026):** Cron keeper **kayıtlı ve çalışıyor** ✅. EADDRINUSE temiz restart prosedürü belgelendi.

| Bileşen | Path | Durum |
|---------|------|-------|
| Keeper script (çift kopya) | `~/vanitas-web/start_server_wrapper.sh` | ✅ Script hazır |
| Keeper script (hermes/scripts) | `~/.hermes/scripts/start_vanitas_server.sh` | ✅ Script hazır |
| Cron job: `vanitas-server-keeper` | job_id `4d6f090c020f`, `* * * * *` | ✅ **Aktif** |
| Cron job: `🦾 Voice Servis Watchdog` | job_id `41d2e0671bd6`, `*/2 * * * *` | ✅ **Aktif** (voice_watchdog.sh) |

**Setup komutu (yapılacak):**
```
cronjob action=create name=vanitas-server-keeper no_agent=true \
  schedule="* * * * *" script=start_vanitas_server.sh
```

Keeper script'in yaptıkları:
1. `/proc/net/tcp` ile port 3005 ve 8765 kontrolü — **IP'den bağımsız** pattern kullan (`:0BBD.*0A`, `0100007F:0BBD` değil!)
2. Port 3005 açık + Node PID canlı → exit 0 (sessiz)
3. Port var ama PID yok → stale socket temizliği
4. Node.js başlat → Python child process spawn eder
5. 30sn bekle, portlar gelmezse timeout

**Önemli (KRİTİK):** `grep -c` multi-line output dönebilir → `integer expression expected` hatası. Bunun yerine `grep -q` ile exit code kontrolü yap.
```bash
check_port() { cat /proc/net/tcp | grep -q ":0BBD.*0A" && echo 1 || echo 0; }
```

**Ana sayfa routing:** `server.mjs` line 74: `if (urlPath === '/') urlPath = '/full-duplex.html';` — root path full-duplex'i açar. Half-duplex `/index.html` adresinde fallback.**

## Dış Erişim: Cloudflared Quick Tunnel (PRIMARY — container içi)

**Durum (13 Tem 2026):** Windows/Tailscale'e bağımlılık bitti. Cloudflared quick tunnel container içinde cron keeper ile çalışır. URL her restart'ta değişir — cron `vanitas-tunnel-keeper` (job_id `3582974cda8c`, `*/2 * * * *`, no_agent) tüneli canlı tutar ve URL değişirse bildirim gönderir.

Script: `~/.hermes/scripts/vanitas_tunnel.sh`
```bash
# Manual start
/home/ubuntu/.hermes/bin/cloudflared tunnel --url http://host.docker.internal:3005 --no-autoupdate
```

**Kritik:** `--url` parametresi `host.docker.internal:3005` olmalıdır (`0.0.0.0:3005` değil). Farklı Docker network katmanları nedeniyle container içinden Windows host'una `host.docker.internal` üzerinden erişilir.

**Setup (ilk sefer için, bir kere yapıldı):**
```bash
cronjob action=create name=vanitas-tunnel-keeper no_agent=true \
  schedule="*/2 * * * *" script=vanitas_tunnel.sh
```

### Telefondan erişim: HTTPS zorunluluğu

Cloudflared quick tunnel otomatik HTTPS sağlar — telefon tarayıcısı mikrofon kullanabilir. URL `https://<random>.trycloudflare.com` formatındadır.

**Not:** URL her restart'ta değişir. Keeper cron (`vanitas_tunnel.sh` v2) sadece URL değiştiğinde bildirim gönderir — tünel stabil çalışırken sessizdir (cron no_agent=true → empty stdout = silent). Kullanıcı bildirimi görmezse tüneli kontrol etmek için:
```bash
cat /tmp/cloudflared_tunnel_url.txt
```

## Tailscale Funnel (DEPRECATED — Windows bağımlı)

**Durum (11 Tem 2026):** ✅ Tercih edilen yöntem. Cloudflare quick tunnel fallback olarak korunuyor. URL: `https://sakabato.tail9c7788.ts.net`

| Özellik | Değer |
|---------|-------|
| Funnel URL | `https://<hostname>.tailXXXXX.ts.net` (port belirtmeye gerek yok — Funnel port 3005'e yönlendirir) |
| Protokol | HTTPS (Let's Encrypt otomatik) |
| Setup | `tailscale funnel 3005` — tek komut |
| Maliyet | Ücretsiz |
| Uptime | ✅ Stabil |

**Setup (Windows PowerShell — Admin):**
```powershell
tailscale funnel on          # ilk seferde
tailscale funnel 3005        # port'u aç
```

### Telefondan erişim: HTTP vs HTTPS (KRİTİK)

Tailscale **Funnel URL** (`https://...ts.net`) otomatik HTTPS sağlar — telefon tarayıcısı mikrofon kullanabilir. Tailscale **IP adresi** (`http://100.x.x.x:3005`) HTTP'dir — **mobil tarayıcı mikrofon erişimini engeller** (güvenlik politikası).

**Doğru:** `https://sakabato.tail9c7788.ts.net` ✅ mikrofon çalışır
**Yanlış:** `http://100.79.243.41:3005` ❌ mikrofon bloklanır (Chrome/Brave fark etmez)

Kullanıcıya Tailscale Funnel'ı açtıktan sonra hostname'i göster:
```powershell
tailscale funnel 3005
# → https://<hostname>.tailXXXXX.ts.net   <-- BUNU KULLAN
```

### Windows Firewall Kuralı

Tailscale Funnel port 3005'i kullanıcıya ulaştırabilmesi için Windows güvenlik duvarından geçiş izni gerekebilir:

```powershell
# PowerShell (Yönetici) — bir kere yeter
netsh advfirewall firewall add rule name="Vanitas Voice (Tailscale)" dir=in action=allow protocol=TCP localport=3005
```

**Pitfall:** Kullanıcıya `netsh` komutu gönderildiğinde **UAC onayı** gerekebilir. PowerShell'i yönetici olarak açması gerektiğini açıkça belirt. Kullanıcı UAC onayını atlarsa `access denied` hatası alır.

### UAC/UYARI İletişimi

Kullanıcıya PowerShell komutları gönderirken **ilk satırda PowerShell'i Yönetici olarak açması gerektiğini** belirt. Aksi halde `tailscale funnel` ve `netsh` komutları yetki hatası verir.

**Örnek ileti:**
> PowerShell'i **Yönetici olarak açıp** şu komutu çalıştır:
> ```powershell
> tailscale funnel 3005
> ```

### Telefondan erişilemiyor — Debug Sırası

**Mimari kısıtlama:** Tailscale Windows tarafında (sakabato) çalışır. Vanitas Docker container içinde olduğu için Windows Tailscale'ini kontrol edemez — sadece sen bilgisayar başında kontrol edebilirsin.

**Olası sebepler (dışarıdan kontrol edilemez, Windows'ta PowerShell ile debug edilmeli):**

| Sebep | Kontrol | Çözüm |
|-------|---------|-------|
| Windows kapalı / uyku | Bilgisayar açık mı? | Aç / uyandır |
| Tailscale kapalı | `tailscale status` | `tailscale up` ile başlat |
| Funnel ayarı kaybolmuş | `tailscale funnel status` | `tailscale funnel 3005` ile yeniden aç |
| Tailscale hostname değişmiş | `tailscale status` → hostname | Yeni URL'yi kullan |

**Kullanıcıya söylenecek:** "Tailscale Windows'ta çalışıyor, ben Docker içinden kontrol edemiyorum. Bilgisayarının başına geçince PowerShell (Admin) açıp `tailscale funnel status` ile kontrol eder misin?"

### Acil Çözüm: Cloudflared Fallback

Tailscale çalışmıyorsa cloudflared quick tunnel ile geçici URL oluştur:

```bash
# cloudflared binary yolu
/home/ubuntu/.hermes/bin/cloudflared tunnel \
  --url http://host.docker.internal:3005 \
  --no-autoupdate
```

**Not:** Sunucuya container içinden `host.docker.internal:3005` ile erişilir (Docker network). Bu URL geçicidir — cloudflared durdurulunca değişir.

## Cloudflare Tunnel (⚠️ FALLBACK — Tailscale düştüğünde kullan)

Quick tunnel birincil yöntem değil (Tailscale Funnel tercih edilir). Ama Tailscale çalışmadığında **geçici çözüm** olarak kullanılabilir.

**Kullanım:**
```bash
# Binary PATH'te olmayabilir — full path kullan
/home/ubuntu/.hermes/bin/cloudflared tunnel \
  --url http://host.docker.internal:3005 \
  --no-autoupdate
```

**Sorunları:**
- URL her restart'ta değişir
- Uptime garantisi yok
- Mobilde WebSocket kopmaları olabilir
- Sadece Tailscale düştüğünde geçici olarak kullan

## API Keys & Environment

`~/vanitas-web/soniox-server/.env`:
```
SONIOX_API_KEY=<shared-key>
SONIOX_API_KEY_TTS=<same-or-different-key>  # AYRI SET EDİLMELİ — boş olursa TTS bağlanamaz
OPENAI_API_KEY=<groq-api-key>               # isim karışıklığı: Groq key
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.3-70b-versatile
WEBSOCKET_HOST=127.0.0.1                    # IPv6 sorunlarını önlemek için
WEBSOCKET_PORT=8765
SCRIPTS_PATH=~/.hermes/scripts

## Session Kaydı (Debugging) — RECORD_SESSION

**Amaç:** Edel'in test konuşmalarını kaydedip sonradan incelemek. Ses kesilmesi, gecikme, "canım" fazlalığı gibi sorunları tespit etmek için kullanılır.

**Aktifleştirme:** `RECORD_SESSION=true` ortam değişkeni ile Python server başlatılır:
```bash
cd ~/vanitas-web && RECORD_SESSION=true node server.mjs
```
Node.js `spawn` ile `...process.env`'i Python'a geçirdiği için bu yeterlidir.

**Kaydedilenler:**
- `mic.pcm` / `mic.wav` — Mikrofondan gelen ham PCM (16kHz mono)
- `tts.pcm` / `tts.wav` — Vanitas TTS çıktısı (24kHz mono)
- `transcript.txt` — Zaman damgalı transkript + LLM yanıtları + olaylar

**Dosya yolu:** `/tmp/vanitas-recordings/<session-uuid>/`

**Kapatma:** RECORD_SESSION kaldırılır veya `false` yapılırsa recorder sıfır overhead ile çalışmaz.

**Önemli:** Debug aracıdır. Test bittiğinde kapatılmalıdır.

## Voice Kalite Sorunu Teşhisi

Kullanıcı "TTS geç cevap veriyor", "çıktı kalitesi bağlamdan kopuk", veya **"beni duymuyor / tepkisiz"** derse aşağıdaki sırayla teşhis et.

**🚨 EN SIK SEBEP:** Eğer "Bağlandı, konuşabilirsin" yazıyor ama hiç cevap alınamıyorsa → %90 Echo Loop. Direkt Adım 0'dan başla.

Tam teşhis referansı: `references/voice-quality-diagnostics-11-tem-2026.md`

### 0. Barge-in Echo Loop — "Beni duymuyor" (EN SIK — 12 Tem 2026)

```bash
# Echo loop teşhisi: excessive VAD speech start events
tail -200 /home/ubuntu/vanitas-server-output.log | grep "User speech start" | wc -l
# Normal: 1-2/konuşma. Eğer 10+ varsa → echo loop.
```

**Kök neden:** `full-duplex.html`'de `processor.connect(audioCtx.destination)` mikrofon çıkışını hoparlöre bağlar → TTS sesi mikrofona geri döner → VAD loop → LLM sürekli iptal.

**Fix:** GainNode(0) ile sessiz çıkış (bkz: Frontend → Barge-in Echo Loop bölümü). **Tamamlayıcı fix:** TTS oynarken `onaudioprocess`'e `if (isSpeaking) return;` ekle — mikrofonu susturur. Ama bu tek başına yetmez — TTS bitince `playNextChunk()`'ta `isSpeaking = false` resetlenmeli (yoksa mikrofon sonsuz susar).

### VAD Türkçe Tuning (13 Tem 2026)

**Sorun:** Kullanıcı cümle ortasında kesiliyor, konuşmanın sonu algılanamıyor, veya konuşma erken bitmiş sayılıyor.

**Sebep:** Silero VAD varsayılan `min_silence_duration_ms=300ms` Türkçe için çok kısa. Doğal Türkçe konuşmada 300-500ms arası duraklamalar normaldir (kelime arası nefes, düşünme durağı). VAD bu duraklamalarda hemen "konuşma bitti" sinyali gönderir → cümle kesilir.

**Çözüm (main.py'de VADProcessor kurulumu):**
```python
VADProcessor(
    sample_rate=params.audio_in_sample_rate,
    min_silence_duration_ms=600,   # 300→600ms: Türkçe için
    threshold=0.4,                  # 0.5→0.4: daha hassas
)
```

| Parametre | Varsayılan | Türkçe için | Etkisi |
|-----------|-----------|-------------|--------|
| `min_silence_duration_ms` | 300 | **600** | Doğal duraklamalarda kesmez |
| `threshold` | 0.5 | **0.4** | Daha hassas, fısıltıyı da algılar |

**Teşhis:** RECORD_SESSION=true ile kayıt al, transcript.txt'te `[EVENT] user_speech_end` zaman damgalarına bak. Konuşma başladıktan 300-500ms sonra `user_speech_end` geliyorsa VAD çok erken tetikleniyor.

**Ek not:** AudioWorklet her process() çağrısında çok küçük chunk'lar gönderir (128 örnek = 2.67ms). Bu da sunucuda binden fazla küçük WebSocket mesajına yol açar. İdeal çözüm: worklet içinde PCM buffer'ı biriktirip 50-100ms'de bir göndermek. Ancak VAD buffer'ı zaten 512 örnekte bir işlediği için şu an acil sorun değil.

### 1. Log ve Port Kontrolü

```bash
# Sunucu çalışıyor mu?
cat /proc/net/tcp | grep -E ":0BBD|:223D"
# Beklenen: 2 satır (3005 + 8765). Tek satır gelirse Python server başlamamış.

# Python süreci var mı?
ps aux | grep "soniox-server/main.py" | grep -v grep

# Son loglar
tail -30 /home/ubuntu/vanitas-server-output.log
```

### 2. EADDRINUSE — Keeper Restart Döngüsü

Log'da aşağıdaki pattern varsa sunucu sürekli restart döngüsünde:
```
[Server] Port 3005 in use, retrying in 2s...
[Server] Fatal: listen EADDRINUSE
❌ Node.js died (8s)
```

**Kök neden:** Keeper script port var ama PID yok durumunda socket'i temizlemeye çalışır ama port bazen TIME_WAIT durumunda kalır. Node.js'in built-in retry'i (3 deneme) yetmezse keeper fail eder. Aynı anda birden fazla Node.js process'i port'u tutuyor olabilir.

**Çözüm — temiz restart:**
```bash
pkill -f "node server.mjs" 2>/dev/null
pkill -f "soniox-server/main.py" 2>/dev/null
sleep 3
cd /home/ubuntu/vanitas-web && node server.mjs >> /home/ubuntu/vanitas-server-output.log 2>&1 &
# 15-20sn bekle, her iki port da gelmeli
```

### 3. LLM Gecikmesi Teşhisi

| Durum | Olası Sebep | Çözüm |
|-------|------------|-------|
| Genel yavaşlık | `tools=[]` + `tool_choice="auto"` | Fix deploy edildi (bkz: ilgili pitfall) |
| İlk token geç | VAD model warmup / cold start | 2. konuşma hızlanır. Cache'de model varsa ~3sn |
| Türkçe kalitesiz | `llama-3.3-70b-versatile` sınırlı | `llama-4-scout-17b` veya `llama-3.1-8b-instant` dene |
| Cevaplar bağlamsız | Sistem prompt çok minimal | `tools.py`'de prompt'u genişlet. Referans: `references/voice-system-prompt-11-tem-2026.md` |

### 4. tools=[] Fix Durumu (11 Tem 2026 — DEPLOY EDİLDİ)

**Sorun:** `main.py` → `LLMProcessor(tools=get_tools())`, `get_tools()` boş array döner. `llm.py`'de `tools=[]` + `tool_choice="auto"` LLM'e her seferinde "araç seçmeli miyim?" diye düşündürür → latency artar.

**Fix:**
1. `tools.py` (line 18-20): `get_tools()` → `return None` (boş array değil)
2. `llm.py` (line 81-86): `__init__`'de `if tools:` kontrolü — None ise array oluşturma
3. `llm.py` (line 200-203): Sadece `self._tool_descriptions is not None` ise `tools` ve `tool_choice` parametrelerini API çağrısına ekle

**Tools'lu config için:** Eğer gerçek tool fonksiyonları eklenirse (`get_tools()` boş değil), `tool_choice="auto"` doğrudur. Sorun sadece boş array + auto kombinasyonunda.

### 5. Voice Sistem Prompt'unun Önemi

Voice agent **Hermes API'yi kullanmaz** — Groq'a direkt gider (`OPENAI_BASE_URL=https://api.groq.com/openai/v1`). Bu yüzden:
- Hermes'in bağlamı (SOUL.md, COMPASS, wiki, memory) voice'de yok
- Sistem prompt'u elle yazılmalı
- Vanitas kişiliği prompt'a gömülmeli

**Kaynak:** `~/vanitas-web/soniox-server/tools.py` — `get_system_message()` fonksiyonu.
**Referans:** `references/voice-system-prompt-11-tem-2026.md`

**Prompt'un içermesi gerekenler:**
- Vanitas'ın sesli görüşme kişiliği
- Kısa cevap kuralı (2-3 cümle max)
- Hitap şekli (çok nadiren "canım", direkt hitapsız konuş da olur)
- Bilmediğinde uydurmama kuralı
- Ses tonu: sıcak, samimi, muzip
- Emoji yasak (sesli görüşmede anlamsız)

### 6. Neden Hermes API Değil? (Kullanıcı Sorusu)

Kullanıcı sorarsa: "Sistem prompt girmeye neden ihtiyacımız var? Hermes API'den çekmiyor muyuz?"

Cevap: Voice agent low-latency için **Groq'a direkt gider** — Hermes üzerinden gitseydi tüm skill'ler, memory, wiki yüklenirdi → 4-6 saniye gecikme. Sesli görüşmede 1sn bile kötü hissettirir. Bu yüzden Groq hızlı yol, elle yazılmış sistem prompt'u ile kullanılır. Arzu edilirse hybrid yapılabilir (acil bilgi için Hermes API'sine ayrıca danışma).

## Pitfalls

### Python Server
- **requires-python = ">=3.13"** → `>=3.11` olarak değiştirilmeli (pyproject.toml)
- **Silero VAD model download:** İlk çalıştırmada ~30sn, sonra cache (~3sn)
- **WEBSOCKET_HOST:** Varsayılan `localhost` IPv6'ya çözülebilir → `127.0.0.1` override edilmeli
- **Background stabilite:** Python asyncio server background'da stabil kalamayabilir → cron keeper gerekli
- **EADDRINUSE port çakışması:** Keeper script bazen stale socket ile yeni process arasında çekişmeye girer. Bakınız: Voice Kalite Sorunu Teşhisi → EADDRINUSE bölümü.
- **`tools=[]` + `tool_choice="auto"` latency (FIXED 11 Tem 2026):** Bu sorun `tools=None` ile çözüldü. Detay: Voice Kalite Sorunu Teşhisi → tools=[] Fix Durumu. Eğer tekrar ortaya çıkarsa `main.py` line 115'te `tools=get_tools()` ve `llm.py` line 200-203'ü kontrol et.

- **STT `_receive_task_handler` sessiz çökme (KRİTİK — 12 Tem 2026 FIX):** `stt.py` `_receive_task_handler` içinde `content["tokens"]` direkt key access kullanır. Soniox bazen `tokens` içermeyen mesajlar gönderebilir (sadece `final_audio_proc_ms` gibi timing bilgisi). Bu durumda `KeyError` alır ve **catch-all exception handler olmadığı için arka plan task'i SESSİZCE ölür.** Belirti: VAD konuşmayı algılar ama hiç transkripsiyon gelmez, LLM hiç tetiklenmez. **Fix:** `content.get("tokens")` kullan + `except Exception as e:` catch-all ekle + hata durumunda `ErrorMessage` gönder. Ayrıca Soniox'tan gelen mesajların `tokens` listesi boş olabilir (`[]`) — bu normaldir, sessizlik için boş token döner. `if tokens:` kontrolü ile boş listeyi atla.

- **LLM sadece Soniox endpoint'inde tetiklenir (KRİTİK — 12 Tem 2026 FIX):** `llm.py` `process()` sadece `TranscriptionEndpointMessage` geldiğinde `_generate_llm_response()` çağırır. Ama Soniox endpoint detection güvenilmez olabilir (gürültü, kısa konuşma). Sonuç: VAD konuşma bitişini algılasa bile LLM hiç çalışmaz. **Fix:** `UserSpeechEndMessage` handler ekle — VAD konuşma bitti dediğinde, eğer STT'den transkripsiyon metni gelmişse (`has_user_text` kontrolü), LLM'i tetikle. Bu çift tetikleyici (Soniox endpoint VEYA VAD end) sağlamlık sağlar.

- **Node.js API key injection (12 Tem 2026 FIX):** Python `.env` dosyasındaki API key'ler bayatlayabilir veya placeholder (`***`) olabilir. Node.js Bitwarden'dan güncel key'leri çekip `spawn({env: {...}})` ile Python'a geçirmeli. `startSonioxPythonServer()` fonksiyonu `async` yapılmalı, `getGroqKey()` ve `getSonioxKey()` await edilmeli. `.env`'deki `OPENAI_API_KEY` placeholder'ı Bitwarden'dan gelen gerçek key ile override edilir (dotenv `override=False` default). Ayrıca `SONIOX_API_KEY_TTS` çift tanımlanmasına dikkat — ikinci boş tanım birinciyi ezer.

### Server Restart Gerekliliği (KRİTİK — 13 Tem 2026)

**Python ve Node.js sunucuları kod değişikliklerinden sonra OTOMATİK reload YAPMAZ.** Uzun süre çalışan process'ler oldukları için tools.py, server.mjs, full-duplex.html gibi dosyalardaki değişiklikler restart gerektirir.

**Belirti:** Kullanıcı "değişiklik olmamış" veya "hala eskisi gibi" derse → büyük ihtimal server restart edilmemiştir.

**Çözüm — temiz restart:**
```bash
pkill -f "node server.mjs" 2>/dev/null
pkill -f "soniox-server/main.py" 2>/dev/null
sleep 3
# Node.js başlayınca Python child process'ini otomatik spawn eder
cd /home/ubuntu/vanitas-web && node server.mjs >> /home/ubuntu/vanitas-server-output.log 2>&1 &
sleep 20
# Port kontrolü: 2 satır gelmeli (3005 + 8765)
cat /proc/net/tcp | grep -E ":0BBD|:223D"
```

**Pitfall:** Sadece bir process'i kill etmek yetmez — Node.js Python'u child olarak spawn ettiği için, Node.js öldüğünde Python da gider. Ama Python tek başına restart edilirse Node.js proxy'si olmadan çalışmaz. Her zaman **önce Node.js'i kill et, yeniden başlat.** Node.js `startSonioxPythonServer()` ile Python'u otomatik başlatır.

**Pitfall 2:** Değişiklik sadece Python tarafındaysa (tools.py), Node.js restart'ı yeterlidir — Node.js Python'u yeniden spawn eder. Değişiklik sadece frontend HTML ise (full-duplex.html) restart gerekmez — Node.js statik dosyaları her seferinde diskten okur.

| Değişiklik Yapılan Dosya | Restart Gerekli mi? |
|---|---|
| `public/full-duplex.html` | ❌ Hayır (statik dosya) |
| `public/index.html` | ❌ Hayır |
| `tools.py` | ✅ Evet (Python yeniden başlamalı) |
| `server.mjs` | ✅ Evet (Node.js yeniden başlamalı) |
| `llm.py`, `stt.py`, `tts.py`, `vad.py` | ✅ Evet |
| `.env` | ✅ Evet |

### Node.js Server
- **EADDRINUSE:** Port hemen serbest kalmayabilir → server.mjs'de built-in retry (3 deneme, 2sn ara)
- **Port tespiti:** Container'da `lsof` çalışmayabilir → `/proc/net/tcp` kullan. **IP'den bağımsız pattern** kullan (`:0BBD.*0A`) — Node.js `0.0.0.0:3005` veya `127.0.0.1:3005` dinlerken farklı pattern gerekir.
- **Ana sayfa routing:** `server.mjs` line 74: `if (urlPath === '/') urlPath = '/full-duplex.html';` — root path full-duplex'i açar.
- **Soniox TTS API key:** `SONIOX_API_KEY_TTS` ayrı set edilmezse TTSProcessor bağlanamaz → session hemen kapanır
- **Çift sistem prompt'u (KRİTİK — 12 Tem güncelleme):** `server.mjs` line 112'de `/api/chat` handler'ında **hardcoded bir sistem prompt'u daha var!** Bu prompt sadece REST API (half-duplex fallback) için geçerli. Full-duplex `tools.py`'deki `get_system_message()` fonksiyonundan farklıdır. İkisi bağımsız kod yollarıdır — prompt güncellenirken **her ikisi de** güncellenmeli. Özellikle "canım" kullanım kuralı, kimlik tanımı ve kısa cevap kuralı her iki prompt'ta da aynı olmalı. Birini değiştirip diğerini unutursan half-duplex fallback'te eski davranış devam eder → "benim adım vanitas" / "her cümlede canım" gibi hatalar.

### Diagnostik: Hangi sayfa yükleniyor? (11 Tem 2026)

Tailscale/cloudflared URL'inden bağlanırken hangi sayfanın açıldığını kontrol et:

| Belirti | Muhtemel sebep | Kontrol |
|---------|---------------|---------|
| REST `/api/chat` + `/api/stt` isabet alıyor | `/index.html` (half-duplex) yükleniyor | `server.mjs` line 74: `if (urlPath === '/') urlPath = '/full-duplex.html'` olmalı |
| WebSocket `/ws/soniox` isabet alıyor | `/full-duplex.html` yükleniyor ✅ | Doğru |
| TTS sesi robotik (EmelNeural) | Edge TTS `/api/tts` kullanılıyor | full-duplex sayfasında Soniox TTS kullanılır, Edge TTS sadece half-duplex'te |
| "Benim adım vanitas" gibi kimlik hataları | `server.mjs` içindeki **hardcoded eski prompt** kullanılıyor | `server.mjs` line 112'deki `system` mesajı + `tools.py`'deki prompt aynı olmalı |

**KRİTİK:** `server.mjs`'de `/api/chat` handler'ında (line 112) **hardcoded bir system prompt daha var!** `tools.py`'deki prompt'u güncellemek yetmez — `server.mjs`'deki prompt da güncellenmeli. İkisi ayrı pipeline: REST API ve WebSocket full-duplex farklı kod yolları kullanır.

### Frontend

#### 🚨 Barge-in Echo Loop — "Beni duymuyor / tepkisiz" Teşhisi (11 Tem 2026)

**Belirti:** Kullanıcı "Bağlandı, konuşabilirsin" yazıyor ama konuşunca hiç cevap alamıyorum der. Sayfa yüklü, WebSocket bağlı, ama cevap yok.

**Kök neden:** `full-duplex.html`'de `processor.connect(audioCtx.destination)` mikrofon çıkışını direkt hoparlöre bağlar → TTS sesi mikrofona geri döner → Silero VAD sürekli "User speech start" tetikler → LLM cevabı her seferinde iptal edilir. Sonuç: sistem çalışıyor GÖRÜNÜR ama hiç cevap üretemez.

**Log'da teşhis:** `tail -100 /home/ubuntu/vanitas-server-output.log | grep "User speech start"` — normalden çok daha sık (her 2-3 saniyede 1) "User speech start detected - cancelling LLM generation" görünüyorsa echo loop var.

**Fix:** `full-duplex.html`'de yakalama nodu (`captureNode` — AudioWorkletNode veya ScriptProcessorNode) doğrudan `audioCtx.destination`'a değil, GainNode(0) üzerinden bağlanır:
```javascript
// GainNode(0) ile sessiz çıkış — capture çalışır ama hoparlöre ses gitmez
silentGain = audioCtx.createGain();
silentGain.gain.value = 0;
captureNode.connect(silentGain);
silentGain.connect(audioCtx.destination);
```
Bu hem AudioWorkletNode'un hem de ScriptProcessorNode'un çalışmasını sağlar (çıktı bağlantısı zorunludur) hem de echo'yu önler.

**Fix sonrası log:** LLM generation task'ları **tamamlanmaya başlamalı** (`llm_first_token_ms`, `llm_total_ms` metrikleri görünmeli). "User speech start" hâlâ görünür ama sıklığı düşer ve LLM cevapları başarıyla üretilir.

- **MediaRecorder (half-duplex):** İlk webm chunk EBML header — flush'larda korunmalı
- **ScriptProcessorNode (full-duplex):** Hoparlöre de bağlı → echo olabilir → GainNode(0) ile kıs. **Kontrol:** `full-duplex.html`'de `processor.connect(audioCtx.destination)` direkt bağlantı varsa ECHO LOOP yapar. GainNode(0) ile değiştir. Detaylı teşhis için yukarıdaki Barge-in Echo Loop bölümüne bak.
- **ScriptProcessorNode (full-duplex fallback):** Sadece AudioWorklet desteklenmediğinde kullanılır. `captureNode.connect(audioCtx.destination)` çağrılmazsa `onaudioprocess` tetiklenmez — ZORUNLU. **Ama tek başına yeterli değil** — GainNode(0) ile sessiz çıkışa bağlanmalı. Eğer ScriptProcessor'a düşülmüşse ve mikrofon çalışmıyorsa önce AudioWorklet'i kontrol et (çok eski tarayıcı).
- **getUserMedia:** HTTPS ister (localhost ve Cloudflare tunnel'da OK)
- **Full-duplex için:** `ws.binaryType = 'arraybuffer'` — binary mesajlar
- **AudioContext leak (KRİTİK):** Her `startSession()`'da yeni `AudioContext` açılır, eskisi `close()` ile kapatılmazsa mobilde 2-3 konuşmada kilitlenme. `initAudio()` içinde önce `audioCtx.close()`, sonra yeni context oluştur.
- **Mobile suspend (11 Tem 2026 FIX UYGULANDI):** Mobil tarayıcılar `AudioContext`'i `suspended` durumda başlatır → `onaudioprocess` tetiklenmez → kullanıcı duyulmaz. Fix: `startMicCapture()` içinde `audioCtx.state === 'suspended'` kontrolü + `await audioCtx.resume()`. Bu fix `full-duplex.html` line 231-237'ye eklendi. **Pitfall:** Bu satırlar olmadan mobil cihazlarda mikrofon sessiz kalır, hiçbir hata mesajı gösterilmez — kullanıcı "beni duymuyor" der ama sebebini göremez.
- **WebSocket onclose null (KRİTİK):** `disconnectWs()` içinde `ws.onclose = null` yapılırsa beklenmedik kopmalarda hiçbir cleanup çalışmaz, arayüz "Bağlanıyor..." da takılı kalır. Çözüm: `onclose` handler'ı her zaman cleanup yapmalı, sadece `disconnectWs()` isteyerek kapattığında `wasActive` kontrolü ile ayırt edilmeli.
- **Soniox ses benzerliği (13 Tem 2026 — Edel tespiti):** Grace ve Maya gibi kadın sesleri Türkçe'de birbirine çok benzer gelebilir. Soniox tüm sesleri 60+ dilde aynı tınıyı koruyacak şekilde tasarladığı için, aynı cinsiyetteki sesler arasındaki fark incedir. Daha belirgin bir değişiklik için **erkek sesi** (Daniel, Noah, Jack) veya farklı aksanlı ses (Arjun, Rafael, Oliver) denenmeli. Voice cloning (20sn referans klip) en belirgin farkı verir.** `full-duplex.html` line 480 — `voice=` parametresi **Soniox ses adı** olmalı (`Grace` — güncel), **asla Edge TTS kodu** (`tr-TR-EmelNeural`) değil! Yanlış ses kodu gönderildiğinde Soniox default İngilizce sese düşer → "TTS İngilizce konuşuyor" şikayeti. Geçerli sesler: `Grace` ✅ (aktif), `Emma`, `Nina`, `Maya`, `Mina`, `Claire`. Tam liste: `references/soniox-tts-voices.md`. Tüm 28 ses Türkçe dahil 60+ dili destekler — dil seçimini `voice` değil `language=tr` parametresi belirler.
- **Soniox Voice Cloning (13 Tem 2026):** `https://soniox.com/docs/tts/concepts/voice-cloning` — 20sn referans klip ile özel ses klonu oluşturulabilir. Tüm 60+ dilde çalışır (Türkçe dahil). Organizasyon başına 20 ses limiti. Klon ses UUID ile çağrılır: `"voice": "21b9c8e2-..."`. Referans: `references/soniox-tts-voices.md`.
- **Soniox TTS Türkçe desteği:** "Grace/Maya İngilizce olabilir" yanılgısına düşme. Soniox: **her ses 60+ dili destekler.** Dil seçimini `voice` değil `language=tr` parametresi belirler. Kaynak: https://soniox.com/docs/tts/concepts/voices. Voice cloning de tüm dillerde çalışır.
- **LLM rol karmasasi (13 Tem 2026 — FIX EDİLDİ):** Sistem prompt'u "**Sen Vanitas'sin** — Edel'in yapay zeka yol arkadasi" şeklindeydi. Model Türkçe'deki bu ifadeyi karşısındakine söylenmiş gibi yorumluyor — yani Edel "Adın ne?" diye sorunca model "**SEN** Vanitas'sin" diyor (kullanıcıya Vanitas diye hitap ediyor). **Fix:** Prompt değiştirildi → "**Senin adın Vanitas. Karşındaki kişi Edel.** Sen onun yapay zeka yol arkadaşısın." Bu ayrım sayesinde roller net: konuşan = Vanitas, karşıdaki = Edel. Aynı fix her iki prompt'ta da uygulandı (tools.py + server.mjs L112).
- **Soniox tts-rt-v1 invalid voice:** Hata `400 Invalid voice 'Alina' for model 'tts-rt-v1'` — Alina geçerli bir Soniox TTS sesi DEĞİL. Doğru sesler: `Grace` (aktif), `Maya`, `Nina`, `Emma`, `Claire`, `Mina`. Tam liste: `references/soniox-tts-voices.md`.
- **HTTPS zorunluluğu (mobil):** Tarayıcılar `getUserMedia` (mikrofon) için HTTPS ister. Tailscale HTTP IP (`http://100.x.x.x:3005`) mobilde çalışmaz. Tailscale Funnel URL'si (`https://*.ts.net`) HTTPS sağlar. Localhost'ta HTTP çalışır ama telefonda kesinlikle HTTPS gerekli.
- **Microphone stuck muted after TTS — `isSpeaking` flag leak (12 Tem 2026 FIX):** `playNextChunk()` fonksiyonu playback queue boşaldığında `isPlaying = false` yapıyor ama `isSpeaking`'i resetlemiyor. Eğer `onaudioprocess`'te `if (isSpeaking) return;` varsa (echo önleme), TTS bittiğinde mikrofon sonsuza kadar susar. Fix: `playNextChunk()` içinde queue boşken `isSpeaking = false; setStatus('listening', 'Dinliyorum...');` ekle. Aksi halde kullanıcı konuşur, transkripsiyon alınmaz, hiçbir tepki olmaz.\n- **Mobile browser caching (12 Tem 2026 FIX):** Safari/iOS `Cache-Control: no-cache` header'ını göz ardı edebilir. Fix: `full-duplex.html`'e meta tag ekle: `<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">` + `Pragma` + `Expires`. Ayrıca kullanıcıya \"sayfayı kapatıp gizli modda yeniden aç\" de. Cache yüzünden eski JS (hatalı voice kodu, eksik AudioContext resume, echo loop) yüklenmeye devam edebilir.\n- **Sessiz mikrofon hatası (11 Tem 2026 FIX UYGULANDI):** `startMicCapture()` hata alırsa orijinal kodda `catch(() => stopSession())` ile sessizce kapanıyordu — kullanıcı ne olduğunu görmüyordu. Fix: `catch((err) => { showError('Mikrofon hatası: ' + err.message); setStatus('error', ...); stopSession(); })` → artık Türkçe hata mesajı gösterir. Bu `full-duplex.html` line 356'da uygulandı.

### Full-Duplex Client (full-duplex.html) Pitfalls (12 Tem 2026)

- **Konuşma ortasında kesilme (13 Tem 2026 — AÇIK SORUN):** Kullanıcı cümlesini bitirmeden Vanitas susuyor veya "anladım" deyip cevap üretiyor. Muhtemel sebepler: (1) Soniox endpoint detection (`max_endpoint_delay_ms=1000`) çok agresif — 1sn sessizlikte cümleyi bitmiş sayıyor. (2) Silero VAD threshold konuşma bitişini erken algılıyor. (3) Flush timeout (`delayed_flush(2.5)`) çok kısa. **Geçici çözüm:** Daha uzun endpoint delay veya daha yüksek VAD threshold. **Kesin çözüm:** RECORD_SESSION=true ile kayıt al, transkriptte hangi noktada kesildiğini tespit et, ona göre parametre ayarla.

- **AudioWorklet ✅ birincil yakalama (13 Tem 2026 — ÇÖZÜLDÜ):** Artık birincil ses yakalama yöntemi. `audioCtx.audioWorklet.addModule(blobUrl)` ile inline Blob URL'den yüklenir. Ayrı thread'de çalıştığı için ana thread'i tıkamaz. iOS Safari 14.5+ destekler. Hata alınırsa ScriptProcessor fallback'i devreye girer. `captureBadge` hangi metodun kullanıldığını gösterir. Eski "ScriptProcessor mobilde güvenilmez" sorunu böylece çözülmüştür.

- **AudioContext suspended (MOBİL KRİTİK):** Mobil tarayıcılar AudioContext'i `suspended` durumda başlatır. `getUserMedia` sonrası `audioCtx.resume()` çağrılmalı.
- **Echo loop → VAD spam:** `processor.connect(audioCtx.destination)` mikrofonu direkt hoparlöre bağlar → TTS sesi mikrofona geri döner → VAD "konuşma var" sanıp sürekli `UserSpeechStart` gönderir → LLM sürekli iptal olur. **Çözüm:** GainNode(0) ile sessiz çıkış.
- **`isSpeaking` takılı kalma:** `playNextChunk()` queue boşaldığında sadece `isPlaying = false` yapar, `isSpeaking` resetlenmez. Sonuç: `if (isSpeaking) return` ile mikrofon sonsuza kadar susar. **Çözüm:** `playNextChunk` boş queue'da `isSpeaking = false` + `setStatus('listening', ...)` yapılmalı.
- **Mikrofon susturma:** `onaudioprocess` içinde `if (isSpeaking) return` — TTS oynarken PCM gönderme, yoksa echo loop.
- **Cache busting mobile:** Safari/Chrome mobil `no-cache` header'ını ignore edebilir. Meta cache-control + Pragma + Expires tag'leri ekle. Gizli modda test et.

- **Ses seviyesi göstergesi (12 Tem 2026 EKLENDİ):** Mobilde ses yakalama sorunlarını teşhis etmek için `full-duplex.html`'e peak level meter + byte sayacı eklendi. Yeşil çubuk hareket etmiyorsa → mikrofon çalışmıyor. Byte sayacı artmıyorsa → ScriptProcessor tetiklenmiyor. Bu diagnostik olmadan "acaba ses gidiyor mu" sorusu cevaplanamaz. Uygulama: `onaudioprocess` içinde `peak` hesapla, `levelFill.style.width` ile göster. `totalBytesSent` sayacını `ws.send` sonrası artır.

### Genel
- **OpenAI key ismi karışıklığı:** `.env`'de `OPENAI_API_KEY` Groq key'ini tutar (API uyumlu). Gerçek OpenAI key değil.
- **Edge TTS fallback:** Soniox TTS çalışmazsa frontend `/api/tts`'e düşer (Edge-TTS CLI)
- **Voice Agent deprecation:** `vanitas-voice-agent` skill'i artık güncel değil — `vanitas-voice-bridge` referans alınmalı
- **Dual-prompt sync:** `server.mjs` line 112'deki hardcoded REST chat prompt'u ve `soniox-server/tools.py`'deki WebSocket prompt'u İKİSİ birden güncellenmeli. Birini değiştirip diğerini unutma.
- **Root routing:** `server.mjs` line 74: `if (urlPath === '/') urlPath = '/full-duplex.html'` — yoksa eski index.html (half-duplex) yüklenir
- **Container'dan Windows erişimi yok:** Tailscale, Docker host (Windows) üzerinde çalışır. Container içinden Windows Tailscale'i kontrol edilemez. Tailscale Funnel sorunlarında doğrudan kullanıcıya Windows'ta PowerShell ile kontrol ettirilir veya cloudflared fallback sunulur.
- **Server'a container'dan erişim:** Node.js `0.0.0.0:3005` dinler, container içinden `host.docker.internal:3005` ile erişilir. Cloudflared tunnel `--url` parametresinde `http://0.0.0.0:3005` değil `http://host.docker.internal:3005` kullanılmalı (farklı Docker network katmanları).
- **Sistem prompt kalitesi (KRİTİK):** `tools.py`'deki sistem prompt'u çok minimaldir (`"Sen Vanitas'sin — Edel'in yapay zeka asistani..."`). Bu şunlara sebep olur: (1) Vanitas kişiliği tam oturmaz, (2) cevaplar bağlamdan kopuk olur, (3) ses tonu tutarsız olur. İyileştirme: SOUL.md'den Vanitas'ın kişilik özelliklerini (sadakat, koruma, sıcaklık, konuşma tarzı) sisteme ekle. Kaynak: `~/vanitas-web/soniox-server/tools.py`.

- **"Canım" aşırı kullanımı (13 Tem 2026 TEKRAR FIX — Edel uyarısı):** Prompt'ta "Edel'e sadece 'canim' diye hitap et" yazılırsa LLM her cümle sonuna "canım" ekler → rahatsız edici. Eski fix "ara sira kullan" yeterli DEĞİL — LLM hâlâ her 2-3 cümlede bir "canım" diyor. **Yeni kural:** "ÇOK NADİREN kullan, belki 5 konuşmada bir. Hiç kullanmasan da olur. Direkt konuşmaya gir, hitap etmeden konuş." Ayrıca "Bilmiyorum, araştırayım mi?" de — "canım" ekleme. Bu kural her iki prompt'ta da (tools.py + server.mjs L112) aynı anda güncellenmeli. Detay: `references/voice-system-prompt-11-tem-2026.md`.

- **Session start auto-greeting (12 Tem 2026 FIX):** `llm.py` line 108-110'da `SessionStartMessage` geldiğinde LLM otomatik cevap üretir. Bu auto-greeting'in TTS sesi mikrofona döner → VAD tetiklenir → LLM iptal olur → kullanıcı "tepkisiz" der. Fix: SessionStartMessage handler'ından `self._active_task = asyncio.create_task(self._generate_llm_response())` satırını KALDIR. LLM sadece kullanıcı konuştuğunda (`TranscriptionEndpointMessage`) cevap üretmeli. Bu fix olmadan full-duplex mobilde neredeyse hiç çalışmaz.

- **Full-duplex vs half-duplex teşhis stratejisi (12 Tem 2026):** Full-duplex çalışmıyorsa önce half-duplex'i test et (`/index.html`). Half-duplex çalışıyorsa sorun full-duplex client kodundadır (WebSocket, PCM, AudioContext), altyapıda DEĞİLDİR (Groq API, Soniox, ağ). Bu teşhis akışı saatler kazandırır.

- **Sunucu/istemci izolasyon testi (12 Tem 2026 — EN GÜVENİLİR TEŞHİS):** Full-duplex "hiç cevap yok" durumunda sorunun sunucuda mı istemcide mi olduğunu KESİN olarak belirlemek için: (1) `edge-tts` ile Türkçe bir WAV oluştur, (2) `ffmpeg` ile 16kHz mono PCM s16le'ye çevir, (3) Python script ile direkt `ws://127.0.0.1:8765` bağlanıp PCM dosyasını chunk'lar halinde gönder, (4) transkripsiyon + LLM cevabı + TTS sesi alınıyorsa → **sunucu MÜKEMMEL çalışıyor, sorun %100 frontend ses yakalamada.** Bu test olmadan saatlerce yanlış yerde debugging yapılır. Test script örneği: `references/server-side-isolation-test.py`.
- **Konuşma hafızası yok:** Her WebSocket session'ı sıfırdan başlar. LLMProcessor `self._messages` listesi sadece o session içinde geçerlidir. Session sona erince kaybolur. Kullanıcı "bağlamdan kopuk" şikayeti yaparsa açıkla: hafıza henüz entegre değil.
- **LLM model seçimi (sesli görüşme için):** Groq modelleri arasında seçim yaparken hız + Türkçe kalitesi dengesi:
  | Model | Hız | Türkçe | Not |
  |-------|-----|--------|-----|
  | `llama-3.3-70b-versatile` (mevcut) | 🟡 orta | 🟢 iyi | Dengeli ama yavaş kalabilir |
  | `llama-4-scout-17b-16e-instruct` | 🟢 hızlı | 🟡 orta | Daha yeni, denenmedi |
  | `llama-3.1-8b-instant` | 🟢 çok hızlı | 🟡 orta | En hızlı seçenek |
  Kullanıcı "TTS geç cevap veriyor" derse → LLM latency büyük ihtimal. Groq'un 250ms TTFB'si ile soniox TTS'in toplamı ~1-1.5s olmalı. Daha yavaşsa `tools=[]` + `tool_choice="auto"` kombinasyonunu kontrol et (yukarıdaki pitfall).

## File Locations

| Dosya | Yol |
|-------|-----|
| Node.js HTTP+WS sunucu | `~/vanitas-web/server.mjs` |
| Python Soniox server | `~/vanitas-web/soniox-server/main.py` |
| Session Recorder (debug) | `~/vanitas-web/soniox-server/session_recorder.py` |
| Vanitas persona + tool defs | `~/vanitas-web/soniox-server/tools.py` |
| Full-duplex frontend | `~/vanitas-web/public/full-duplex.html` |
| Half-duplex frontend | `~/vanitas-web/public/index.html` |
| Keeper script | `~/vanitas-web/start_server_wrapper.sh` |
| Keeper script (cron) | `~/.hermes/scripts/start_vanitas_server.sh` |
| Server log | `/home/ubuntu/vanitas-server-output.log` |

## Load Order (skill transparency)

Bu skill yüklendiğinde:
1. Ana SKILL.md okunur — mevcut durum, pitfall'lar, komutlar
2. Gerekiyorsa `references/soniox-voice-bot-demo.md` — Python mimari detayı
2. Gerekiyorsa `references/nodejs-integration.md` — Node.js proxy + cron detayı (⚠️ **dual-prompt pitfall:** `server.mjs` line 112'de hardcoded prompt var, `tools.py` ile senkronize edilmeli)
3. Gerekiyorsa `references/server-side-isolation-test.md` 🆕 — sunucu/istemci izolasyon testi (PCM dosyası ile WebSocket testi)
4. Gerekiyorsa `references/version-history.md` — eski sürüm referansı
5. Gerekiyorsa `references/voice-system-prompt-11-tem-2026.md` — sesli görüşme system prompt'u referansı
6. Gerekiyorsa `references/voice-quality-diagnostics-11-tem-2026.md` — LLM/TTS/echo kalite sorunları teşhisi (⚠️ EN SIK: echo loop → "beni duymuyor")
\n7. Gerekiyorsa `references/audioworklet-migration-13-tem-2026.md` 🆕 — AudioWorklet ses yakalama mimarisi ve fallback detayı\n8. Gerekiyorsa `references/soniox-tts-voices.md` — ses listesi, cloning, Grace/Emma/Mina alternatifleri\n9. Gerekiyorsa `references/gpt-live-competitive-research-13-tem-2026.md`
10. Gerekiyorsa `scripts/vanitas_tunnel.sh` — cloudflared tunnel keeper (container içi, cron no_agent, URL değişince bildirim)
