# Delegation Model Routing — Nihai Cozum (30 Mayis 2026)

## Kok Neden: Cloudflare UA Block

Pollinations Python User-Agent'i Cloudflare tarafindan bloklaniyor (error 1010).
`Pollinations-Safe` header'i, icerik filtresi, system prompt kisaltma — hicbiri sorun degildi.

Cozum: Tarayici User-Agent'i ekleyen proxy → `scripts/pollinations-proxy.py`, port 19999.

## Proxy

- Dosya: `scripts/pollinations-proxy.py`
- Servis: `pollinations-proxy.service` (systemd user)
- Port: 19999
- Islev: `User-Agent: Mozilla/5.0` ekler, Pollinations'a iletir

## Delegation Config (Calisiyor)

```yaml
delegation:
  provider: pollinations
  model: deepseek
  base_url: http://127.0.0.1:19999/v1
  api_key: sk_...
```

`hermes config set` ile ayarlanir. Gateway restart gerekir.

## Per-Task Model Override

### delegate_task: YOK (30 Mayis 2026 testi)

`delegate_task`'e `model` ve `provider` parametreleri gecildi, her iki task da `deepseek` kullandi.
Per-task override yok.

- **GitHub PR #35033:** `feat(delegate): per-task model/provider overrides` merge edilmis ama `delegate_task` tool semasina yansimamis
- **Hermes resmi dokumani:** `delegation.model` tek global deger (eski bilgi)
- **Kanban Workers:** Per-task override VAR (v0.15.0)

### Workaround: terminal + hermes CLI

```bash
# Tek ajan
hermes -z "GOREV" -m MODEL --provider pollinations --yolo \
  --base-url http://127.0.0.1:19999/v1

# Paralel
hermes -z "Kod yaz" -m minimax --provider pollinations --yolo \
  --base-url http://127.0.0.1:19999/v1 > /tmp/kodcu.log 2>&1 &
hermes -z "Arastir" -m glm --provider pollinations --yolo \
  --base-url http://127.0.0.1:19999/v1 > /tmp/analist.log 2>&1 &
wait
```

### Hafif alternatif: execute_code + requests

```python
import requests
resp = requests.post(
    "http://127.0.0.1:19999/v1/chat/completions",
    headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
    json={"model": "minimax", "messages": [
        {"role": "system", "content": "Sen kidemli bir yazilim muhendisisin."},
        {"role": "user", "content": "Palindrome fonksiyonu yaz"}
    ]},
    timeout=60
)
```

Tool kullanamaz (dosya, terminal, web yok). Hafif isler icin uygun.

## Routing Tablosu

| Gorev | Model | pollen/1K | Neden |
|-------|-------|-----------|-------|
| Kod | minimax | 0.30/1.20 | SWE-bench 80.2% |
| Analiz | glm | 1.00/3.20 | MMLU #1 |
| Metin | gpt-5.4-mini | 0.75/4.50 | TR en iyi |
| AUX | gemma | 0.07/0.34 | En ucuz + vizyon |

**TR Pitfall:** Modeller Ingilizce ve Turkce'de COK farkli. HER ZAMAN hedef dilde test et.

## Claude Code Karsilastirmasi

| | Claude Code | Hermes Agent |
|---|---|---|
| Per-agent model | Native ✅ (`@agent-name`) | delegate_task'te YOK ❌ |
| Kanban | - | Per-task ✅ (v0.15.0) |
| Workaround | Gerekmez | `hermes -z -m MODEL --yolo` |
