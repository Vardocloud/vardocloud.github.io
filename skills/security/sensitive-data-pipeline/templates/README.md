# Templates

| File | Purpose | Fields | Output Format |
|------|---------|--------|-------------|
| `elements_secure_login.html` | Generic email+password login | email, password | `VANITAS_SECURE::<base64>` |
| `bw-token-form.html` | Bitwarden OAuth2 client credentials | client_id, client_secret, scope, grant_type | raw base64 (JSON) |
| `secure-master-password.html` | Bitwarden master password (single field) | password | `VANITAS_SECURE::<base64>` |
| `set-or-key.sh` | SSH-based API key storage script | reads stdin, writes to /tmp/.or_key | stdout |
| `api-key-form.html` | Single API key via cloudflared tunnel (single field) | api_key (password field) | `VANITAS_SECURE::<base64>` |

## Usage

All HTML templates are **self-contained, zero-network-call** JavaScript pages:
1. Serve over HTTPS via localhost.run tunnel (see `references/localhost-run-cred-capture.md`)
2. User fills fields → clicks "Kod Üret" → base64 auto-copied
3. Fields auto-clear after generation (prevents re-exposure)
4. Paste base64 into chat → decode via `mcp_local_secure_secure_ask` (local Qwen 3.5)

## Reference
- `references/localhost-run-cred-capture.md` — tunnel setup + teardown workflow
- `references/bitwarden-identity-api-oauth2.md` — Bitwarden Identity API quirks (device info in body, version header)
- `references/bw-cli-setup.md` — bw CLI login + unlock + `bw serve` systemd service automotion

### 🔑 Unlock Method Correction

`echo "PASSWORD" | bw unlock` **does NOT work.** `bw unlock` reads from a TTY
and ignores stdin. Use `--passwordfile` instead:

```bash
bw unlock --raw --passwordfile <(gpg --decrypt --quiet bw_masterpass.gpg)
```

See `references/bw-cli-setup.md` for full systemd service setup with GPG-encrypted
master password and auto-start on boot.

## Reference
- `references/bitwarden-identity-api-oauth2.md` — Bitwarden Identity API quirks (device info in body, version header)
