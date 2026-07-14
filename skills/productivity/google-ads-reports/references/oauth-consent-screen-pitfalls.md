# OAuth Consent Screen Pitfalls (Testing Mode)

When the Google Ads reports cron job fails with `invalid_grant: Token has been expired or revoked`, the recovery flow involves re-authorizing via OAuth. The following are common blockers at the OAuth consent screen step.

## OAuth Link → "Erişim engellendi: [app name], doğrulama süreci tamamlanmadı" (403)

**Cause:** The Google Cloud app is in "Testing" status and the user's email hasn't been added as a test user.

**Fix:**
1. User goes to https://console.cloud.google.com/auth/audience
2. Under "Test users" → "Add users" → enter their Google email → Save
3. Retry the OAuth link

## Save Button Greyed Out on Consent Screen

If the user fills in fields but the Save/Continue button stays disabled:

| Check | Correct Format | Common Mistake |
|-------|---------------|----------------|
| Developer contact email | Filled with a valid email | Left empty |
| App Domain | `example.com` (NO scheme) | `https://example.com` ❌ |
| Authorized domains | `example.com` (NO scheme) | `https://example.com` ❌ |
| Application Home Page | `https://example.com/` (WITH scheme) | `example.com` ❌ |
| Privacy Policy URL | `https://example.com/privacy-policy.html` | Left empty or wrong format |
| Terms of Service URL | Optional — can be left blank | Not required for Testing |

**Error message example:** "Invalid domain: must not specify the scheme (http:// or https://)"

## GitHub Pages as Free Domain

When the user has no domain for the OAuth consent screen:

1. Create GitHub repo: `<username>.github.io` (must be exact name, public)
2. Add `index.html` + `privacy-policy.html`
3. GitHub Pages auto-deploys in ~1 minute
4. Domain becomes `https://<username>.github.io/`

Use `https://<username>.github.io/privacy-policy.html` as the Privacy Policy URL.

## Testing Mode → ~7 Day Token Lifecycle

- Token auto-refreshes while actively used
- If unused for ~7 consecutive days, refresh token becomes invalid (`invalid_grant`)
- Recovery: fresh OAuth flow (Step 3-4 in google-workspace setup)
- Permanent fix: Publish app to "In Production" (requires app verification)
