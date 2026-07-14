# n8n Workflow Credential Extraction

## Context

n8n workflow JSON exports contain API keys, tokens, and credentials in node parameters. When migrating from n8n to Hermes, extract these securely.

## Extraction Targets

| Node Type | Sensitive Field | Pattern |
|-----------|----------------|---------|
| `httpRequest` headers | Authorization header | `Bearer sk_...` or raw API key |
| `httpRequest` query params | access_token | `EAAP9...` (FB tokens) |
| `httpRequest` body params | upload_preset, api keys | `n8n_instagram`, etc. |
| `facebookGraphApi` | credentials.id | References n8n credential store |
| `googleSheets` | documentId, sheetName | Not secret but useful to capture |
| `telegram` | chatId | `-100...` |
| `cloudinary` URL | cloud_name | Extracted from endpoint URL |

## Python Extraction Script

```python
import json, re, os

def extract_secrets(workflow_path, output_env_path):
    with open(workflow_path) as f:
        data = json.load(f)

    secrets = {}

    for node in data.get("nodes", []):
        params = node.get("parameters", {})
        params_str = json.dumps(params)

        # Pollinations API keys (sk_ prefix)
        for m in re.finditer(r'sk_[a-zA-Z0-9]{20,60}', params_str):
            secrets.setdefault("POLLINATIONS_API_KEY", m.group())

        # Facebook access tokens
        for qp in params.get("queryParameters", {}).get("parameters", []):
            if qp.get("name") == "access_token" and qp.get("value", "").startswith("EAA"):
                secrets["FB_ACCESS_TOKEN"] = qp["value"]

        # Header-based keys
        for hp in params.get("headerParameters", {}).get("parameters", []):
            val = hp.get("value", "")
            name = hp.get("name", "")
            if "Authorization" in name:
                if val.startswith("Bearer "):
                    key = val[7:]
                    if key.startswith("sk_"):
                        secrets.setdefault("POLLINATIONS_API_KEY", key)
                    elif len(key) > 40:
                        secrets.setdefault("OTHER_API_KEY", key)

        # Instagram Business Account ID
        url = params.get("url", "")
        m = re.search(r'(\d{15,20})', url)
        if m and "graph.facebook.com" in url:
            secrets["INSTAGRAM_BUSINESS_ID"] = m.group(1)

    # Cloudinary from URL patterns
    m = re.search(r'cloudinary\.com/v\d+/([^/]+)/', params_str)
    if m:
        secrets["CLOUDINARY_CLOUD"] = m.group(1)

    # Write secure file
    with open(output_env_path, "w") as f:
        f.write("# Extracted from n8n workflow\n")
        for k, v in sorted(secrets.items()):
            f.write(f'{k}="{v}"\n')

    os.chmod(output_env_path, 0o600)
    return secrets

if __name__ == "__main__":
    import sys
    secrets = extract_secrets(sys.argv[1], sys.argv[2])
    for k in sorted(secrets):
        masked = secrets[k][:8] + "..." + secrets[k][-4:]
        print(f"  {k}: {masked}")
    print(f"\n{len(secrets)} secrets → {sys.argv[2]}")
```

## Secure Deletion

```bash
shred -u workflow.json   # Linux: overwrite + delete
# or
rm -P workflow.json       # macOS: overwrite + delete
```

## Why Not n8n Credential Store?

n8n credentials are encrypted in its internal DB. The JSON export only contains credential *references* (IDs), not the actual values. Values only appear in nodes that use raw HTTP requests with inline API keys. Extract from those HTTP nodes directly.

## Token Verification (ZORUNLU)

Çıkan token'ları hemen test et — n8n'deki token'lar sık sık expire olur:

- **FB Graph API token:** curl ile `/ME` endpoint'ine test isteği yap. `"error"` içeren yanıt (code 190) = expired. Kullanıcıdan Facebook Developer → Graph API Explorer'dan yeni token almasını iste.
- **Pollinations key:** curl ile text endpoint'ine Authorization header'ı ile test et. 401/403 = geçersiz key.
- **Diğer token'lar:** İlgili API'nın test endpoint'ine istek at.

Token expired ise kullanıcıdan yeni token iste veya alternatif auth yöntemine geç (cookie tabanlı Instagram API).
