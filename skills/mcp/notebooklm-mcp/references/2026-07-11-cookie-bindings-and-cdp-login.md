# 11 Tem 2026 — Cookie Binding & CDP Credential Login

## Session Summary

NotebookLM MCP auth expired. Keepalive Chrome restart caused permanent CookieMismatch.
Solution: CDP credential login on keepalive Chrome → cookie injection to MCP Chrome.

## Key Findings

### 1. Keepalive Chrome Restart = CookieMismatch (Permanent)

- Keepalive Chrome'u kill edip restart etmek Google'ın cookie binding'ini kırar
- MCP aynı profili kullansa bile `accounts.google.com/CookieMismatch` hatası alınır
- **Çözüm:** Keepalive Chrome'u restart etme. Crash olursa CDP credential login yap (aşağıdaki gibi)

### 2. CookieMismatch vs Accountchooser

| Redirect URL | Anlamı |
|---|---|
| `accounts.google.com/CookieMismatch` | Aynı profil, iki Chrome instance'ı, cookie binding uyuşmazlığı |
| `accounts.google.com/accountchooser` | Cookie'ler tanındı, hesap seçimi gerekli |
| `accounts.google.com/signin/identifier` | Hiç cookie yok, email girilmeli |
| `accounts.google.com/challenge/pwd` | Şifre giriş ekranı |

### 3. CDP Credential Login Flow (Tested ✅)

Keepalive Chrome'da oturum açmak için:

```
Step 1: Chrome notebooklm.google.com'a gider → accountchooser sayfası
Step 2: document.querySelector('[data-identifier="isimgorulsunn@gmail.com"]').click()
Step 3: /challenge/pwd sayfasına yönlenir
Step 4: Bitwarden'dan şifre al (bw-serve port 8087, item: "Google-isimgorulsunn")
Step 5: Şifreyi native value setter ile input'a yaz
Step 6: Input.dispatchKeyEvent ile Enter tuşu gönder
Step 7: NotebookLM açılır ✓
```

### 4. MCP Chrome'a Cookie Injection

Keepalive Chrome login olduktan sonra MCP'nin Chrome'una cookie enjekte et:

```
keepalive WS → Network.getAllCookies → cookies listesi (52 adet)
MCP WS → Network.setCookies({cookies: unique}) → Page.navigate(notebooklm)
```

**Not:** SQLite Cookies dosyasını kopyalamak çalışmaz (CookieMismatch).
Runtime CDP injection çalışır.

### 5. nb_keepalive.py authuser Handling

```
SKIP: not logged in for this account (authuser=1)
```

Aynı profilde birden çok Google hesabı varsa, biri login olmayabilir.
Bu uyarı normaldir, işlemi etkilemez.

### 6. Cookie Domain Dağılımı (Keepalive Chrome — 52 cookies)

| Domain | Adet |
|---|---|
| .google.com | 18 |
| .youtube.com | 11 |
| .google.com.tr | 10 |
| accounts.google.com | 7 |
| .notebooklm.google.com | 3 |
| notebooklm.google.com | 2 |
| ogs.google.com | 1 |

### 7. Hermes MCP Registration

```bash
# Bu timeout alır (Chrome başlatma + login > 30s):
hermes mcp add notebooklm-mcp --command /usr/local/bin/notebooklm-mcp --args '--config config.json'

# Önce config'siz ekle (disabled olur), sonra etkinleştir:
hermes mcp add notebooklm-mcp --command /usr/local/bin/notebooklm-mcp
# (timeout, but config saved)
hermes mcp enable notebooklm-mcp
```
