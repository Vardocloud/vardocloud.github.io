# Multi-Agent Model Selection — Araştırma ve Workaround

## Genel Durum

| Framework | Alt ajana model atama | Esneklik |
|-----------|----------------------|----------|
| **Hermes (delegate_task)** | ❌ Tek global (`delegation.model`) | Config'te 1 değer |
| **Hermes (Kanban)** | ✅ Per-task `model_override` | v0.15.0+ |
| **Claude Code** | ✅ Per-agent YAML | `model: sonnet/opus/haiku` |
| **MetaGPT** | ✅ 3 katmanlı | Action > Role > Global, 28+ provider |
| **AutoGPT** | ✅ Blok seviyesinde | Her OrchestratorBlock bağımsız, 40+ model |
| **CrewAI** | ✅ Native | `agent = Agent(llm="openai/gpt-4o")` |
| **LangGraph** | ✅ Node başına | Her node bağımsız LLM |
| **AutoGen** | ✅ Native | `model_client=OpenAIChatCompletionClient(model="...")` |
| **Agno** | ✅ Native | `Agent(model=Gemini(id="..."))` |

## Hermes Dokümantasyonu vs Gerçek (30 Mayıs 2026)

| Kaynak | Diyor ki |
|--------|----------|
| Resmi doküman | `delegation.model` tek global |
| GitHub PR #35033 | `feat(delegate): per-task model/provider overrides` **merge edildi** |
| v0.15.0 sürüm notu | "Per-task model overrides" (Kanban için) |
| **Gerçek (test edildi)** | `delegate_task`'te çalışmıyor ❌, Kanban'da çalışıyor ✅ |

**Sonuç:** Hermes resmi dokümanı güncel değil. PR #35033 merge edilmiş ama
`delegate_task` tool'una henüz yansımamış. Per-task override şu an sadece Kanban'da.

## Cloudflare UA Block — Pollinations 403 Sorunu (ÇÖZÜLDÜ ✅ 30 Mayıs 2026)

**GERÇEK KÖK NEDEN:** Cloudflare browser signature ban (error 1010). Python'un varsayılan User-Agent'ı bloklanıyor.
Pollinations içerik filtresi, `Pollinations-Safe` header'ı, tool sayısı, system prompt boyutu — bunların hiçbiri sorun değildi.

**Yanlış teşhis zinciri (3 saatlik debugging):**
İçerik filtresi → Pollinations-Safe header → system prompt kısaltma → tool sayısı düşürme → model değiştirme → hepsi gereksizdi.

**Debugging dersi:** 403/block → ÖNCE HTTP katmanı (UA, Cloudflare, IP), SONRA içerik/prompt. Occam's razor.

**Çözüm:** Proxy (systemd servis `pollinations-proxy.service`) → sadece browser UA header'ı ekler, başka manipülasyon yapmaz.
Detay: `references/cloudflare-ua-bypass.md`

## Delegation Config (ÇALIŞIYOR ✅)

```yaml
delegation:
  provider: pollinations
  model: deepseek  # veya minimax, kimi, qwen-coder-large...
  base_url: http://127.0.0.1:19999/v1  # ← proxy
  api_key: sk_2qC...4Tsc
```

Proxy kurulumu ve tüm Pollinations trafiğinin yönlendirilmesi: `references/cloudflare-ua-bypass.md`

## Pollinations Model Routing (Final — 30 Mayıs 2026)

Tüm modeller benchmark + Türkçe test ile değerlendirildi. Detay: `references/pollinations-model-routing-final.md`

| Görev | Model | Input | Output | Neden |
|-------|-------|-------|--------|-------|
| 🔧 Kod | `minimax` | 0.30 | 1.20 | SWE-bench 80.2%, en hızlı kod |
| 🔬 Analiz | `glm` | 1.00 | 3.20 | MMLU #1, BFCL #1 |
| ✍️ Metin | `gpt-5.4-mini` | 0.75 | 4.50 | 🇹🇷 En iyi Türkçe |
| ⚡ Auxiliary | `nova-fast` | 0.035 | 0.14 | En hızlı + en ucuz |

⚠️ **Türkçe Pitfall:** Modeller İngilizce ve Türkçe'de ÇOK farklı. HER ZAMAN hedef dilde test et.
glm İngilizce Arena CW 1442 → Türkçe "Analyze the Request". gpt-5.4-mini benchmark orta → Türkçe #1.


## Çalışan Workaround: light_agent.py (Direkt API + ThreadPoolExecutor)

`delegate_task` per-task override gelene kadar çalışan tek yöntem. **hermes -z güvenilmez — kullanma.**

```bash
python3 ~/.hermes/scripts/light_agent.py yazar "İzmir'i anlat"
```

Paralel çalıştırma için `execute_code` içinde `ThreadPoolExecutor` kullan.
Direkt Pollinations proxy üzerinden API çağrısı yapar, proxy API key'i otomatik ekler.

### Ekip (Edel'in tercih ettiği isim)

| Ekip | Model | pollen/1K | Rol |
|------|-------|-----------|-----|
| 👨‍💻 kodcu | minimax | 0.30/1.20 | Kod yaz, debug, test |
| 🔬 analist | glm | 1.00/3.20 | Araştır, karşılaştır, kaynak göster |
| ✍️ yazar | gpt-5.4-mini | 0.75/4.50 | Akıcı Türkçe içerik |
| 📦 yardimci | gemma | 0.07/0.34 | Hafif işler, hesap, tarih |

Agent prompt'ları: `~/.hermes/agents/{kodcu,analist,yazar,yardimci}.md`
Tam sistem referansı: `references/ekip-multi-agent.md`

## hermes -z Pollinations Sessizliği (30 Mayıs 2026 — Debug Edildi, Kısmi Çözüm)

`hermes -z` Pollinations provider'ında **hiç çıktı vermiyor**, exit 0. DeepSeek ve Mistral custom provider ile çalışıyor.

**Kök neden zinciri:**
1. Hermes provider'ı tanımak için `/v1/props`, `/version`, `/api/tags`, `/v1/models/{model}` gibi endpoint'leri sorguluyor
2. Pollinations bu endpoint'leri desteklemiyor → 404
3. Hermes sessizce provider'ı geçersiz sayıyor
4. **KISMİ ÇÖZÜM:** Proxy'ye sahte endpoint yanıtları eklendi (`/v1/models`, `/api/tags`, `/version`, `/v1/props`, `/api/show`) → artık provider tanınıyor
5. **KALAN SORUN:** Chat completions isteği gidiyor, Pollinations cevap veriyor ama hermes stdout'a yazdırmıyor. Muhtemelen `content_filter_results` gibi ekstra alanlar parse edilemiyor.

**Workaround:** Tool gerektiren ajanlar için `hermes -z --provider deepseek`, toolsuz işler için `light_agent.py`.

## OpenCode + Pollinations (31 Mayıs 2026 — Yeni Keşif)

OpenCode CLI (`opencode run --model openai/gpt-5.4-mini`) Pollinations ile kısmen çalışıyor:

**Çalışan:** Provider tanıma, model listesi, auth ✅
**Sorun:** OpenCode `/v1/responses` endpoint'ini kullanıyor (OpenAI Responses API). Pollinations Chat Completions API'si.

**Proxy çözümleri:**
1. **Path dönüşümü:** `/v1/responses` → `/v1/chat/completions` ✅
2. **Body dönüşümü:** `input` → `messages`, `developer` → `system`, Responses API'ye özel alanları temizle ✅
3. **Kalan sorun:** OpenCode'un gönderdiği tool listesi çok büyük (68KB). Pollinations "JSON body validation failed" veriyor.

**Çalışan formül:**
```bash
export OPENAI_BASE_URL="http://127.0.0.1:19999/v1"
export OPENAI_API_KEY=*** opencode run "görev" --model openai/gpt-5.4-mini --pure --agent plan
```

**Wrapper script:** `~/.hermes/scripts/opencode_poll.sh` — .env'den API key okur, OpenCode'u Pollinations proxy ile başlatır.

**Edel bulgusu (Android Codespace):** OpenCode Pollinations ile düzgün çalışıyor (telefondan test edildi). Sunucuda tool listesi sorunu var.

## Proxy Güncel Özellikler (31 Mayıs 2026)

`pollinations-proxy.py` systemd servisi (`pollinations-proxy.service`):
- **UA spoofing:** Cloudflare 1010 bypass
- **Auto API key:** .env'den okur, Authorization header'ı yoksa ekler
- **Sahte endpoint'ler:** `/v1/models`, `/api/tags`, `/version`, `/v1/props`, `/api/show`, `/api/v1/models` → 200
- **Responses → Chat dönüşümü:** `/v1/responses` path + body transform
- **Debug log:** journalctl --user -u pollinations-proxy

## light_agent.py — Direkt Pollinations API Wrapper

**Dosya:** `~/.hermes/scripts/light_agent.py`
**Kullanım:** `python3 ~/.hermes/scripts/light_agent.py kodcu "görev"`
**Özellikler:** Direkt Pollinations proxy (127.0.0.1:19999) üzerinden API çağrısı. Toolsuz (web_search, terminal YOK). Paralel için `execute_code` + `ThreadPoolExecutor`.

## Hermes Konfigürasyon Pitfall'ları

- **config.yaml KESİNLİKLE paylaşılmaZ** — API key'ler, token'lar içerir. Telegram'da görünürse hemen sil. Güvenlik açığı.
- **config.yaml korumalı:** `patch` ve `write_file` çalışmaz. `hermes config set` kullan.
- **Delegation config değişiklikleri gateway restart gerektirir.** Runtime'da alınmaz.
- **Restart:** `systemctl --user restart hermes-gateway` ~30sn sürebilir.

## Edel Tercihleri

- Hermes'ten vazgeçilmez
- PAID model kullanılmaz
- Önce benchmark araştırması, sonra model seçimi

---

## Ekip Sistemi (30 Mayıs 2026)

Hermes'te per-task model override olmadığı için `terminal` + `hermes -z` veya `light_agent.py` ile çoklu agent sistemi kuruldu.

### Mimari
```
~/.hermes/
├── agents/
│   ├── kodcu.md      → minimax (yazılım)
│   ├── analist.md    → glm (araştırma)
│   ├── yazar.md      → gpt-5.4-mini (Türkçe içerik)
│   └── yardimci.md   → gemma (hafif işler)
└── scripts/
    ├── agent_runner.sh   → ./agent_runner.sh <agent> "görev" [--background]
    └── light_agent.py    → direkt Pollinations API wrapper (toolsuz)
```

### Agent Prompt'ları (Claude tarafından optimize edildi)
Her agent için İngilizce system prompt (modeller İngilizce talimatla daha iyi çalışır):
- **kodcu**: Senior software engineer. Code-first, minimal commentary.
- **analist**: Research analyst. Bullet points, 2+ sources, max 10 bullets.
- **yazar**: Turkish content writer. Warm, "sen" language, 2-3 sentence paragraphs.
- **yardimci**: Utility assistant. 1-3 sentences, formula + result.

### Kullanım
```bash
# Tek ajan
./agent_runner.sh kodcu "Python palindrome fonksiyonu yaz"

# Paralel (execute_code + ThreadPoolExecutor)
# 3 agent aynı anda çalışır: kodcu, analist, yazar
```

### Bilinen Limitasyon
- `light_agent.py` direkt API çağrısı yapar → TOOL'SUZ (web_search, terminal, file yok)
- `hermes -z` deepseek ile çalışır ama Pollinations ile çalışmaz → `references/hermes-z-pollinations-debug.md`
- Analist için web_search şart → deepseek üzerinden `hermes -z` kullanılır (hibrit)
