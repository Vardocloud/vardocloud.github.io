# Gmail Body Extraction — Deep Multipart Workaround

## Problem

`google_api.py`'nin `gmail get` komutu bazı e-postalarda **boş body** döndürür. `_extract_message_body()` fonksiyonu sadece 1 seviye derinlik kontrol eder, iç içe multipart yapıları parse edemez.

## Belirti

```json
{"id": "...", "from": "...", "subject": "...", "body": ""}
```
Snippet dolu, body boş.

## Çözüm — Recursive Extractor (elle Python ile)

```python
import sys, json, base64
sys.path.insert(0, '/home/ubuntu/.hermes/skills/productivity/google-workspace/scripts')
from google_api import build_service

service = build_service('gmail', 'v1')
msg = service.users().messages().get(userId='me', id='MESSAGE_ID', format='full').execute()

def extract_text(payload):
    texts = []
    data = payload.get('body', {}).get('data', '')
    if data:
        texts.append((payload.get('mimeType',''), base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')))
    for part in payload.get('parts', []):
        texts.extend(extract_text(part))
    return texts

texts = extract_text(msg['payload'])
for mime, text in texts:
    if 'text/plain' in mime:
        print(text)
```

## Ne Zaman

- Kurumsal/postacı e-postaları (NEU, okul, banka)
- Alıntı/forward içeren mailler
- Snippet var ama body boşsa
