# Bitwarden Identity API — OAuth2 Client Credentials

## Endpoint
```
POST https://identity.bitwarden.com/connect/token
Content-Type: application/x-www-form-urlencoded
Bitwarden-Client-Version: 2025.1.0
```

## Body (form-urlencoded)
| Field | Value | Notes |
|-------|-------|-------|
| `client_id` | `user.<uuid>` | Machine Account client ID |
| `client_secret` | `<secret>` | Machine Account secret |
| `scope` | `api` | Required |
| `grant_type` | `client_credentials` | Fixed for OAuth2 machine accounts |
| `deviceType` | `8` | Integer. 8=LinuxDesktop |
| `deviceIdentifier` | `<uuid>` | UUID v4. Can be all-zeroes for one-shot |
| `deviceName` | `bws` | Arbitrary string |

## Key Quirk — device info goes in BODY, not headers
Bitwarden Identity API (as of 2025) rejects requests that omit device info.
The device fields (`deviceType`, `deviceIdentifier`, `deviceName`) MUST be sent
as form body parameters — NOT as HTTP headers. Headers like
`Bitwarden-Device-Type`, `Bitwarden-Device-Name`, `Bitwarden-Device-Identifier`
do NOT work; the API returns `device_error: "No device information provided"`.

Additionally, `Bitwarden-Client-Version` MUST be sent as an HTTP header.
Omitting it returns `version_header_missing`.

## Response (success)
```json
{
  "access_token": "eyJ...",
  "expires_in": 3600,
  "token_type": "Bearer",
  "scope": "api"
}
```

## Warning
The JWT token (`eyJ...`) from OAuth2 client_credentials is NOT the same format
as Bitwarden's own organization access token (`0.xxx...`). The `bws` CLI
expects the organization access token format. OAuth2 client_credentials is
useful for API calls but the resulting token may not work with `bws` CLI
if the organization also requires a decryption key.

## Python Implementation
```python
import urllib.request, urllib.parse

data = urllib.parse.urlencode({
    'client_id': cid,
    'client_secret': cs,
    'scope': 'api',
    'grant_type': 'client_credentials',
    'deviceType': 8,
    'deviceIdentifier': str(uuid.uuid4()),
    'deviceName': 'bws',
}).encode()

req = urllib.request.Request(
    'https://identity.bitwarden.com/connect/token',
    data=data,
    headers={
        'Content-Type': 'application/x-www-form-urlencoded',
        'Bitwarden-Client-Version': '2025.1.0',
    },
)
with urllib.request.urlopen(req, timeout=15) as resp:
    token = json.loads(resp.read().decode())['access_token']
```
