# JS Syntax Debug: node --check

When inline JavaScript fails silently (no console errors, all functions undefined), use `node --check` to find syntax errors offline.

## Pattern
1. Save served JS to a temp file
2. Run `node --check /tmp/page.js`
3. Node reports exact line + error type
4. Fix, redeploy

## Why This Matters
Browser console often shows ZERO errors for script-level parse errors. `typeof start` returns `"undefined"` even though `function start()` appears in the source. The entire script is blocked by a single syntax error — usually a Turkish character inside a quoted string.

## Common Root Causes

| Symptom | Likely Cause |
|---------|--------------|
| All functions `undefined` | Script-level parse error blocks everything |
| `missing ) after argument list` | Unescaped apostrophe in string (`'işte'` → `'` breaks string) |
| `Unexpected token` | Missing `}` or bracket |

## Real Case (17 Jun 2026)
Vanitas Ses button did nothing. All JS functions were `undefined`. No console errors. Root cause: `'Başlat'a dokun'` — Turkish `'` broke the string. Fix: `'Başlat -a dokun'`.

## iOS Safari AudioContext Note
`getUserMedia` must happen BEFORE any `await` in click handler. `await` breaks the user gesture chain on iOS Safari.
