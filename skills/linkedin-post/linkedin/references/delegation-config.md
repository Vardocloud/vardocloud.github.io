# Delegation (Alt Ajan) Konfigürasyonu

## Bug Geçmişi

- **v0.14.0 ve öncesi**: `delegation.model` ve `delegation.provider` ayarları ignore ediliyordu — sub-agent her zaman parent model'i miras alıyordu
- **v0.15.1 (29 Mayıs 2026)**: Fix merge edildi! 3 commit: `fix(delegation): pass target_model`, `fix(delegate): clear acp_command`, `feat: configurable subagent provider:model`
- **#12440**: P1 bug, artık kapandı

## Konfigürasyon (v0.15.1+)

```yaml
delegation:
  provider: pollinations     # custom_providers'taki isimle eşleşmeli
  model: gemini-flash-lite-3.1  # hafif/ucuz model
  api_key: ''               # boş → custom_providers'tan alır
  base_url: ''              # boş → provider'ın base_url'ini kullanır
```

## Önemli Notlar

- **Gateway restart şart!** Config değişikliği sonrası `systemctl --user restart hermes-gateway`
- Model değişikliği session sırasında etki etmez — restart gerek
- Provider ismi CASE-SENSITIVE: custom_providers'ta `name: Pollinations` ise `delegation.provider: Pollinations`
- Sub-agent'lar tools kullanamaz (clarify, memory, send_message, execute_code YOK)

## Model Seçimi

Alt ajanlar için hafif/ucuz modeller:

| Model | Provider | $/1M token (giriş/çıkış) | Not |
|-------|----------|--------------------------|-----|
| gemini-flash-lite-3.1 | pollinations | ~$1-3 (pollen opak) | ✅ Kurulu |
| gemini-2.5-flash-lite | google direkt | $0.10/$0.40 | En ucuz |
| mistral-small | mistral | $0.20/$0.60 | ✅ Kurulu |

Pollinations pahalı (~10x Google direkt). Google API key alınırsa en ekonomik seçenek.
