# Article Rotation & Duplicate Prevention

## The "Last Modified" Antipattern

**Problem:** Cron job prompts that say "find the most recently modified file in ~/wiki/apa-articles/" will repeatedly select the same article. Every time a new article gets added or an existing file gets touched, the "most recent" changes — but the cron job keeps picking whatever file happens to be latest, not what's unused.

**Root cause:** No tracking of which articles have already been turned into posts. The prompt lacks a cross-reference step against the published/pending archive.

## Prevention Strategy

### Source: linkedin_posts.json
Path: `~/.hermes/data/linkedin_posts.json`

Structure:
```json
{
  "posted": [
    {"date": "...", "title": "...", "source_url": "...", "hash": "md5..."},
    ...
  ]
}
```

Each entry has a `source_url` that maps back to the APA article. Before selecting an article, read this file and skip any article whose URL or title hash already appears.

### Source: linkedin_posts_archive.json
Path: `~/.hermes/data/linkedin_posts_archive.json`

Full-text archive with status field. Also check `status == "pending_approval"` entries — articles waiting for approval count as "used" and should be skipped too.

### Cron Prompt Pattern (Correct)
```markdown
KAYNAK: ~/wiki/apa-articles/ klasöründen rastgele bir makale seç, ancak linkedin_posts.json ve
linkedin_posts_archive.json'da kaydı OLAN (posted veya pending_approval) makaleleri ATLA.
Daha önce kullanılmamış bir makale bulamazsan en son eklenen ama kullanılmamış olanı seç.
```

### Cron Prompt Pattern (Wrong — DO NOT USE)
```markdown
KAYNAK: ~/wiki/apa-articles/ klasöründeki en son düzenlenen dosyayı bul.  ← KISIR DÖNGÜ
```

## Debugging Checklist

When investigating duplicate post issues:

1. Read cron job prompts from golden/jobs.json:
   ```
   python3 -c "import json; data=json.load(open('~/.hermes/golden/jobs.json')); jobs=data['jobs']; [print(j['name'], j['prompt'][:300]) for j in jobs if 'linkedin' in j.get('name','').lower()]"
   ```

2. Check linkedin_posts_archive.json for duplicate entries (same text appearing multiple times):
   ```
   python3 -c "import json; data=json.load(open('~/.hermes/data/linkedin_posts_archive.json')); texts=[p.get('text','') for p in data]; dupes=[t for t in texts if texts.count(t)>1]; print(f'{len(dupes)} duplicate text entries')"
   ```

3. List APA wiki articles by modification time:
   ```
   ls -lt ~/wiki/apa-articles/*.md | head -10
   ```

4. Cross-reference apa-articles against linkedin_posts.json to find unused articles.
