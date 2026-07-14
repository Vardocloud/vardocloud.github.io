---
name: account-security-response
description: "Step-by-step incident response for account security alerts — verify, contain, recover, and correlate with automation"
version: 1.0.0
metadata:
  hermes:
    tags: [security, account, google, breach, incident-response, 2fa, phishing]
    category: security
---

# Account Security Incident Response

## When to Use
- User reports a "suspicious sign-in" or "new device login" alert from any platform
- User suspects their account has been compromised
- User asks for help with 2FA setup or password change
- Security alert from Google, Microsoft, or similar services

## Step 1: Verify the Alert
- Check the **sender email address** carefully:
  - **Legitimate Google**: `no-reply@accounts.google.com`
  - **Legitimate Microsoft**: `account-security-noreply@accountprotection.microsoft.com`
  - Anything else → likely phishing. Do not click links.
- If the user is unsure, ask them to **check the sender** in the mail app (long-press on mobile, hover on desktop) before taking any other action.
- **Tone**: Validate their concern immediately — never say "it's probably nothing." First acknowledge, then verify.

## Step 2: Containment (Priority Order)

### 2a. Change Password
- Direct user to: `myaccount.google.com/security` → **Password** → Change
- Use a strong, unique password not used elsewhere
- If they're away from computer, guide through Google app: Profile → Manage Account → Security

### 2b. Enable 2FA (Two-Step Verification)
- Same page → **2-Step Verification** → Enable
- **Authenticator app preferred** over SMS (Google Authenticator, Authy, Microsoft Authenticator)
- Scan QR code → enter the code shown → done
- **If the user says "authenticator açıyorum"** → confirm and move to next steps, don't interrupt

### 2c. Review Active Sessions
- Same page → **Your devices** or **Manage devices**
- Sign out any unrecognized devices

### 2d. Check Recovery Info
- Same page → **Recovery email** and **Recovery phone**
- Ensure attacker hasn't altered them

## Step 3: Investigate
- **Recent security events**: `myaccount.google.com/security` → Recent security activity
  - Shows location, device, timestamp of each sign-in attempt
  - If Google blocked it, status shows "Blocked" — user should see this confirmation
- **Have I Been Pwned**: Ask the user to check their email at haveibeenpwned.com
- **Password reuse**: If the compromised password was used elsewhere, those accounts need password changes too

## Step 4: Local Device Security
- **Windows Defender full scan**: Başlat → Windows Güvenliği → Virüs ve tehdit koruması → Tam tarama
- **Check open ports** (if user asks or you suspect a deeper breach):
  - Open Command Prompt as admin, run:
    ```
    netstat -ano | findstr LISTENING
    ```
  - Look for unrecognized listening ports
- **Windows Firewall**: Ensure default inbound rule is "Block"
- **File sharing**: Başlat → Gelişmiş paylaşım ayarları → Dosya ve yazıcı paylaşımı → Kapat (if not needed)

## Step 5: Correlation with Automation (Critical)

**THE KEY DISTINCTION: OAuth/API access ≠ web login attempt**

| Access Method | Triggers "New Sign-In" Alert? |
|---------------|-------------------------------|
| 🌐 Web login (user + password) | ✅ Yes — this is what the alert tracks |
| 🔑 OAuth 2.0 / API access | ❌ No — API calls don't count as "sign-in" |
| 📧 IMAP/SMTP with App Password | ❌ No |
| 🤖 Automated tools (OpenCode, cron jobs, scripts) via API | ❌ No — unless they're using direct password login |

**When the user asks "was this from [some automation]?":**
- Explain the distinction clearly — API tools do not cause web login alerts
- Only investigate further if the user explicitly asks and provides details about the tool
- Do NOT guess or suggest it "might be related" to automation

## Step 6: Post-Recovery
- If user was away from home: tell them to check the Google Security page themselves when they get back
- Confirm that 2FA + password change = fully protected
- Reassure: if Google blocked the attempt, the attacker never gained access

## Common User Questions & Responses

**"Amerika'dan girmiş olabilirler mi?"**
→ "Eğer mail gerçekse (no-reply@accounts.google.com), evet birisi denemiş. Ama Google tanımadığı cihazdan girişi engellemiştir. Yine de şifre değiştir + 2FA aç."

**"Portlardan girmiş olabilirler mi?"**
→ "Gmail port tabanlı bir saldırıyla girilemez — tamamen web/http üzerinden olur. Yani birisi ya şifreni bilerek denemiş, ya da başka bir sitede aynı şifreyi kullandığın için sızmış."

**"Şimdi evde değilim ne yapayım?"**
→ "2FA'yı telefondan açabilirsin. Eve gidince şifreni değiştir ve Google Güvenlik sayfasından cihazları kontrol et."

## Pitfalls
- ❌ Do NOT ask the user for their password or verification codes — ever
- ❌ Do NOT click links in the suspicious email to "check" — guide user to type URL manually
- ❌ Do NOT say "it's probably nothing" — validate their concern first, then analyze
- ❌ Do NOT list too many steps at once — give 2-3 actionable items, wait for completion
- ❌ Do NOT assume WSL can access Windows drives (`/mnt/c/`) for port checks — it's not always mounted
- ✅ Give the user the exact `netstat` command they can paste themselves
- ✅ If user is setting up 2FA, let them focus — handle parallel tasks yourself
