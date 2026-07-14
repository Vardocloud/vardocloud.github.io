# APA Newsletter Comprehensive Sweep Format

> **Use case:** Manual full sweep across ALL APA newsletter types (not single-article cron processing).
> **When:** Edel requests a comprehensive "all APA bültenleri" pull. Not for daily cron.
> **Origin:** 2026-06-14 APA Bilgi Pipeline v4.0 execution (7 newsletters + Monitor).

## When to Use This vs Cron Format

| Aspect | Cron Mode (daily) | Comprehensive Sweep (manual) |
|--------|-------------------|------------------------------|
| Source | Single newsletter/topic | ALL APA newsletters + Monitor |
| Format | 5 headers per article | Numbered sections per newsletter type |
| Depth | 250-350 words total | Per-article: method, findings, clinical significance |
| Emoji headers | 💡📖🔑🧩⭐ | ❶❷❸❹❺❻❼ + 📋📊🔍💡 |
| Speed target | Fast, cron-safe | Thorough, no time pressure |

## Newsletter Types to Sweep

| # | Newsletter | From | Frequency |
|---|-----------|------|-----------|
| 1 | Editor's Choice | apa@info.apa.org | Weekly (Thu) |
| 2 | Science Spotlight | apa@info.apa.org | Biweekly (Thu) |
| 3 | Practice Update | pracupdate@info.apa.org | Weekly (Fri) |
| 4 | Media Watch | public.affairs@apa.org | Weekly (Fri) |
| 5 | Advocacy / Washington Update | advocacy@info.apa.org | Weekly (Thu) |
| 6 | Six Things | apa@info.apa.org | Weekly (Mon) |
| 7 | CE Roundup (ATLA — skip) | apace@info.apa.org | Weekly (Wed) |
| 8 | Membership (ATLA — skip) | membership@info.apa.org | Varies |
| 9 | Monitor on Psychology | (web_extract) | Monthly |

**Fetch method:** `ALL_PROXY="" python3 ~/.hermes/skills/productivity/google-workspace/scripts/google_api.py gmail get <ID>` with individual email IDs.

## Per-Article Deep Analysis Template

When an article has full scientific detail (Editor's Choice, Science Spotlight):

```
a) [Makale Başlığı] — [Yazarlar, Dergi]

📋 Araştırma Sorusu: [What was tested?]
📊 Yöntem: [N participants, design, measures]
🔍 Bulgular: [Key numerical findings, effect sizes]
💡 Klinik Anlamı: [How Edel uses this in therapy]
```

For news/commentary (Media Watch, Six Things, Practice Update news items):

```
• **[Topic]** — [Key insight in 1-2 sentences]
💡 *[Clinical relevance]*
```

## Multi-Newsletter Report Structure

```
🧠 APA HAFTALIK BÜLTEN — [TARİH ARALIĞI]
────────────────────────────

❶ [BÜLTEN ADI] ([TARİH])
a) [article 1] — ...
b) [article 2] — ...

❷ [NEXT BÜLTEN] ([TARİH])
...

📌 ÖNE ÇIKAN: [1-2 critical items highlighted]
🧩 Öneri: [1-2 action items for Edel]
```

## Notes

- **All email body HTML** — strip formatting; the text-based content is enough for analysis.
- **DOIs are included** in Editor's Choice emails. Preserve them for future reference.
- **APA member quotes** in Media Watch are valuable for Edel's network awareness. Note names.
- **Action alerts** (grant rules, advocacy) deserve their own section with deadline emphasis.
- **Ücretsiz etkinlikler** go to wiki/apa-etkinlikler/. Her şey için ayrı dosya gerekmez — aynı tarih aralığındaki etkinlikler tek dosyada toplanabilir.
