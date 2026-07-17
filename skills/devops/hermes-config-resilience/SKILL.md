---
name: hermes-config-resilience
title: Hermes Config Resilience
description: Preserve Hermes Agent config across updates using golden_config.yaml and restore_config.py
trigger: User mentions golden_config, config reset after update, or post-update hook issues
---

# Hermes Config Resilience

Preserve Hermes config across updates. Uses `golden_config.yaml` as single source of truth and `restore_config.py` with `--post-update` mode.

## Architecture

`hermes update` → `post-update.sh` hook → `restore_config.py --post-update`

Pipeline: snapshot → sync golden from config → check drift → restore golden values → restart gateway → verify

## Commands

| Command | Action |
|---------|--------|
| `--check` | Dry-run diff, exit 0=aligned 1=drift |
| `--sync` | Add new config entries to golden |
| `--restore` | Sync + apply golden to config preserves version metadata |
| `--post-update` | Full pipeline + gateway restart + verify |

## Critical Rules

1. `_config_version` never overwritten
2. API keys empty in golden (from .env or Bitwarden)
3. **Bitwarden enabled MUST be true in golden** — after setting up Bitwarden SM, golden_config.yaml has `secrets.bitwarden.enabled: false` by default. MUST manually set to `true` in golden, then `--restore` to apply. If golden says `false`, every `--restore` will DISABLE Bitwarden.
4. SOUL/AGENTS section-merged (user additions preserved)
5. `hooks_auto_accept: true` required

## Provider Degisikligi Sonrasi Auxiliary Bosluk Doldurma

Bir custom provider kaldirildiginda (Pollinations gibi), auxiliary altindaki model/provider alanlari bos/bosta kalir. Doldurma sirasi:

1. **Provider API'sini test et:** Model listesini ve bir chat completion'ini dene. Yavas/timeout veren modelleri kritik yollara koyma.
2. **`hermes config set` ile doldur:** Ornegin `hermes config set auxiliary.compression.provider "custom:NVIDIA"`
3. **Fallback guncelle:** `hermes config set fallback_providers '[...]'` ile eski provider referansini kaldir, yenisini ekle
4. **Golden config sync:** `restore_config.py --sync && restore_config.py --check`
5. **Free tier rate limitlerine dikkat et:** NVIDIA free tier'da model worker limitleri var (48/48 ResourceExhausted). Bu kalici bir limit degil, gecici worker yuklenmesi — retry edilebilir. Ama DeepSeek V4 Flash free tier surekli overload. Oneri: opencode-go lokal proxy kullan (kota yok, hizli). GLM 5.2 NVIDIA'da en stabil free model.

Bilinen bos alanlar (model: '' / provider: auto): compression, kanban_decomposer, tts_audio_tags. TTS genelde LLM gerektirmez, auto kalabilir.

**Dil kalitesi kriterdir — model secerken Turkce performansina dikkat et.**
- `nvidia/llama-3.1-nemotron-70b-instruct` Turkcede zayif — compression gibi Turkce input isleyen gorevler icin uygun DEGIL
- `deepseek-v4-flash` (opencode-zen) Turkcede cok iyi — compression gibi metin isleme gorevleri icin dogru secim
- `meta/llama-3.3-70b-instruct` Turkcede orta — decomposer gibi Ingilizce prompt agirlikli gorevlerde kullanilabilir
- Test etmeden modeli kritik yola koyma: once bir chat completion ile dil kalitesini dogrula, timeout/error veren modelleri ele

**Env var override uyarisi:** Auxiliary tool'lar config'deki model yerine `AUXILIARY_*_MODEL` env var'ini kullanabilir. Debug'da once env var kontrol et. Config dogru olsa bile env override ederse tool calismaz.

**Free tier limit testi ONCE yapilmali — modeli kritik yola koymadan once sinirlarini bil.**
14 Tem 2026'daki hata: DeepSeek V4 Flash NVIDIA free tier'da worker limiti dolu (48/48) cikti. Oysa once burst testi yapilsaydi bu gorulurdu. Kural: yeni bir provider/modeli herhangi bir auxiliary role atamadan ONCE:
1. Model listesini cek (`GET /v1/models`)
2. Basit bir chat completion dene (200 donuyor mu?)
3. Burst test: 10-20 ardışık request at, worker limiti / rate limit / 500 error var mi?
4. Dil kalitesini dogrula (Turkce input ver, cikti mantikli mi?)
5. Tum bunlar gectikten SONRA config'e ekle

## CLI Config Edit Riskleri

`hermes config set` komutu YAML parse edemezse config dosyasini truncate edebilir. Hermes truncation'dan once `.config.yaml.corrupt.*.bak` ile yedek alir. Kurtarma icin en son corrupt yedegi geri kopyala ve YAML sentaksini dogrula.

**Kural:** `sed -i` gibi global pattern araclariyla YAML duzenleme — tum nested bloklarda eslesme yapip yapiyi bozar. Hermes config'ini sadece `hermes config set`, `restore_config.py` veya Python YAML API'si ile degistir.

## Pitfalls

- **`discover_models` flag (critical):** When adding a custom_provider with an explicit `models:` list, you MUST set `discover_models: false`. Hermes defaults this to `true`, which causes it to call the provider's `/v1/models` API and **overwrite your curated model list** with the live catalog. This is especially bad for aggregator gateways like NVIDIA's free tier where the API returns 121 models (including embedding/safety/vision) instead of your curated 84. The `/model` picker will show every model from the endpoint, unordered, instead of your tier-sorted curation. **Additionally**, Telegram inline keyboards have a ~100 button limit — models alphabetically at the end (like `z-ai/glm-5.2` at position #117/118) are silently invisible. See `free-models` skill → `references/telegram-model-picker-limit.md` for diagnosis and fix. See `references/nvidia-free-tier-notes.md` for the code path in `hermes_cli/model_switch.py`.
- **Provider name collision:** Don't define the same provider under both `providers:` and `custom_providers:`. The basic `providers:` entry takes precedence and shadows the custom_providers models. Put rich model lists in `custom_providers` only.
- **NVIDIA model name mapping NOT applied by gateway (17 Jul 2026):** Even when `models:` is correctly configured in the NVIDIA custom_provider (e.g. `glm-5.2: z-ai/glm-5.2`), the gateway sends the raw name `glm-5.2` to the API, which returns HTTP 404. The mapping IS applied in the custom_providers YAML but the gateway's NVIDIA provider handler doesn't respect the `models:` section for name resolution. **Workaround:** Use a different provider (opencode-go, opencode-zen) or configure model_aliases directly. Test: `curl -X POST ... -d '{"model":"glm-5.2"}'` → 404 vs `'{"model":"z-ai/glm-5.2"}'` → 401 (model exists, needs auth).
- **Bitwarden + Golden cycle:** Setup Bitwarden → `--sync` → edit golden to set `secrets.bitwarden.enabled: true` → `--restore`. Don't skip the golden edit step.
- **`--restore` after update:** If the update added new config keys, `--sync` first, then `--restore`. Never `--restore` without `--sync` — you'd lose the new keys.
- **`--check` exit code:** Exit 0 = aligned, exit 1 = drift. Use this in automation.
- **`_config_version` increase:** If Hermes update bumps `_config_version` and golden blocks it during restore, check if a migration is expected. `_config_version` 23 at time of writing.
- **Run `--check` BEFORE `--restore`** — always see the diff first. This session found 32 diffs after Bitwarden setup; most were harmless ordering diffs, but `secrets.bitwarden.enabled: false` in golden was critical. If `--restore` had run without first fixing golden to `true`, Bitwarden would have been disabled.
- **After new provider/model alias:** `--sync` then `--check`. New custom providers or model_aliases won't be in golden until synced.
- **Adding custom providers (Hermes config):** When `hermes config` CLI doesn't support the operation, use `python3` with `yaml` to edit `custom_providers` and `model_aliases` programmatically. Then run `restore_config.py --sync` to update golden. Always `systemctl --user restart hermes-gateway` after provider changes. The `api_key_env` references a Bitwarden secret name. See voice-agent reference for Groq integration example.
- **`hermes config set` deletes YAML comments:** The `hermes config` CLI serializes YAML without preserving comments. If your config has documentation comments (like tier headers in model lists), use Python string replacement instead of `hermes config set` when editing blocks that contain comments.

## Env Var Override Pitfall: AUXILIARY_VISION_MODEL (11 Tem 2026)

**Sorun:** `browser_vision` ve `vision_analyze` tool'ları model adını config'deki `auxiliary.vision.model` alanından DEĞİL, `AUXILIARY_VISION_MODEL` ortam değişkeninden okur. Bu env var ayarlanmışsa, config'de ne yazarsan yaz O değer KULLANILIR.

**11 Tem 2026 vakası:**
- Config'de `auxiliary_models.vision.model: qwen/qwen3.7-plus` ayarlanmıştı
- `.env`'de `AUXILIARY_VISION_MODEL=qwen-vision` (eski değer) duruyordu
- `browser_vision` 404 "invalid_model" hatası veriyordu — çünkü `qwen-vision` diye bir model Zenmux'ta yok
- Çözüm: env var'ını config'le aynı değere (`qwen/qwen3.7-plus`) güncelle

**Kural:**
1. Hermes'te auxiliary tool'lar (vision, compression, etc.) config'de tanımlanmış modeli kullanır — ANCAK ilgili `AUXILIARY_*_MODEL` env var'ı mevcutsa, env var KAZANIR.
2. Herhangi bir vision/auxiliary model hatasında:
   - ÖNCE `echo $AUXILIARY_VISION_MODEL` (veya ilgili env) ile override var mı kontrol et
   - Config'i değil env var'ını düzelt (config zaten doğru olsa bile env override eder)
3. Hangi env var'larının hangi tool'ları etkilediğinin tam listesi için Hermes dokümantasyonuna bak. Bilinenler:
   - `AUXILIARY_VISION_MODEL` → `browser_vision`, `vision_analyze`
   - `AUXILIARY_WEB_EXTRACT_MODEL` → `web_extract`
   - `HERMES_AUXILIARY_MODEL` → genel auxiliary fallback
4. Env var ve config arasında tutarsızlık varsa, hata ayıklarken ÖNCE env var'ını kontrol et.

**Test:** Vision/browser/extract tool'larından 404/400 hatası alıyorsan → DUR. `echo $AUXILIARY_VISION_MODEL` çıktısı config'deki model adıyla eşleşiyor mu? Eşleşmiyorsa env var'ını düzelt, restart at.

## Setup

1. Make post-update hook executable
2. Enable `hooks_auto_accept` in config
3. `python3 scripts/restore_config.py --sync`
4. `python3 scripts/restore_config.py --check`
5. `python3 scripts/restore_config.py --restore`

## Maintenance

- After new provider: `--sync` then `--check`
- After broken update: `--check` then `--restore`
- Golden can be manually edited
- Always `--check` after any update
