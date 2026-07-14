# GitHub Push Protection — Secret Fix Prosedürü

Bir `no_agent=true` cron script'i veya LLM-driven job, `git push` yaparken GitHub Push Protection'a takıldığında izlenecek yol.

## Teşhis

Git push çıktısında şu pattern'i ara:

```
remote: error: GH013: Repository rule violations found for refs/heads/main.
remote: - GITHUB PUSH PROTECTION
remote:   — Push cannot contain secrets
remote:   —— LinkedIn Client Secret ————————————————————————————
remote:    locations:
remote:      - commit: a1040ec
remote:        path: skills/xxx/scripts/linkedin_api.py:17
```

**Anahtar bilgiler:**
- Hangi dosyada (`path:`)
- Hangi secret türü (`LinkedIn Client Secret`, `GitHub PAT`, AWS key vb.)
- Hangi commit'te (`commit:` SHA'sı)

## Çözüm Akışı

### 1. Secret'ı Kaynaktan Kaldır

Hardcoded secret'ı env variable, BWS (Bitwarden Secrets Manager), veya credentials file'dan okuyacak şekilde değiştir.

**Python — BWS / env dosyası:**
```python
import os, json, subprocess
HOME = os.path.expanduser("~")
CRED_FILE = f"{HOME}/.hermes/secrets/service.env"

def _load_credentials():
    if not os.path.exists(CRED_FILE):
        raise RuntimeError(f"Credentials file not found: {CRED_FILE}")
    creds = {}
    with open(CRED_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                creds[k.strip()] = v.strip()
    cid = creds.get("SERVICE_CLIENT_ID")
    csec = creds.get("SERVICE_CLIENT_SECRET")
    if not cid or not csec:
        raise RuntimeError("Missing credentials in env file")
    return cid, csec
```

**Python — BWS (Bitwarden Secrets Manager):**
```python
import subprocess, json
result = subprocess.run(["bws", "secret", "get", "<SECRET_ID>"],
                        capture_output=True, text=True, timeout=15)
token = json.loads(result.stdout)["value"]
```

### 2. .gitignore Güncelle

Secret içeren dosyanın bir daha commit'e eklenmemesi için `.gitignore`'a ekle:

```gitignore
# Scripts with hardcoded secrets — use BWS instead
skills/linkedin-post/linkedin/scripts/linkedin_api.py
```

**⚠️ .gitignore pattern'leri:** `.gitignore`'daki path pattern'leri **görecelidir**. `scripts/linkedin_api.py` sadece kök dizindeki `scripts/` klasörüyle eşleşir, `skills/linkedin-post/linkedin/scripts/linkedin_api.py` ile eşleşmez. Alt dizinlerdeki dosyalar için tam yolu yaz.

**Doğrulama:**
```bash
cd ~/.hermes
git add --dry-run skills/linkedin-post/linkedin/scripts/linkedin_api.py
# Çıktı boşsa → .gitignore çalışıyor (dosya eklenmez)
# Dosya adı yazıyorsa → .gitignore pattern'i yanlış
```

### 3. Git History'den Secret'ı Temizle

Secret'ın commit history'den tamamen kaldırılması gerekir (amend, reset veya rebase ile).

#### Durum A: Secret sadece son commit'te var (en yaygın)

```bash
cd ~/.hermes
git log --oneline
# Örn: a1040ec Daily backup - 2026-07-14
#      66dfabd Initial backup - 2026-07-11

# Secret'ı son commit'e sokan commit SHA'sını bul
git log --oneline --all -- <dosya-yolu>
# => a1040ec

# Eğer son commit'ten başka parent da yoksa (rebase edilmemişse):
git reset --soft <parent-sha>   # Örn: git reset --soft 66dfabd
git add .gitignore <düzeltilen-dosya>
git commit -m "<önceki commit mesajı>"
git push origin main
```

**Not:** `git reset --soft` son commit'i geri alır, değişiklikleri stagging'de tutar. Secret içeren eski commit artık history'de yoktur.

#### Durum B: Secret geçmiş commit'lerde de var

`git filter-repo` veya `git rebase -i` ile temizle:

```bash
# filter-repo ile belirli bir dosyayı tüm history'den sil
pip install git-filter-repo
git filter-repo --path <dosya-yolu> --invert-paths
git remote add origin <remote-url>
git push --force origin main
```

**⚠️ Dikkat:** `git filter-repo` tüm commit SHA'larını değiştirir. Takım arkadaşlarınız varsa önce haber verin.

### 4. Push

```bash
cd ~/.hermes
timeout 30 git push origin main
```

Başarılı çıktı:
```
<old-sha>..<new-sha>  main -> main
```

Hata devam ediyorsa:
- Secret hâlâ commit history'de olabilir → `git log --all --oneline -- <dosya>` ile kontrol et
- GitHub's cached scan result'u bloke ediyor olabilir → `git push --force` dene (eğer remote'tan sonra güncellenmemişse)
- Farklı bir dosyada/commit'te başka bir secret daha olabilir → tüm push çıktısını oku

## Önleme

1. **İlk commit'ten önce `.gitignore`'a hassas dosyaları ekle:** Secret içeren script'leri `secrets/` veya `scripts/` altında tut, `.gitignore`'da izin verme
2. **Pre-commit hook:** `git secrets` veya `detect-secrets` ile commit öncesi tara
3. **BWS kullan:** API key'leri asla dosyada hardcoded tutma, Bitwarden Secrets Manager'dan runtime'da oku (`bws secret get <ID>`)
4. **LinkedIn API key'leri için:** `~/.hermes/secrets/linkedin.env`'de tut, hardcoded fallback EKLEME

## Gerçek Vaka: daily_backup.py LinkedIn Secret (14 Tem 2026)

**Hata:** `daily_backup.py` (no_agent=true, schedule=02:00) `git push` yaparken GitHub Push Protection tarafından bloke edildi.

**Kök neden:** `skills/linkedin-post/linkedin/scripts/linkedin_api.py` dosyasında LinkedIn Client Secret hardcoded duruyordu (satır 17: `CLIENT_SECRET = "WPL_AP1...."`).

**Çözüm adımları:**
1. Hardcoded `CLIENT_ID` ve `CLIENT_SECRET` kaldırıldı → `_load_credentials()` fonksiyonu sadece `~/.hermes/secrets/linkedin.env`'den okur (bu dosyada zaten vardı)
2. `.gitignore`'a `skills/linkedin-post/linkedin/scripts/linkedin_api.py` eklendi
3. `git reset --soft 66dfabd` ile son commit geri alındı (a1040ec history'den düştü)
4. `.gitignore` değişikliği staging'e eklendi
5. `git commit -m "Daily backup - 2026-07-14"` ile yeni commit oluşturuldu (3a79a64 — secret yok)
6. `git push origin main` ✅ başarılı
