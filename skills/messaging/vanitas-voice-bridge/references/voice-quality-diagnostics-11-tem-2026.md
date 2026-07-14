# Voice Quality Diagnostics — 11 Temmuz 2026 (Updated: 12 Tem)

## Şikayetler
- "TTS geç cevap veriyor"
- "Çıktı kalitesi bağlamdan kopuk ve kötü"
- "Beni duymuyor / tepkisiz"
- "Konuşuyorum yazıyor ama cevap yok"
- "benim adım sen vanitas" gibi kimlik hataları
- "TTS sesi İngilizce konuşuyor / kötü"

## Teşhis Akışı (Sırayla)

### 0. Barge-in Echo Loop — "Beni duymuyor" (12 Tem 2026 — EN SIK)

**Belirti:** "Bağlandı, konuşabilirsin" yazıyor ama konuşunca hiç cevap yok. Sayfa yüklü, WebSocket bağlı.

**Log kontrolü:**
```bash
tail -200 /home/ubuntu/vanitas-server-output.log | grep "User speech start"
```
Normalde konuşma başına 1-2 kez görünmeli. **Her 2-3 saniyede bir** "User speech start detected - cancelling LLM generation" varsa → echo loop.

**Kök neden:** `full-duplex.html` line 275'te `processor.connect(audioCtx.destination)` mikrofon çıkışını direkt hoparlöre bağlar. TTS sesi mikrofona geri döner → Silero VAD loop'ta.

**Fix:** GainNode(0) ile sessiz çıkış:
```javascript
silentGain = audioCtx.createGain();
silentGain.gain.value = 0;
processor.connect(silentGain);
silentGain.connect(audioCtx.destination);
```

**Doğrulama:** Fix sonrası log'da `llm_first_token_ms` ve `llm_total_ms` metrikleri görünmeye başlamalı.

### 1. LLM: Groq, Ollama değil

```python
# main.py
OPENAI_BASE_URL = "https://api.groq.com/openai/v1"
OPENAI_MODEL = "llama-3.3-70b-versatile"
```
Kullanıcıya "aslında Groq kullanıyorsun, Ollama değil" diye netleştir.

### 2. `tools=[]` + `tool_choice="auto"` — gereksiz latency (KRİTİK)

```python
# llm.py line 198-203
response = await self._client.chat.completions.create(
    model=self._model, messages=self._messages, stream=True,
    tools=self._tool_descriptions,      # == [] (boş!)
    tool_choice="auto",                   # "araç seçmeye çalış" modu
)
```
LLM her yanıtta "tool seçmeli miyim?" diye karar vermeye çalışır — boş array olsa bile. ~200-500ms ekstra latency.

**Düzeltme:** `tools=None` yap. Sadece gerçek tool fonksiyonları varsa `tools=<list>` + `tool_choice="auto"` kullan.

### 3. Yanlış sayfa yükleniyor — half-duplex vs full-duplex

| Belirti | Sebep | Kontrol |
|---------|-------|---------|
| TTS sesi robotik (EmelNeural) | `/index.html` yükleniyor (half-duplex + Edge TTS) | `server.mjs` line 74: `urlPath = '/full-duplex.html'` olmalı |
| "benim adım vanitas" | `server.mjs` line 112'deki hardcoded eski prompt | `server.mjs`'deki prompt'u `tools.py` ile senkronize et |
| REST `/api/chat` + `/api/stt` isabet alıyor | Half-duplex kullanılıyor | Full-duplex buzzer: WebSocket `/ws/soniox` isabet alıyorsa doğru |
| Soniox TTS İngilizce ses | Frontend `voice=tr-TR-EmelNeural` (Edge kodu!) gönderiyor | `full-duplex.html` line 338: `voice=Maya` olmalı |

**KRİTİK:** `server.mjs` line 112'de `/api/chat` handler'ında hardcoded sistem prompt'u var! Bu REST API yolu. Full-duplex WebSocket `tools.py`'deki prompt'u kullanır. İkisi **bağımsız** — prompt güncellenirken ikisi de güncellenmeli.

### 4. Sistem prompt'u çok minimal / eski sürüm

**Eski prompt (server.mjs line 112):**
```javascript
{ role: 'system', content: "Sen Vanitas'sin - Edel'in yapay zeka asistani. Sicak, samimi, merakli, biraz cilveli konusursun. Kisa ve dogal cevaplar verirsin. Türkçe konusursun." }
```

### 5. Konuşma hafızası yok — Her WebSocket session'ı sıfırdan başlar.

### 6. Sunucu dengesizliği (EADDRINUSE) — Keeper script port çakışması.

### 7. Mobil AudioContext suspended — mikrofon sessiz. Fix: `audioCtx.resume()`.

### 8. Mobil mikrofon hatası sessizce kapanıyor — Fix: Türkçe hata mesajı.

## Fix Durumu (12 Tem 2026)

| Sorun | Durum | Tarih |
|-------|-------|-------|
| Echo loop (GainNode) | ✅ FIXED — `full-duplex.html` GainNode(0) deploy edildi | 12 Tem |
| `tools=[]` + `tool_choice="auto"` | ✅ FIXED — `tools=None` + conditional API params | 11 Tem |
| Sistem prompt minimal | ✅ FIXED — Vanitas kişilikli prompt (tools.py + server.mjs) | 11-12 Tem |
| Yanlış sayfa (half-duplex) | ✅ FIXED — `server.mjs` root → full-duplex.html | 12 Tem |
| Yanlış TTS ses kodu (EmelNeural) | ✅ FIXED — `full-duplex.html` voice=Maya | 12 Tem |
| Mobil AudioContext suspended | ✅ FIXED — `full-duplex.html` resume() eklendi | 11 Tem |
| Sessiz mikrofon hatası | ✅ FIXED — Türkçe hata mesajı | 11 Tem |
| Sunucu EADDRINUSE | ✅ Temizlendi — pkill + fresh restart | 11 Tem |
| Model `llama-3.3-70b` | 🔄 Kalsın (Edel kararı) | 11 Tem |
| Konuşma hafızası yok | 🔄 Planlandı — temel tamamlanınca | - |
| v10.10 Dual-Path | 🔄 Planlandı — temel tamamlanınca | - |
