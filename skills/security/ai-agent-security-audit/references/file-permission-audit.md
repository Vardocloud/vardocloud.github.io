# File Permission Audit — Known Findings (July 2026)

## Audit Command

```bash
# Find all world-readable credential files in ~/.hermes
find ~/.hermes -type f \( -name '*key*' -o -name '*token*' -o -name '*secret*' -o -name '*password*' -o -name '*cred*' \) -perm /o+r 2>/dev/null | grep -v '/\.git/' | grep -v 'backup-'
```

## Findings from 16 July 2026 Audit

### CRITICAL — World-Readable (777 / 644)

| File | Permission | Content |
|------|-----------|---------|
| `secrets/apa.env` | 777 | APA account credentials |
| `secrets/apa_cookies.json` | 777 | APA session cookies |
| `secrets/bw_client_id.txt` | 777 | Bitwarden client ID |
| `secrets/bw_client_secret.txt` | 777 | Bitwarden client secret |
| `secrets/google_cse_api_key.txt` | 777 | Google Custom Search API key |
| `secrets/linkedin.env` | 777 | LinkedIn OAuth tokens |
| `soniox_api_key.txt` | 777 | Soniox STT API key |
| `soniox_password.txt` | 777 | Soniox account password |
| `serper_key.txt` | 777 | Serper API key |
| `serper_key_fallback.txt` | 777 | Serper backup API key |
| `tavily_key.txt` | 777 | Tavily API key |
| `brave_key.txt` | 777 | Brave Search API key |
| `google_client_secret.json` | 644 | Google OAuth client secret |

### OK — Properly Restricted (600)

| File | Permission | Content |
|------|-----------|---------|
| `.env` | 600 | Main environment (NVIDIA, GROQ, ZENMUX, etc. keys) |
| `google_token.json` | 600 | Google OAuth token |
| `secrets/opencode_go_api_key.txt` | 600 | OpenCode Go API key |
| `secrets/linkedin_token.json` | 600 | LinkedIn OAuth token |
| `apa_email.txt` | 600 | APA email (separate) |
| `apa_password.txt` | 600 | APA password (separate) |
| `instagram_graph_token.txt` | 600 | Instagram Graph token |
| `.nb_totp_secret` | 600 | NotebookLM TOTP secret |
| `.nb_totp_secret_pro` | 600 | NotebookLM PRO TOTP secret |
| `.git-credentials` | 600 | GitHub credentials |

## Fix Command

```bash
cd ~/.hermes
chmod 600 secrets/* 2>/dev/null
chmod 600 soniox_api_key.txt soniox_password.txt 2>/dev/null
chmod 600 serper_key.txt serper_key_fallback.txt tavily_key.txt brave_key.txt 2>/dev/null
chmod 600 google_client_secret.json 2>/dev/null
```

## Verification

After fix, `find ~/.hermes -type f -perm /o+r` should show NO credential files.
