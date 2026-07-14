# Bitwarden Secrets Manager — Secret CRUD Operations

Day-to-day operations with the `bws` CLI.

## Prerequisites

- `BWS_ACCESS_TOKEN` set (from initial OAuth2 setup)
- `bws` binary installed (see bitwarden-sm-oauth2-setup reference)

## CLI Syntax (v2.x)

### List Secrets

```bash
bws secret list PROJECT_ID
```

Process output server-side to avoid exposing values (see Provider Visibility section in SKILL.md):

```bash
# Show key names with masked values
bws secret list PROJECT_ID | python3 -c "
import json, sys
data = json.load(sys.stdin)
for s in data:
    val = s['value']
    masked = val[:6] + '...' + val[-4:] if len(val) > 12 else '****'
    print(f'  {s[\"key\"]:40s} {masked}')
"
```

### Create a Secret

```bash
bws secret create KEY_NAME --value "VALUE" --project-id PROJECT_ID --organization-id ORG_ID
```

### Edit a Secret

```bash
bws secret edit SECRET_ID --key "NEW_KEY_NAME"
bws secret edit SECRET_ID --value "NEW_VALUE"
bws secret edit SECRET_ID --key "NEW_KEY" --value "NEW_VALUE"
```

### Delete a Secret

```bash
bws secret delete SECRET_ID
```

### Check for Duplicate Keys

```bash
bws secret list PROJECT_ID | python3 -c "
import json, sys
from collections import Counter
data = json.load(sys.stdin)
names = [s['key'] for s in data]
dupes = {k: v for k, v in Counter(names).items() if v > 1}
if dupes:
    print(f'DUPLICATE keys: {dupes}')
else:
    print('No duplicate keys')
"
```

## Naming Convention

Secret key name = environment variable name in ALL_CAPS.

| Key | Service |
|-----|---------|
| `POLLINATIONS_API_KEY` | Pollinations AI |
| `MISTRAL_API_KEY` | Mistral AI |
| `BRAVE_API_KEY` | Brave Search |
| `SERP_API_KEY` | serpapi.com (NOT the same as Serper) |
| `GITHUB_TOKEN` | GitHub (uses TOKEN suffix, not API_KEY) |
| `HUGGINGFACE_API_KEY` | HuggingFace — normal (read) token |
| `HUGGING_FACE_API_KEY` | HuggingFace — write token (separate scope) |

**Two tokens for the same service:** Different scopes/tokens get different keys.
Separate with `_` suffix: `RUNWAY_API_KEY`, `RUNWAY_API_KEY_2` for two accounts.

**Serp vs Serper** are DIFFERENT platforms:\n- Serp = serpapi.com\n- Serper = serper.dev\nEach has its own independent API key.\n\n## override_existing: true (Priority Rule)\n\nHermes config'inde `secrets.bitwarden.override_existing: true` varsa:\n- Hermes önce `.env`'yi okur\n- Sonra Bitwarden'a bakar\n- Aynı isimde secret varsa **Bitwarden'daki değer `.env`'dekini ezer**\n- `.env`'de olup Bitwarden'da olmayan key'ler olduğu gibi kalır\n\nYani Bitwarden her zaman kazanır. Eğer `false` olsaydı, `.env`'de olan değerler korunur,\nsadece `.env`'de olmayanlar Bitwarden'dan eklenirdi.\n\nBu ayar config.yaml'de `secrets.bitwarden` blokunda:\n```yaml\nsecrets:\n  bitwarden:\n    enabled: true\n    project_id: \"2b375eb2-293e-4774-b5e5-b46601543563\"\n    override_existing: true   # Bitwarden kazanır\n```\n\n## Provider Visibility: User-Adds-Themselves Pattern\n\n> Edel'in kuralı: **\"secretları deepseek görmemeli\"**\n\nPrimary model (DeepSeek) tüm terminal çıktısını ve tool call parametrelerini görür.\n`bws secret create --value \"SIFREM\"` yazarsan, sifre DeepSeek'e gider.\n\n**En güvenli yol:** Kullanıcının kendisinin secret eklemesi.\n\n1. Vanitas sadece **key adını ve project_id'yi** söyler\n2. Kullanıcı kendi terminalinde `bws secret create KEY --value \"...\" --project-id X` çalıştırır\n3. Değer asla bir AI modeli context'ine girmez\n\n**Vanitas'ın yapabileceği:** Değer zaten `.env`'deyse (önceden girilmiş), Vanitas\nBitwarden'a taşıyabilir — çünkü değer zaten primary model context'inde.\n\n## Helper Script\n\nShell quoting sorunları (Python f-string vs shell) yaşamamak için:\n`scripts/list_secrets.py` — BWS_ACCESS_TOKEN'ı `.env`'den okur, maskeli liste basar.\n\n```bash\npython3 ~/.hermes/skills/security/sensitive-data-pipeline/scripts/list_secrets.py\n```
