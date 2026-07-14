# Media Watch Handling in Cron Mode

> Added: 2026-07-13
> Context: Cron run found Media Watch email but correctly determined it's a news clippings roundup, not original APA content needing wiki processing.

## What Is Media Watch?

APA Media Watch is a **weekly news clippings roundup** sent by APA Public Affairs. It samples news coverage of APA, its publications, and psychology in major media outlets. It typically contains:

- **APA in the News:** External news articles where APA members/leaders are quoted or APA research is cited
- **APA Journals in the News:** News coverage citing APA journal research
- **APA Members in the News:** APA members' appearances/expertise in media
- **APA Podcast or Event mentions:** House ads for APA's own content

## Key Distinction

| Content type | Original APA? | Process? |
|---|---|---|
| External news citing APA | ❌ (third-party) | Note in report, no wiki |
| APA podcast episode mention | ✅ (APA-produced) | Route to Speaking of Psychology channel |
| APA Labs / official program mention | ✅ (APA-produced) | Route to Monitor/Events channel |
| APA member quoted in news | ❌ (third-party) | Note in report if notable |

## Cron Mode Rule

- **Do NOT** create wiki files for Media Watch items
- **Do NOT** add to NotebookLM
- **DO** scan Media Watch for:
  1. APA-produced content announcements (podcast, event, new initiative) → route to appropriate channel
  2. Notable 1-2 themes → mention briefly in report as "📰 APA Medyada" section (1-2 cümle)
- Skip routine news clippings. Only flag items where:
  - The coverage is exceptional (front-page, national conversation)
  - The coverage reveals a trend (e.g., AI chatbots appearing across 5+ news outlets)
  - APA leadership issued a statement on a major topic

## Rationale

Processing every Media Watch clipping as a wiki entry would:
- Create dozens of low-value files per week
- Duplicate content already in the original news source
- Dilute the wiki's signal-to-noise ratio for APA research

The Media Watch exists for PR tracking, not knowledge building. Keep it in its lane.
