# No-Agent Script SQLite Timeout Debug — Gerçek Vaka

## Vaka: "Vanitas 8-Boyutlu Rüya" cron job timeout (120s)

**Script:** `~/.hermes/scripts/vanitas_dream.py` (no_agent=true)
**Hata:** "Script timed out after 120s" — çıktı yok, exit code yok.

## Debug Akışı

### 1. Elle çalıştır — timeout'u doğrula
```bash
timeout 10 python3 scripts/vanitas_dream.py 2>&1
echo "EXIT: $?"
```
→ EXIT: 124 (timeout). 10 saniyede bile bitmedi.

### 2. En yavaş fonksiyonu bul
```bash
timeout 30 python3 -c "
import os, sys, time
sys.path.insert(0, os.path.expanduser('~/.hermes/scripts'))
from vanitas_dream import *
t0 = time.time()
result = analyze_skills()
print(f'skill: {time.time()-t0:.2f}s')
t0 = time.time()
result = workflow_patterns()
print(f'pattern: {time.time()-t0:.2f}s')
"
```
→ **analyze_skills: 24s**, **workflow_patterns: 17s+** (timeout)

### 3. Yavaş SQL sorgularını tespit et
Tools names sorgusu (analyze_skills içinde):
```sql
SELECT DISTINCT m.tool_name FROM messages m
WHERE m.tool_name IS NOT NULL AND m.tool_name != ''
AND m.timestamp > datetime('now', '-7 days', 'unixepoch')
```
→ 20.97 saniye — hiç sonuç dönmedi ama full table scan yaptı!

Workflow pattern sorgusu:
```sql
SELECT content, COUNT(*) as cnt FROM messages
WHERE role='user' AND timestamp > datetime('now', '-7 days')
AND length(content) > 10
GROUP BY content HAVING cnt > 1 ORDER BY cnt DESC LIMIT 5
```
→ ~17 saniye — `GROUP BY content` full scan + sort

### 4. Kök neden: Index yok
```sql
-- messages tablosunda sadece 3 index vardı:
idx_messages_session, idx_messages_platform_msg_id, idx_messages_session_active
-- role, timestamp, tool_name kolonlarında HİÇ index YOK
```

Index ekle:
```sql
CREATE INDEX idx_messages_role_ts ON messages(role, timestamp);
CREATE INDEX idx_messages_toolname ON messages(tool_name);
CREATE INDEX idx_sessions_started ON sessions(started_at);
```
→ Her index 24-25 saniye sürdü (büyük tablo), ama eklendikten sonra sorgular <1s'ye indi.

### 5. Skills taraması yavaşlığı
Orijinal:
```python
skill_files = list(Path(skills_dir).rglob("SKILL.md"))  # WSL'de çok yavaş
```
→ 43 skill dizini olmasına rağmen `rglob` recursive tarama yapıp `.curator_backups` gibi gizli dizinlere de girdiği için timeout.

Düzeltme:
```python
all_skill_names = sorted([
    d.name for d in Path(skills_dir).iterdir()
    if d.is_dir() and not d.name.startswith(".") and (d / "SKILL.md").exists()
])
```

### 6. Eksik binary: ss komutu
Container'da `ss` yok. `shutil.which('ss')` ile kontrol et, yoksa `/proc/net/tcp` fallback kullan.

### 7. SIGALRM timeout wrapper
```python
def safe_db_query(query, params=(), timeout=10):
    conn = sqlite3.connect(STATE_DB)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA query_only=1")
    result = []
    signal.alarm(timeout)
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        result = cur.fetchall()
        signal.alarm(0)
    except:
        signal.alarm(0)
        return {"error": "timeout"}
    finally:
        conn.close()
    return result
```

### 8. Altın Kural: Zaman damgalarını Python'da hesapla
YANLIŞ:
```python
cur.execute("... WHERE ts > datetime('now', '-7 days')")
```
→ SQLite string karşılaştırması, index kullanamaz, full table scan.

DOĞRU:
```python
cutoff = (datetime.now() - timedelta(days=7)).timestamp()
cur.execute("... WHERE ts > ?", (cutoff,))
```
→ Index kullanabilir, milisaniyelerde çalışır.

## Dersler

1. **SQLite sorgusu yavaşsa → hemen index kontrol et.** `EXPLAIN QUERY PLAN` çalıştır.
2. **Zaman karşılaştırmalarını ASLA SQL `datetime()` ile yapma** — hep Python'da hesaplayıp parametre geç.
3. **`rglob` WSL/Docker'da çok yavaş** — `iterdir()` veya `os.scandir()` kullan.
4. **no_agent script'leri sessiz kalır** — timeout yediğinde hiç çıktı olmaz. Teker teker fonksiyon test et.
5. **`shutil.which('komut')`** ile binary varlığını kontrol et, yoksa fallback hazırla.
