# LinkedIn API Capabilities & Limitations

## Current Token Scopes
- `openid profile email w_member_social`
- **Can do**: Post share (text + image via registerUpload → shareMediaCategory: IMAGE), delete posts
- **Cannot do**: Profile read (GET /v2/me → 403), profile edit (About/summary), people search

## Profile Editing
- About section (= summary field) requires `r_liteprofile` + `w_liteprofile` or `r_basicprofile` scopes
- Endpoint: `PUT https://api.linkedin.com/v2/people/(id:{person_id})`
- Current token does NOT have these scopes — needs re-auth with expanded scope
- Person URN: `urn:li:person:hy0rYB54uc`

## Token Location
- `~/.hermes/secrets/linkedin_token.json` (600 permissions)
- Token refresh: OAuth2 re-auth flow required when scope changes

## Workaround for Profile Updates
- When API can't access profile, ask Edel to provide current text
- Combine old + new text manually, return for copy-paste
- DON'T chain multiple API calls trying to find a working endpoint — just ask
