# Gmail Inbox Reading via Google API

## When to use

The user says "maillere bak", "mail var mı", "gelen kutusunu kontrol et", or any variation of checking Gmail inbox.

## Preferred Flow (2026-06-16)

### 1. Google API'yi dene (ÖNCELİKLİ)

```bash
GAPI="python $HOME/.hermes/skills/productivity/google-workspace/scripts/google_api.py"
$GAPI gmail search "in:inbox" --max 20
```

Token `~/.hermes/google_token.json` üzerinden otomatik çalışır. Edel'in hesabı zaten yetkilendirilmiş — denemeden atlama.

Bitwarden'a gitmene, browser açmana, OAuth code istemene gerek yok. API varsa direkt kullan.

### 2. Tek mail detayı

```bash
$GAPI gmail get MESSAGE_ID
```

### 3. AUTHENTICATED (partial) — Scope'lar eksikse

`$GSETUP --check` çıktısında `AUTHENTICATED (partial)` ve `gmail.readonly` eksikse API hazır değildir. 
İki seçenek:
- OAuth'u Gmail scope'ları ile yeniden yetkilendir (Cloud Console'dan)
- Veya doğrudan Bitwarden → browser fallback'ine geç

### 4. API yoksa/scope eksikse → Bitwarden fallback

Önce `curl http://127.0.0.1:8087/status` ile bw serve REST API'nin unlocked olduğunu kontrol et, 
ardından Bitwarden'dan credential çekip browser ile Gmail'e gir.

## Neden Browser Automation Değil?

Google login sayfası headless Chrome'da bot detection'a takılır:
- "Couldn't sign you in" sayfası
- Invisible button element'leri
- Captcha/audio challenge

API çalışıyorken browser'a gerek yok. API her zaman daha hızlı ve güvenilir.

## PITFALL: OAuth Code İsteme

**Yanlış:** "Gmail'e bağlanmam gerekiyor, onay kodu göndereyim mi?"
**Doğru:** API'yi direkt dene — token zaten var.

Edel "ya şöyle yap: bitwarden password manager'a git" dediğinde bile API çalışıyor olabilir. Önce API'yi dene, çalışmazsa alternatife geç.
