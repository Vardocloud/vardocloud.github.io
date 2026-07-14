# Hermes -z + Pollinations Custom Provider Sorunu

## Belirti
`hermes -z "prompt" -m MODEL --provider custom:Pollinations --yolo` → sessiz, exit 0, stdout/stderr boş.
Ama `hermes chat` çalışıyor, `custom:mistral` çalışıyor, direkt API çağrıları çalışıyor.

## Kök Neden
Hermes -z modu, custom provider'ı doğrulamak için şu endpoint'leri sorguluyor:
- `/api/tags` (Ollama formatı)
- `/v1/models`, `/v1/models/MODEL` (OpenAI formatı)
- `/api/v1/models`
- `/v1/props`, `/props`, `/version`
- `/api/show?name=MODEL`

Pollinations bu endpoint'lerin çoğunu desteklemiyor → 404 → hermes provider'ı geçersiz sayıyor.
Ayrıca Pollinations response'undaki `content_filter_results` ek alanı hermes -z çıktı yolunda sorun çıkarıyor.

## Kısmi Çözüm: Proxy Fake Endpoint'leri
`~/hermes/scripts/pollinations-proxy.py` içinde `do_GET()` metodu, bilinen sorgu endpoint'lerine sahte 200 yanıtları döndürür:

```python
fake_responses = {
    '/api/tags': {'models': [{'name': 'openai'}, {'name': 'gemma'}, {'name': 'minimax'}, {'name': 'glm'}, {'name': 'gpt-5.4-mini'}]},
    '/v1/models': {'object': 'list', 'data': [{'id': 'openai'}, {'id': 'gemma'}, {'id': 'minimax'}, {'id': 'glm'}, {'id': 'gpt-5.4-mini'}]},
    '/api/v1/models': {'object': 'list', 'data': [{'id': 'openai'}]},
    '/v1/props': {'pollinations': True, 'supports_tools': True},
    '/props': {'pollinations': True},
    '/version': {'version': '1.0.0'},
}
# /api/show?name=X formatı da yakalanır
```

Bu, hermes'in "API çalışmıyor" deyip vazgeçmesini engeller. Ancak response parsing sorunu devam eder — hermes -z hala çıktı vermez.

## Eklenenler
- `api_mode: chat_completions` config'e eklendi (işe yaramadı)
- `--ignore-user-config --ignore-rules` (işe yaramadı)
- `OPENAI_BASE_URL` + `OPENAI_API_KEY` env (işe yaramadı)

## Sonuç
Hermes -z Pollinations ile ÇALIŞMIYOR. Workaround: `light_agent.py` (direkt API, toolsuz) veya `hermes -z --provider deepseek` (tool'lu).
