# MEMORY_META.json TTL Audit

## When to audit

- **Doluluk alarmı:** MEMORY.md >85% veya USER.md >95%
- **Recurring correction:** User corrects stale/missing memory
- **Post-migration:** After model/provider/config change
- **Monthly hygiene:** Every ~30 days without alarms

## Workflow

### 1. Inventory

```bash
cat ~/.hermes/memories/MEMORY.md
cat ~/.hermes/memories/USER.md
python3 -c "import json,collections; m=json.load(open('/home/ubuntu/.hermes/memories/MEMORY_META.json')); c=collections.Counter(e['type'] for e in m['entries'].values()); print(f'Entries: {len(m[\"entries\"])}, {dict(c)}')"
```

### 2. Check expired entries

```python
import json, datetime
now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
meta = json.load(open('/home/ubuntu/.hermes/memories/MEMORY_META.json'))
print(f'Expired entries ({now.date()}):')
for eid, entry in meta['entries'].items():
    if 'expires_date' not in entry: continue
    exp = datetime.datetime.fromisoformat(entry['expires_date'].replace('Z','+00:00')).replace(tzinfo=None)
    if exp < now:
        print(f"  {eid[:8]}.. | {entry.get('type','?'):6s} | {entry.get('content_preview','')[:60]}")
```

### 3. Classify by content

TTL types for memory entries: short=7d (temporary config/errors), medium=60d (procedures/status/lessons), long=365d (infrastructure/rules/archive).

| Should be | If content_preview contains |
|-----------|---------------------------|
| long | Altyapı: "never killed", "keepalive", "bitwarden", "himalaya", "apa login", "nlm default profile" |
| long | Doğrulanmış teknik gerçek: "deepseek prompt caching verified" |
| long | "[ARSIV:" prefix (seminer/arşiv notları) |
| long | Kullanıcı tercihi: "tekrar eden", "okunmuş bilgileri" |
| long | Kullanıcı profili: "yatırım" + banka/hisse adı |
| medium | Prosedür: "workflow", "kural", "cron iso", "meet auth", "wrapper fix" |
| medium | Ders: "kritik ders", "chromium executable", "docker container" |
| medium | Proje durumu: "supervisor poc", "vanitas voice v", "linkedin post revize" |
| medium | "[CONFIRMED]" (yukarıdaki long keyword'lerinden biri DEĞİLSE) |
| medium | Yatırım planı: "dca plani", "bist dca" |
| short | "[ERROR]" prefix (hata logları) |
| short | Geçici API key, port, token |

### 4. Fix script

```python
import json, datetime
meta = json.load(open('/home/ubuntu/.hermes/memories/MEMORY_META.json'))
changes = 0

LONG_KW = ['never killed','keepalive chrome','keepalive + mcp','bitwarden cli',
           'bitwarden vault','himalaya imap','apa login','apa uyelik',
           'apa üyelik','nlm default profile','deepseek prompt caching verified']
MEDIUM_KW = ['workflow','kural','cron iso','no-agent cron','meet auth',
             'wrapper fix','chromium executable','api key arama',
             'heartbeat & skill','docker container','gmail_check',
             'gmail api token','mid-session','kritik ders','otomatik onarim',
             'supervisor poc','vanitas voice v','linkedin post revize',
             'kocaer','pozisyonu','oncelik sirasi','edel duzeltmesi',
             'kayit saglik','dca plani','bist dca']

for eid, entry in meta['entries'].items():
    if 'content_preview' not in entry:
        continue
    preview = entry.get('content_preview','')
    p_lower = preview.lower()
    cur_type = entry.get('type','')
    
    if any(kw in p_lower for kw in LONG_KW) or preview.startswith('[ARSIV:'):
        new_type, new_ttl = 'long', 365
    elif any(kw in p_lower for kw in MEDIUM_KW):
        new_type, new_ttl = 'medium', 60
    elif any(kw in p_lower for kw in ['tekrar eden','okunmus bilgileri','sistemik cozum']):
        new_type, new_ttl = 'long', 365
    elif 'yatirim' in p_lower and ('is bankasi' in p_lower or 'kocer' in p_lower):
        new_type, new_ttl = 'long', 365
    elif preview.startswith('[CONFIRMED]') and not any(kw in p_lower for kw in
            ['keepalive chrome never','bitwarden cli','himalaya imap']):
        new_type, new_ttl = 'medium', 60
    elif preview.startswith('[ERROR]'):
        new_type, new_ttl = 'short', 7
    else:
        new_type, new_ttl = 'medium', 60
    
    if cur_type != new_type or entry.get('ttl_days') != new_ttl:
        entry['type'] = new_type
        entry['ttl_days'] = new_ttl
        if 'added_ts' in entry:
            added = datetime.datetime.fromtimestamp(entry['added_ts'], tz=datetime.timezone.utc).replace(tzinfo=None)
            entry['expires_date'] = (added + datetime.timedelta(days=new_ttl)).isoformat()
        changes += 1

if changes:
    with open('/home/ubuntu/.hermes/memories/MEMORY_META.json','w') as f:
        json.dump(meta, f, indent=2)
    print(f'{changes} entries corrected.')
else:
    print('No changes needed.')
```

Verify:
```bash
grep '"type"' ~/.hermes/memories/MEMORY_META.json | sort | uniq -c
```

## 🚩 Turkish character pitfall

Python `in` is character-exact. Turkish letters WON'T match ASCII keyword variants:

| Wrong keyword | Actual text | Issue |
|--------------|-------------|-------|
| `'apa uyelik'` | `'apa üyelik'` | `ü` ≠ `u` |
| `'yatirim'` | `'yatırım'` | `ı` ≠ `i` |

**Fix:** Include BOTH ASCII and Turkish forms in keyword lists:
```python
'apa uyelik', 'apa üyelik'
```

Or normalize:
```python
def fold_tr(s):
    for a,b in [('ı','i'),('ğ','g'),('ü','u'),('ö','o'),('ş','s'),('ç','c')]:
        s = s.replace(a,b)
    return s
```

## Post-audit checklist

- [ ] Types corrected — distribution should have more medium+long than short
- [ ] MEMORY.md < 85% capacity
- [ ] USER.md < 95% capacity
- [ ] If USER.md > 95%, schedule separate compression session
- [ ] Cross-reference expired entries' content_preview against MEMORY.md + skills
