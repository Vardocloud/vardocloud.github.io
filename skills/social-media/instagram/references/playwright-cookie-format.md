# Instagram Cookie Format

## Netscape Cookie Jar

```
domain  TRUE/FALSE  path  SECURE  expiry  name  value
```

Her satır TAB ile ayrılmış.

## Örnek

```
.instagram.com	TRUE	/	TRUE	1795766685	csrftoken	9D3KRgTT...
.instagram.com	TRUE	/	FALSE	1785690678	ds_user_id	78089668165
.instagram.com	TRUE	/	FALSE	1785690261	mid	aYEtdQALAAHb...
.instagram.com	TRUE	/	TRUE	0	rur	CLN,78089668165,...
.instagram.com	TRUE	/	TRUE	1795765260	sessionid	78089668165%3A...
```

## Parse (Python → Playwright)

```python
def parse_netscape_cookies(path):
    cookies = []
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 7:
                cookies.append({
                    "name": parts[5],
                    "value": parts[6],
                    "domain": parts[0],
                    "path": parts[2],
                    "secure": parts[3] == "TRUE",
                    "httpOnly": False,
                })
    return cookies
```

## Kritik Çerezler

| Çerez | Amaç | Süre |
|-------|------|------|
| `sessionid` | Oturum anahtarı | ~6 ay |
| `csrftoken` | CSRF koruması | ~6 ay |
| `ds_user_id` | Kullanıcı ID | ~3 ay |
| `rur` | Rate limiting token | Session |
| `mid` | Machine ID | ~3 ay |
