# File Permission Audit — Known Findings (July 2026)

## Audit Command

```bash
# Full scan: find world-readable files matching credential or env patterns
find ~/.hermes -type f \( \
  -name '*key*' -o -name '*token*' -o -name '*secret*' -o \
  -name '*password*' -o -name '*cred*' -o -name '*.env' -o -name '.env*' \
\) -perm /o+r 2>/dev/null | grep -v '/\.git/' | grep -v 'backup-' | grep -v 'node_modules' | sort
```

## Findings from 17 July 2026 Audit (after fix)

All previously world-readable credential files have been fixed to **600** (owner read/write only).

### CRITICAL — Fixed to 600

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
| `google_client_secret.json` | 777 | Google OAuth client secret | ✅ 17 Jul |
| `.env.bak-*` files | 777 | Old env backups (API keys) | ✅ 17 Jul |
| `.env.example` | 777 | Example env (may contain keys) | ✅ 17 Jul |
| `bardo_instagram.env` | 777 | Instagram automation credentials | ✅ 17 Jul |

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

## Remediation Steps

For each world-readable credential or env file, run the permission restriction command (owner read/write only). Include env backup files and example files — they often carry live credentials.

```bash
cd ~/.hermes
chmod 600 secrets/* 2>/dev/null
chmod 600 soniox_api_key.txt soniox_password.txt 2>/dev/null
chmod 600 serper_key.txt serper_key_fallback.txt tavily_key.txt brave_key.txt 2>/dev/null
chmod 600 google_client_secret.json 2>/dev/null
```

## Known Gaps

| File | Permission | Owner | Issue |
|------|-----------|-------|-------|
| `linkedin-poster/.env` | 777 | root:root | Needs root to fix permissions |

## Pitfalls

- **The audit scan catches named patterns only.** A file named `backup.env.20260528` won't match `*key*` — include `.env*` patterns.
- **Environment backup files (.env.bak, .env.example) often contain live credentials.** Treat them with same severity as the primary `.env` file.
- **Secrets leak through backups.** 600-permission files may be included in backup archives with broader permissions. Exclude credential paths from backup scripts.

## Verification

After fix, `find ~/.hermes -type f -perm /o+r` shows no credential files.
