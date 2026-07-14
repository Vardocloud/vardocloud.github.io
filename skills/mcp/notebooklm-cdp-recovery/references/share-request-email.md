# NotebookLM Share Request Email Handling

## Overview

When a user clicks "EriÅŸim iste" (Request Access) on a NotebookLM notebook,
Google sends a share request email to the notebook owner's inbox.
This email contains a "View Request" link (c.gle shortened URL) that opens
an approval page.

## Email Detection via Himalaya

```bash
# List recent emails in isimgorulsunn inbox
himalaya envelope list --page-size 20 --output json | python3 -c "
import sys,json
for e in json.load(sys.stdin):
    if 'Share Request' in e.get('subject',''):
        print(f\"ID: {e['id']} | {e['subject']} | {e['from']['addr']}\")
"
```

**Key identifiers**:
- Subject: "Share Request for ... Ekonomi ZekasÄ± ..."
- From: "NotebookLM-noreply@google.com"
- To: isimgorulsunn@gmail.com

## Reading the Email

```bash
# Read plain text version
himalaya message read <ID>

# Export raw MIME for URL extraction
himalaya message export <ID> --full | grep -oP 'https?://[^"<> ]+' | head -5
```

The raw email contains only c.gle tracking links.
These require a browser session to resolve â€” they return HTTP 404 from curl.

## c.gle Link Behavior

- **Format**: `https://c.gle/AKMee0...` (Google click tracker)
- **curl**: returns HTTP 404 with no redirect
- **Browser (CDP)**: requires JavaScript and valid Google auth cookies to redirect
- **Resolution**: must be opened in a Chrome instance where isimgorulsunn is signed in

## Workflow

1. User clicks "EriÅŸim iste" on NotebookLM access request page
2. Email arrives in isimgorulsunn inbox within seconds
3. Agent finds email via Himalaya
4. If isimgorulsunn has valid session: open c.gle link in Chrome CDP
5. If session expired: ask Edel to open the email in browser and approve
6. After approval: kenshin4155 can access the notebook directly

## Alternative

If CDP login for isimgorulsunn is stuck (no TOTP, phone verification needed),
the simplest path is:
- Ask Edel to open notebooklm.google.com with isimgorulsunn
- Wait 5-10 seconds
- Agent extracts cookies from keepalive Chrome
- MCP works with the notebook
