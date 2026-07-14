# Bitwarden Secrets Manager — OAuth2 Setup with bws CLI

## Overview

Hermes Bitwarden SM integration (`secrets.bitwarden`) uses the `bws` CLI to pull secrets from Bitwarden Secrets Manager at process startup. The CLI uses a `0.{org_id}.{encrypted}:{key}` format **access token** stored as `BWS_ACCESS_TOKEN` in `.env`.

## OAuth2 client_credentials Token Acquisition

Bitwarden Identity API requires SPECIFIC header + body parameters:

### Headers
```
Content-Type: application/x-www-form-urlencoded
Bitwarden-Client-Version: 2025.1.0
```

### Body (form-encoded)
```
client_id=<user.xxx>
client_secret=<secret>
scope=api
grant_type=client_credentials
deviceType=8
deviceIdentifier=<uuid>
deviceName=bws
```

### Endpoints
| Region | URL |
|--------|-----|
| US Cloud | `https://identity.bitwarden.com/connect/token` |
| EU Cloud | `https://identity.bitwarden.eu/connect/token` |

### Critical Details
- **Device info goes in BODY**, NOT headers. Sending `Bitwarden-Device-Type` etc. as headers returns `device_error`.
- `Bitwarden-Client-Version` IS a header — without it, `version_header_missing` error.
- Token response is a JWT (`eyJ...`), usable as `BWS_ACCESS_TOKEN`.

## bws CLI Setup

### Install/Upgrade
```bash
# Hermes auto-installs bws v2.0.0. For newer version:
wget "https://github.com/bitwarden/sdk-sm/releases/download/bws-v2.1.0/bws-aarch64-unknown-linux-gnu-2.1.0.zip"
unzip -o bws.zip && chmod +x bws
cp bws ~/.hermes/bin/bws
```

### Config Commands
```bash
bws config server-identity https://identity.bitwarden.com
bws config server-api https://api.bitwarden.com
```

Note: Do NOT use `bws config set` — the `set` subcommand does not exist. Direct `bws config <NAME> <VALUE>`.

### Project Management
```bash
# List projects
bws --access-token "$TOKEN" project list --output json

# Create project (name is positional, NOT --name flag)
bws --access-token "$TOKEN" project create "project-name" --output json
```

### Token Passing
`--access-token` flag works reliably. `BWS_ACCESS_TOKEN` env var may fail if the token contains special characters or newline artifacts from `.env`. When the CLI says "Doesn't contain a decryption key" via env var but works with `--access-token`, the env file has a subtle formatting issue — fix by re-saving the token line or using the flag directly.

### Pushing .env Secrets to Bitwarden
When moving existing API keys from `.env` to Bitwarden SM:

```bash
bws --access-token "$TOKEN" secret create "KEY_NAME" "key_value" "PROJECT_ID" --output json
```

The `PROJECT_ID` is a positional argument (the 3rd arg), NOT `--project-id`. Use `secret edit <ID> --key <KEY> --value <VALUE>` to update existing secrets.

Be aware of rate limits: ~10 secrets in rapid succession triggers HTTP 429. Add `sleep 3` between batches.

### Hermes Bitwarden Setup
```bash
hermes secrets bitwarden setup \
  --access-token "$TOKEN" \
  --server-url "https://vault.bitwarden.com" \
  --project-id "$PROJECT_ID"
```

## Troubleshooting

### "Doesn't contain a decryption key"
- Token format `0.{org_id}.{encrypted}:{key}` — ensure all 3 `.`-separated parts are present
- Try passing token via `--access-token` instead of env var
- Verify token was created from Secrets Manager (not Organization API key)
- Upgrade bws CLI to latest version (v2.1.0+)

### "device_error: No device information provided"
Fix: Add `deviceType`, `deviceIdentifier`, `deviceName` to request BODY, not headers.

### "version_header_missing"
Fix: Add `Bitwarden-Client-Version: 2025.1.0` header.

## Reference

- [Bitwarden Secret Decryption docs](https://bitwarden.com/help/secret-decryption/)
- [Bitwarden SDK-SM Releases](https://github.com/bitwarden/sdk-sm/releases)
- [bws CLI docs](https://bitwarden.com/help/secrets-manager-cli/)
