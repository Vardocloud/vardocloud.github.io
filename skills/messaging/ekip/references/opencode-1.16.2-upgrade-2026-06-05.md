# OpenCode 1.16.2 Güncelleme Notları (5 Haz 2026)

## Güncelleme
- 1.15.12 → 1.16.2 (`opencode upgrade` ile npm üzerinden)
- `opencode upgrade` komutu, `update` değil

## Yeni Modeller
OpenCode Go'ya eklenen modeller:
- **minimax-m3** — Kodcu birincil oldu (M2.7'nin yerine)
- **mimo-v2.5** — Analist birincil oldu (Zen'den taşındı)
- **mimo-v2.5-pro** — Analist yedek
- **qwen3.6-plus**
- **qwen3.7-plus**

## Model Davranış Değişiklikleri (KRİTİK)

### minimax-m2.7 Bozulması
2 Haziran'da 0 reasoning iken 5 Haziran'da tamamen reasoning dökmeye başladı:
- max_tokens=100: "The user says... The user wants..." → `finish_reason: length`
- Asıl cevaba ulaşamadı
- **Teşhis:** Düşük token testi (max_tokens=20, "Reply with only: OK")

### minimax-m3
- 0 reasoning ✅
- `<think>...</think>` tag'lerini content'e döküyor (M2.7'den farklı, daha kısa)
- Kod çıktısı doğru — `<think>` tag'leri filtrelenebilir
- max_tokens 2000 önerilir (tag'ler token tüketiyor)

### mimo-v2.5 (OpenCode Go)
- ~100 reasoning token + temiz içerik
- "Merhaba! 👋" — doğal Türkçe
- `finish_reason: stop`
- WARP gerekmiyor (Zen'deki free sürümün aksine)

### Zen free modeller (güncel liste)
`GET opencode.ai/zen/v1/models` → 46 model, 7'si `-free`:
mimo-v2.5-free, nemotron-3-super-free, nemotron-3-ultra-free, minimax-m3-free, big-pickle, deepseek-v4-flash-free, qwen3.6-plus-free

⚠️ Zen artık YEDEK. Oracle Cloud IP'si block'lu → WARP şart.

## EKİP Güncel Atama

| Ajan | Model | Provider | max_tokens |
|------|-------|----------|-----------|
| Kodcu | minimax-m3 | OpenCode Go :19998 | 2000 |
| Analist | mimo-v2.5 | OpenCode Go :19998 | 2000 |
| Yazar | gpt-5.4-mini | Pollinations :19999 | 1000 |
| Yardımcı | gemma-4-26b | Pollinations :19999 | 200 |

## opencode.json Güncelleme
Yeni modeller `~/.config/opencode/opencode.json` → `provider.opencode-go.models` altına eklendi.
Varsayılan model `deepseek-v4-flash` → `deepseek-v4-pro` değiştirildi (Edel talimatı).
