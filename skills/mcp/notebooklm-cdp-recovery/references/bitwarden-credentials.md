# Bitwarden Credential Mapping for NotebookLM

Two Google accounts used for NotebookLM:

| Profile | Bitwarden Item ID | Email | TOTP | Purpose |
|---------|------------------|-------|------|---------|
| pro | `google-pro` | kenshin4155@gmail.com | ✅ Var | MCP ana hesabı |
| legacy | `google-isimgorulsunn` | isimgorulsunn@gmail.com | ❌ Yok | Notebook sahibi |

## Credential Retrieval

```python
import json, urllib.request

BW_SERVE = "http://127.0.0.1:8087"
items_req = urllib.request.Request(f"{BW_SERVE}/list/object/items")
with urllib.request.urlopen(items_req, timeout=10) as r:
    items = json.loads(r.read())

for item in items.get("data",{}).get("data",[]):
    name = item.get("name","")
    if name in ["google-pro", "google-isimgorulsunn"]:
        data = json.loads(urllib.request.urlopen(
            urllib.request.Request(f"{BW_SERVE}/object/item/{item['id']}"), timeout=10).read())
        login = data["data"]["login"]
        username = login["username"]
        password = login["password"]
        totp = login.get("totp")  # None for legacy
```

## BWS Secret Names (env-var format)

BWS'de `google-pro` item'i TOTP secret içerir, `google-isimgorulsunn` içermez.
Legacy hesap phone verification veya Google Prompt gerektirebilir.

## NOT: Case Sensitivity

Bitwarden'da item isimleri:
- ✅ `google-pro` (küçük g)
- ✅ `Google-isimgorulsunn` (BÜYÜK G)

Python'da karşılaştırma yaparken `name.lower()` kullan. Yoksa `Google-isimgorulsunn`'u
`"google"` ile karşılaştırınca eşleşmez!
