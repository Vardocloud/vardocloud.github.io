# NotebookLM CDP Login — Full Automation Reference

Google login via CDP with 2FA/TOTP support. Used when cookie extraction and autologin both fail.

## Flow

```
1. Navigate to clean sign-in (accounts.google.com/signin/v2/identifier)
2. Fill email → document.querySelector('#identifierId') → Input.insertText
3. Click Next → document.querySelector('#identifierNext')?.click()
4. Wait for password input → document.querySelector('input[type=password]')
5. Fill password → Input.insertText or JS value= set
6. Click Next → document.querySelector('#passwordNext')?.click()
7. Wait for 2FA challenge page → /challenge/selection
8. Click "Google Authenticator" → div[role=link] text include 'Authenticator'
9. Wait for TOTP input → document.getElementById('totpPin')
10. Set TOTP code via JS (NOT Input.insertText — it appends!)
    → el.value = code; dispatchEvent(new Event('input', {bubbles:true}))
11. Click "Next" button → Array.from(buttons).find(b => b.innerText === 'Next')
```

## Key Differences from nlm CLI Autologin

| Aspect | nb_autologin.py (existing) | CDP Manual (this flow) |
|--------|---------------------------|----------------------|
| Port | 18800 (keepalive) | MCP's Chrome (varies) |
| Browser profile | keepalive Chrome | MCP Chrome (headless) |
| After login | N/A | Extract cookies + save to profile |
| TOTP handling | Uses `Input.insertText` (broken) | JS value= set (works) |
| "Try another way" loop | Gets stuck | Explicitly click "Google Authenticator" option |

## TOTP Specifics

The `/challenge/totp` page structure:
```html
<input type="tel" id="totpPin" name="totpPin" autocomplete="off">
<button type="button">Next</button>
```

**CRITICAL**: `Input.insertText` APPENDS to `type=tel` fields. Always use:
```javascript
document.getElementById('totpPin').value = '123456';
document.getElementById('totpPin').dispatchEvent(new Event('input', {bubbles: true}));
```

Then click Next:
```javascript
Array.from(document.querySelectorAll('button')).find(b => b.innerText === 'Next')?.click()
```

## Combined Google Sign-in Form (New)

Son Google sign-in sayfası bazen email (`#identifierId`) ve password (`input[type=password]`)
alanlarını aynı sayfada gösterir.

**Belirtileri**: `email=True`, `pwd=True`, `next=True`, `pwdnext=False`

**Çözüm**:
1. Password alanını JavaScript ile doldur (`el.value = 'password'`)
2. `#identifierNext`'e tıkla (bu formun submit butonudur)
3. `#passwordNext` yoksa panik yapma — `#identifierNext` submit eder

```javascript
document.querySelector('input[type=password]').value = 'password';
document.querySelector('#identifierNext').click();
```

## Google Login Anti-Bot Loop

Autologin ve manuel CDP login'de karşılaşılan döngüler:

### "Try another way" Sonsuz Döngüsü
`/challenge/selection` sayfasında "Try another way" tıklamak aynı sayfayı yükler.
**Çözüm**: `div[role=link]` içinde "Get a verification code from the Google Authenticator app"
yazan seçeneği doğrudan tıkla — "Try another way" ile uğraşma.

```javascript
document.querySelectorAll('div[role=link]').forEach(el => {
    if(el.innerText.includes('Google Authenticator')) el.click();
});
```

### "Too many failed attempts"
Aynı Chrome profilinde çok oturum denemesi yapılırsa Google 1 saat bloke koyar.
**Çözüm**: Farklı Chrome profili kullan. MCP her restartta yeni bir Chrome açar
(yeni port), bu clean profile sahiptir.

## MCP Server Lifecycle

Gateway restart sonrası MCP server ve Chrome davranışı:

1. Gateway yeni `notebooklm-mcp server --transport stdio --headless` başlatır (yeni PID)
2. Yeni MCP server undetected_chromedriver ile yeni Chrome açar (farklı port)
3. Yeni Chrome `chrome_profile_notebooklm` profilini kullanır
4. Profilde Cookies SQLite DB'de cookie varsa → bunları okur
5. Cookie'ler geçerliyse → NotebookLM'e gider, değilse login sayfasına

**Önemli port değişikliği**: Her restartta Chrome portu değişir. Tespit:
```bash
ps aux | grep "chromium.*remote-debugging-port" | grep -oP 'remote-debugging-port=\K[0-9]+'
```

## MCP Chrome Cookie Enjeksiyonu (Gateway Restart'sız)

Gateway restart almadan MCP'yi canlandırmak için:
1. Canlı Chrome'dan (örn. port 47407) cookie'leri çek: `Network.getAllCookies`
2. MCP'nin Chrome'una (örn. port 60079) enjekte et: `Network.setCookie`
3. Navigate to NotebookLM: `Page.navigate`

```python
for c in auth_cookies:
    ws.send("Network.setCookie", {
        "url": f"{'https' if c['secure'] else 'http'}://{c['domain'].lstrip('.')}{c['path']}",
        "name": c["name"], "value": c["value"],
        "domain": c["domain"], "path": c.get("path","/"),
        "secure": c.get("secure",False),
        "httpOnly": c.get("httpOnly",False),
        "sameSite": c.get("sameSite","Lax")
    })
```

**Not**: Bu yöntem cookie'leri sadece runtime'a ekler. Chrome restart'ında kaybolur.
Kalıcı olması için SQLite Cookies DB'ye yaz (SKILL.md'deki Cookie persistence bölümü).

### "Enter your password" → "Try another way" Loop
If clicking "Try another way" keeps showing the same page, look for:
- `div[role=link]` with text "Get a verification code from the Google Authenticator app"
- Click that directly instead of "Try another way"

### Rate Limiting
- Google blocks repeated automated login attempts
- "Too many failed attempts" → wait 30-60min or use different Chrome profile
- MCP's Chrome (port 60079) has a CLEAN profile — best for retry

### Auth Cookie Count Reference
- **53 cookies / 42 Google / 41 auth**: Healthy session (working)
- **43 cookies / 32 Google / 30 auth**: Semi-healthy (may expire soon)
- **23 cookies / 18 Google / 0 auth**: Dead (RotateCookiesPage hit)
- **0 cookies / 0 Google / 0 auth**: Fresh Chrome, no login

## Multi-Account Setup

NotebookLM notebooks may require specific Google accounts:
- **kenshin4155@gmail.com** (pro) — genel kullanım
- **isimgorulsunn@gmail.com** (legacy) — notebook sahibi

If access request page shows, the notebook owner (isimgorulsunn) needs to grant access to kenshin4155.
Bitwarden items: `google-pro` (kenshin4155), `google-isimgorulsunn` (legacy)
