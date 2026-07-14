# News Sources Catalog

> Durable reference of all known news sources for bundle gündem processing.
> Characteristics, URL patterns, content profiles, and quirks.
> Maintain this file when new sources are discovered or source behavior changes.

## Primary Sources (Highest Value)

### ScienceDaily
- **URL**: `https://www.sciencedaily.com/`
- **Content Profile**: University press releases, journal paper summaries, Nature/Science/PNAS coverage
- **Strengths**: Clean markdown via web_extract, clear date stamps, broad science coverage (biology, physics, health, environment, space)
- **Weaknesses**: 1-3 day delay vs breaking news; articles are 2-3 sentence previews on front page (full text on individual article pages)
- **URL Pattern**: Release IDs like `releases/2026/06/260625014830.htm`
- **Frequency**: ~10-15 new articles per day, most on weekdays
- **Verification**: Each article has clear "Date: June 26, 2026" line
- **Best for**: Morning run (06:15); rarely has fresh content by 10:15 or 16:15

### BBC News
- **URL**: `https://www.bbc.com/news`
- **Content Profile**: Breaking news, world events, politics, science, technology, business
- **Strengths**: Real-time timestamps ("21 mins ago"), broadest coverage, reliable
- **Weaknesses**: Article URLs may 404 for hours after appearing on homepage (propagation delay); survey script triggers ERR_BLOCKED_BY_CLIENT (non-fatal)
- **Extraction**: web_extract works — includes summaries from homepage listings even when article URLs 404
- **BBC Sub-sections**: `/news/technology` (features-heavy, not breaking), `/news/business` (sometimes blocks more aggressively), `/news/science_and_environment`
- **Key Pattern**: Same story often appears on BBC News main + Business + Technology with slightly different headlines → intra-bundle dedup needed
- **Pitfall**: Tech sub-page often returns <1K chars → skip and use main page

### Build Fast with AI
- **URL**: `https://www.buildfastwithai.com/blogs/ai-news-today-...`
- **Content Profile**: Comprehensive AI news roundups — 10-15 stories with analysis, context, and developer guidance
- **Strengths**: Deep analysis, Polymarket odds references, insider context on delays/strategy shifts, developer-angle insights
- **Weaknesses**: Only covers AI (not general science/tech), published ~3x/week
- **URL Pattern**: `/blogs/ai-news-today-june-27-2026` (slug-based, date in URL)
- **Best for**: AI-specific depth on the latest model releases, corporate moves, regulation
- **Example value**: GPT-5.6 delay with Polymarket odds and Goblin Incident context; Alphabet $269B loss with detailed talent exit chronology

### Universe Today
- **URL**: `https://www.universetoday.com/`
- **Content Profile**: Space and astronomy news — exoplanets, telescopes, solar system, cosmology
- **Strengths**: 3-5 articles per day, excellent detail, clear dates, clean markdown via web_extract
- **Weaknesses**: Only space/astronomy (no general science)
- **Topics Covered**: NASA missions, JWST discoveries, exoplanet research, solar activity, astronomy history
- **Best for**: Secondary check when science news is thin — always has fresh content

## Secondary Sources (Supplemental)

### Science.org (AAAS) — NEW 2026-06-30
- **URL**: `https://www.science.org/news/latest-news`
- **Content Profile**: Science magazine news — journalist-written articles covering research, policy, and scientific community
- **Strengths**: High-quality journalism from AAAS (publishers of Science journal), clear dates with author names, covers broad topics (biodiversity, computing, research integrity, cosmology, biology/medicine, paleontology, virology, AI policy)
- **Weaknesses**: Articles may have paywall for full text (summaries are free and sufficient for news bundles); web_extract truncates at ~5K chars so only top 10-15 headlines visible
- **URL Pattern**: `https://www.science.org/content/article/[slug]`
- **Best for**: Science policy stories, research integrity news, and topics not covered by ScienceDaily's press-release pipeline (e.g., insect species estimates, Neanderthal genetics, Arctic research expeditions)
- **Dedup note**: Overlaps with ScienceDaily when both cover the same Nature/Science paper — Science.org has the journal's own perspective, ScienceDaily has the university press release version. Keep Science.org for policy/community angle, ScienceDaily for research findings.

### Medium — AI News Weekly (David Akpovi)
- **URL Pattern**: `https://medium.com/@davidakpovi/ai-news-week-of-june-22-to-june-28-2026-...`
- **Content Profile**: Weekly AI roundup — cybersecurity, chips, tools, costs
- **Strengths**: Weekly synthesis with explicit takeaways; easy to extract via web_extract (no paywall)
- **Weaknesses**: Not daily (weekly only); Medium paywall may block some articles
- **Best for**: AI-specific weekly roundups (run on Monday/Tuesday)
- **Topics**: AI security incidents, hardware, startup costs, design tools, agent systems

### DonanımHaber — Popüler Bilim
- **URL**: `https://www.donanimhaber.com/populer-bilim`
- **Content Profile**: Turkish tech/science news — localizes global developments, covers Turkish R&D
- **Strengths**: Turkish language, unique stories not found on BBC/ScienceDaily (ASELSAN, Turkish R&D), human-interest science
- **Weaknesses**: Aggregated format (some stories are translations of international news), paginated (937 pages)
- **Best for**: Turkish reader-specific news, local inventions, unique science stories
- **Unique Stories Found**: ASELSAN LIFELINE HLM heart-lung machine, lab-grown embryo models, fusion energy developments, baldness treatment

### Pew Research Center
- **URL Pattern**: `https://www.pewresearch.org/.../YYYY/MM/DD/title/`
- **Content Profile**: In-depth survey-based reports on technology adoption, social trends
- **Strengths**: Authoritative statistics, detailed methodology, clean markdown
- **Weaknesses**: Reports are episodic (not daily), long-form (web_extract may truncate)
- **Best for**: Statistical data points for tech/society stories

### EarthSky
- **URL**: `https://earthsky.org/`
- **Content Profile**: Space weather, astronomy, skywatching
- **Strengths**: Real-time CME/solar storm alerts, daily sky updates, clear dates
- **Weaknesses**: Narrow focus (mostly solar system astronomy)
- **Best for**: CME alerts, aurora forecasts, planetary alignments

### Science News
- **URL**: `https://www.sciencenews.org/`
- **Content Profile**: In-depth science journalism — neuroscience, AI, paleontology, health
- **Strengths**: Journalist-written (not press releases), feature-length articles with analysis, clear dates
- **Weaknesses**: Limited free articles per month (paywall for full archive)
- **Best for**: Feature-quality science stories, trending science topics

### TechCrunch
- **URL**: `https://techcrunch.com/`
- **Content Profile**: Startup and technology news
- **Strengths**: Startup ecosystem, AI company moves, funding rounds, AI model launches
- **Weaknesses**: web_extract output includes Cloudflare Turnstile + reCAPTCHA verification boilerplate text ("Checking your Browser…", "Verification failed/expired") — this is NON-FATAL, article content still comes through. Some JS rendering issues.
- **Best for**: AI company news, startup funding, tech policy, AI model announcements
- **Pitfall**: Do NOT abandon TechCrunch when you see Cloudflare verification text in web_extract output — the headlines and article content are still there. Only treat as failed if < 2K chars of real article text (excluding verification boilerplate). Added 2026-06-30.

### Wikipedia Current Events
- **URL Pattern**: `https://en.wikipedia.org/wiki/Portal:Current_events/YYYY_MMMM_DD`
- **Content Profile**: Human-curated list of major events for a specific date
- **Strengths**: Gold standard for date verification, human-curated, no hallucination risk
- **Weaknesses**: Not a news source (headlines only with brief summaries), may lag by 12-24 hours
- **Best for**: Date verification anchor — "do the stories I found actually belong to today?"

### Nature.com News — NEW 2026-07-02
- **URL**: `https://www.nature.com/news`
- **Content Profile**: Science journalism from Nature — news features, Q&As, explainers, policy analysis
- **Strengths**: High-quality meta-science stories (trust in science, peer review reform, paper mills, funding policy), clear dates with article type labels (news, news feature, news q&a, world view), covers topics no other source does (academic community dynamics, research integrity, political dimensions of science)
- **Weaknesses**: Not a primary research news source (more meta-analysis of science as an enterprise); some articles behind paywall (summaries are free and sufficient)
- **URL Pattern**: `https://www.nature.com/articles/d41586-026-NNNNNN-N`
- **Best for**: Science-society interface stories, research community news, science policy analysis
- **Example value (July 2)**: "Paper mill cancer studies get double citations" (research integrity), "Have people stopped trusting science?" (meta-analysis of trust data), "Paying peer reviewers works" (85% faster decisions)
- **Dedup note**: Minimal overlap with ScienceDaily/SciTechDaily — Nature covers the meta-story, not the research finding itself

### Reuters AI Hub — NEW 2026-07-02
- **URL**: `https://www.reuters.com/technology/artificial-intelligence/`
- **Content Profile**: AI industry news — corporate moves, regulatory developments, market analysis, government policy
- **Strengths**: Timely AI-specific headlines with clear dates, market/financial angle on AI stories, covers regulatory and geopolitical dimensions (US-China AI competition, EU AI policy), exclusive reports and analyses
- **Weaknesses**: Only AI (not general science/tech); some content is analysis/opinion rather than breaking news
- **URL Pattern**: `https://www.reuters.com/technology/artificial-intelligence/` (hub page) → individual articles at `reuters.com/world|business|technology/...`
- **Best for**: AI corporate/government news — funding rounds, regulatory actions, corporate strategy, international AI competition
- **Example value (July 2)**: "Chinese inexpensive AI model catching up with OpenAI/Anthropic" (competition analysis), "OpenAI proposes handing Trump administration 5% stake" (corporate-government), "Together AI raises $800M at $8.3B" (funding), "UN panel warns unchecked AI may pose catastrophic risks" (regulatory)
- **Dedup note**: Overlaps with TechCrunch on funding/startup news. Reuters has the financial/regulatory angle; TechCrunch has the startup/product angle. Keep Reuters for market/policy context, TechCrunch for product/startup detail.

## Source Selection Strategy

```
Morning Run (06:15):    ScienceDaily + BBC News + Build Fast with AI + Universe Today
Midday Run (10:15):     BBC News only + DonanımHaber + EarthSky
Evening Run (16:15):    BBC News + TechCrunch + Medium AI Weekly (if Monday)
```

**Rationale:**
- ScienceDaily content is typically 1-3 days delayed → morning check is sufficient
- BBC News has real-time timestamps → check every run for breaking stories
- Build Fast with AI publishes ~3x/week → check on morning runs
- Universe Today has fresh daily content → morning check sufficient
- DonanımHaber has steady Turkish content → midday for variety
- EarthSky has space weather → midday for CME/aurora updates
- Medium is weekly → Monday morning check
- TechCrunch has startup news → evening for daily roundup
- Science.org (AAAS) → check when ScienceDaily is thin or for science policy/community stories not in the press-release pipeline
- Nature.com/news → check for science journalism + meta-stories (trust in science, peer review, paper mills)
- Reuters AI hub → check for AI industry/market news, regulatory developments, corporate moves

## Content Categorization Map

| Source | Best For | Category | Reliability |
|--------|----------|----------|-------------|
| ScienceDaily | Research breakthroughs | science | High |
| BBC News | Breaking news, world events | world, tech, economy | High |
| Build Fast with AI | AI depth, strategy, market | tech | High |
| Universe Today | Space/astronomy | science | High |
| Science.org (AAAS) | Science policy, research community | science | High |
| Medium AI Weekly | AI ecosystem | tech | Medium |
| DonanımHaber | Turkish tech/science | tech, science | Medium |
| Pew Research | Statistics/adoption data | tech, economy | High |
| EarthSky | Solar/space weather | science | High |
| Science News | Feature science stories | science | Medium |
| TechCrunch | Startup/AI company news | tech | Medium |
| Nature.com News | Science meta-stories, policy, community | science | High |
| Reuters AI Hub | AI industry, regulation, market | tech, economy | High |
| Wikipedia Current Events | Date verification | — | High |

## Deduplication Notes

When using multiple sources in one run, watch for these known overlap patterns:

- **ScienceDaily ↔ SciTechDaily**: Often cover the same university press releases on the same day with different headlines. Keep the more detailed version.
- **ScienceDaily ↔ Science.org (AAAS)**: Both may cover the same Nature/Science paper. ScienceDaily has the university press release angle; Science.org has the journal's own perspective. Keep both angles if space allows, otherwise keep Science.org for policy/community context.
- **BBC News ↔ BBC Business**: Same breaking story appears on both. BBC Business version usually has market/financial context.
- **TechCrunch ↔ Build Fast with AI**: Same AI company news may appear on both. Build Fast with AI has deeper analysis; TechCrunch is timelier.
- **DonanımHaber ↔ International sources**: DonanımHaber sometimes translates BBC/ScienceDaily stories. Check proper nouns to identify originals.
- **Reuters AI ↔ TechCrunch**: Same AI funding/corporate news may appear on both. Reuters has financial/regulatory angle; TechCrunch has startup/product angle. Keep both if space allows, otherwise prefer Reuters for market context and TechCrunch for product detail.
- **Nature.com News ↔ ScienceDaily**: Minimal overlap — Nature covers the meta-story (research integrity, science policy, community dynamics) while ScienceDaily covers the research finding itself. Both can coexist in a bundle.
