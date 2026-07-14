# Gmail → NotebookLM Pipeline

31 Mayıs 2026'da kuruldu. Gmail'deki önemli servis maillerini otomatik tarar ve ilgili NotebookLM notebook'una kaynak olarak ekler.

## Cron Job
- **ID:** `f4ea19bb906a`
- **Schedule:** `0 9,15,21 * * *` (günde 3 kez)
- **Model:** deepseek-v4-pro
- **Skills:** google-workspace

## Notebook Eşleştirmesi

| Kaynak | Filtre | Notebook ID | Notebook Adı |
|--------|--------|------------|--------------|
| APA | @apa.org, @info.apa.org | c44469fe-a69a-4a86-8dd8-756c2f365109 | APA Bilgi |
| Firecrawl | @firecrawl.dev | 9c5f7e8f-4c89-40b9-866d-ff9df8d9780b | 📧 Firecrawl Mailleri |
| Skool | @skool.com | 96556f1f-56d6-4532-aaf4-2c4662249a7d | 📧 Skool Mailleri |
| Cloudflare | @cloudflare.com | c48be9bd-cabc-403f-a9c5-f20ff54f27a7 | 📧 Cloudflare Mailleri |
| DeepSeek | @deepseek.com | 51456733-181c-4a43-a8ed-b6364ce2dd9c | 📧 DeepSeek Mailleri |

## Kritik Pitfall: ALL_PROXY=""

Google API çağrıları WARP SOCKS5 proxy üzerinden çalışmaz. Sunucuda `ALL_PROXY` env var'ı WARP'a yönlendirdiği için, Google API script'i çalıştırmadan önce mutlaka `ALL_PROXY=""` set edilmeli:

```bash
ALL_PROXY="" python3 ~/.hermes/skills/productivity/google-workspace/scripts/google_api.py gmail search "is:unread ..."
```

Python içinde:
```python
import os
env = os.environ.copy()
env["ALL_PROXY"] = ""
subprocess.run([...], env=env)
```

## Gmail Arama Sözdizimi

Tüm kaynakları tek sorguda taramak için:
```
is:unread (from:apa.org OR from:firecrawl.dev OR from:skool.com OR from:cloudflare.com OR from:deepseek.com)
```

## İş Akışı

1. `gmail search` ile yeni okunmamış mailleri bul
2. Her mail için `gmail get MESSAGE_ID` ile tam içeriği al
3. `from` alanına göre kaynağı belirle
4. İlgili notebook'a `source_add(source_type="text")` ile ekle
5. Edel'e özet geç: kaç yeni mail, hangi notebook'lara eklendi
