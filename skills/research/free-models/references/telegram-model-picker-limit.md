# Telegram Model Picker — 100 Button Limit Pitfall

**Keşif tarihi:** 16 Tem 2026
**Dosya:** `hermes_cli/model_switch.py` → Telegram inline keyboard rendering

## Sorun

Telegram `/model` komutu, provider bazında modelleri **inline keyboard** olarak listeler.
Telegram inline keyboard'ların **~100 buton limiti** vardır (kesin sayı: callback_data boyutuna bağlı, pratikte 95-105 arası).

Provider'da 100'den fazla model varsa:
- NVIDIA `discover_models: true` → **118 model** (16 Tem 2026 itibarıyla)
- Modeller **alfabetik sıralanır**
- Listenin **sonundaki modeller Telegram tarafından gösterilmez** (limit aşımı)

Bu yüzden `z-ai/glm-5.2` gibi `z` ile başlayan modeller görünmez olur.

## Tanı (Diagnostic)

```bash
# 1. Provider'da kaç model var?
curl -s https://integrate.api.nvidia.com/v1/models \
  -H "Authorization: Bearer $NVIDIA_API_KEY" \
  | python3 -c "import json,sys; data=json.load(sys.stdin); print(f'Total: {len(data[\"data\"])} models')"

# 2. Hedef model listede nerede (alfabetik sırası)?
curl -s https://integrate.api.nvidia.com/v1/models \
  -H "Authorization: Bearer $NVIDIA_API_KEY" \
  | python3 -c "
import json,sys
models = json.load(sys.stdin)['data']
targets = [m for m in models if 'glm' in m['id'].lower()]
for t in targets:
    idx = next(i for i,m in enumerate(models) if m['id']==t['id'])
    print(f'  #{idx+1}/{len(models)} {t[\"id\"]}')
"
```

**Yorum:** Eğer `#100+` görüyorsan → Telegram limiti dışında → görünmez.

## Çözüm

### Seçenek A: `discover_models: false` + kısa alias (ÖNERİLEN)

```yaml
# config.yaml → custom_providers → NVIDIA
discover_models: false  # API'den çekme, explicit listeyi kullan
models:
  glm-5.2: z-ai/glm-5.2  # KISA isim, 'g' ile başlar → listede önde
  # ... diğer modeller
```

- `discover_models: false` → API'den 118 model çekilmez, sadece config'deki explicit liste
- Kısa alias `glm-5.2` (`g` ile başlar) → listede `google/*` modellerinden sonra, görünür konumda
- Telegram limitini aşmamak için explicit listeyi 80-90 modelle sınırlı tut

### Seçenek B: Model sıralamasını değiştir (Hermes patch gerekir)

Hermes'in model listesini alfabetik yerine config'deki sıraya göre göstermesi — ama bu Hermes core değişikliği gerektirir, pratik değil.

### Seçenek C: Sayfalama (Hermes feature request)

Telegram inline keyboard'da "Sonraki sayfa →" butonu — şu an Hermes'te implemente değil.

## İlgili Skill'ler

- `hermes-config-resilience` → `references/nvidia-free-tier-notes.md` — `discover_models` flag davranışı
- `free-models` → skill'in kendisi — NVIDIA model listesi ve test sonuçları

## Geçmiş Vakalar

| Tarih | Model | Provider | Modeller | Sıra | Görünür? |
|-------|-------|----------|----------|------|----------|
| 16 Tem 2026 | `z-ai/glm-5.2` | NVIDIA | 118 | #117/118 | ❌ |
| 16 Tem 2026 | `glm-5.2` (alias) | NVIDIA | ~85 explicit | #30 civarı | ✅ (fix sonrası) |
