# bw-serve Down Recovery (20 June 2026)

## Scenario
Cron job loaded `upwork-cookie-session` skill, attempted session refresh but hit a blocker:
- `bw-serve` on port 8087 was not running (Docker container restart)
- GPG secret key (`07449FA9ACE3A935`) missing from the container — only on host machine
- `bws` (Bitwarden Secrets Manager) had no upwork password stored
- Result: cookies were 107/111 expired, password unreachable → **session refresh failed**

## Full Diagnosis Path

```bash
# 1. Check bw-serve
curl -s http://localhost:8087/status
# → curl: (7) Failed to connect to localhost port 8087

# 2. Check GPG keys
gpg --list-secret-keys
# → Empty output → no secret keys on this machine

# 3. Try GPG decrypt manually
gpg --decrypt ~/.hermes/secrets/bw_masterpass.gpg
# → gpg: public key decryption failed: No secret key
# → gpg: decryption failed: No secret key

# 4. Check bws (Bitwarden Secrets Manager)
test -x ~/.hermes/bin/bws && echo "bws available"
env | grep BWS_ACCESS_TOKEN  # should show token
# List project and secrets
~/.hermes/bin/bws project list
# → Find project ID, then:
~/.hermes/bin/bws secret list <project-id> | python3 -c "
import json,sys
data = json.load(sys.stdin)
upw = [s for s in data if 'upwork' in s.get('key','').lower()]
print(f'{len(upw)} upwork secrets')
"

# 5. Check if /tmp/pw_val.txt exists from a previous run
ls -la /tmp/pw_val.txt 2>/dev/null
# Likely doesn't exist (temp files cleaned on reboot)

# 6. Check cookie file
cat ~/.hermes/secrets/upwork_cookies.json | node -e "
const fs = require('fs');
const c = JSON.parse(fs.readFileSync('/dev/stdin','utf8'));
const n = Date.now();
let v=0,e=0;
c.forEach(x=>{(x.expirationDate||x.expires)*1000>n?v++:e++});
console.log('Valid:',v,'Expired:',e,'Total:',c.length);
"
```

## Decision Tree for Agent

```
bw-serve running?
  ├── YES → use curl to get password → /tmp/pw_val.txt → run script
  └── NO  → bws available?
              ├── YES → bws has UPWORK_PW secret?
              │         ├── YES → extract to /tmp/pw_val.txt → run script
              │         └── NO  → BLOCKED
              └── NO  → BLOCKED

BLOCKED → Report to user with:
         • Cookie stats (valid/expired/total)
         • Which services failed (bw-serve, GPG, bws)
         • Recovery options
```

## Recovery Options for User

### Option A: Start bw-serve (fastest)
Run on the machine that has the GPG secret key:
```bash
bash ~/.hermes/scripts/bw-serve.sh
```
This decrypts `bw_masterpass.gpg` and starts `bw serve` on port 8087.

### Option B: Add upwork password to bws (permanent fix)
Once the password is known (from a successful bw-serve start or user input):
```bash
~/.hermes/bin/bws secret create UPWORK_PW \
  --value "the-password" \
  --project-id <project-id> \
  --organization-id <org-id>
```
After this, bws becomes a permanent fallback that doesn't need bw-serve.

### Option C: Export fresh cookies from Chrome
1. Log into Upwork on Chrome with "Keep me logged in"
2. Use "Export cookie JSON file for Puppeteer" extension
3. Export as JSON
4. Send file to Vanitas → overwrite `~/.hermes/secrets/upwork_cookies.json`
5. Next cron run will find valid cookies and skip login entirely

## Why This Happens

The system runs inside a Docker container on WSL (Windows Subsystem for Linux). Docker containers do NOT use systemd, so services like `bw-serve` that depend on systemd user services do NOT auto-start on container restart. Any container restart (Hermes update, host reboot, Docker restart) will stop bw-serve.

The GPG-encrypted master password (`bw_masterpass.gpg`) was encrypted with a key stored on the original setup machine, not in the container's GPG keyring. This means the container cannot decrypt it independently.

## Prevention

Store the upwork password in **both**:
1. **Bitwarden Password Manager** (via bw-serve) — for normal operation
2. **Bitwarden Secrets Manager** (bws) — as Docker/WSL-safe fallback
