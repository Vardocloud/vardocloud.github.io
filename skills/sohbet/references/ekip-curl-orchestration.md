# EKİP Curl Orkestrasyonu (31 Mayıs 2026)

4 ajanı curl ile paralel veya sıralı çalıştırma pattern'leri.

## Proxy'ler
- Pollinations: `http://127.0.0.1:19999/v1`
- OpenCode Go: `http://127.0.0.1:19998/v1`

## Ajanlar ve Token Limitleri

| Ajan | Model | Port | max_tokens |
|------|-------|------|------------|
| Analist | glm-5.1 | 19998 | 1500-2000 |
| Yazar | gpt-5.4-mini | 19999 | 500-1000 |
| Yardımcı | gemma | 19999 | 50-200 |
| Kodcu | minimax-m2.7 | 19998 | 500-1500 |

## Pattern 1: Sıralı (Araştır → Yaz → Kontrol)

```bash
# 1. Analist araştırır
ARASTIRMA=$(curl -s --max-time 45 http://127.0.0.1:19998/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"glm-5.1","messages":[...],"max_tokens":2000}')

# 2. Yazar yazar  
curl -s --max-time 30 http://127.0.0.1:19999/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"gpt-5.4-mini\",\"messages\":[{\"role\":\"user\",\"content\":\"Şunu yaz: $ARASTIRMA\"}],\"max_tokens\":1000}"
```

## Dil Kuralı (2 Haz 2026)

Türkçe karakterler (ğ, ü, ş, ı, ö, ç) GLM-5.1'de boş dönmeye sebep olabilir.
**Kural:** EKİP prompt'larını İngilizce yaz, sonuna `Respond in Turkish.` ekle.
Bu hem confusable Unicode sorununu hem GLM-5.1 seçici boş dönmesini azaltır.
```python
from concurrent.futures import ThreadPoolExecutor
agents = {
    "Analist": {"url": "...19998", "model": "glm-5.1", ...},
    "Yazar": {"url": "...19999", "model": "gpt-5.4-mini", ...},
    ...
}
with ThreadPoolExecutor(max_workers=4) as ex:
    futures = {ex.submit(call, n, c): n for n, c in agents.items()}
```

## Pattern 3: Cron Job İçi (Adım adım terminal)

Cron prompt'unda her adım için ayrı curl:
```
## ADIM 1 — Analist
curl -s --max-time 45 http://127.0.0.1:19998/v1/chat/completions ...

## ADIM 2 — Yazar  
curl -s --max-time 30 http://127.0.0.1:19999/v1/chat/completions ...
```

## Kritik Notlar
- OpenCode Go modelleri REASONING yapar → max_tokens 500 altı kesilir
- Pollinations modelleri direkt yanıt verir → 100 token yeterli olabilir
- API key redaction: anahtar dosyadan okunur, tool parametresinde geçilmez
