---
name: bulgu-degerlendirme
description: "Rigorous evaluation pipeline for cron-discovered items (Skool, GitHub, YouTube, RSS, etc.). Before assigning any label (Adaptable / Try / Watch / Skip), the evaluator MUST research Vanitas's relevant subsystems for conflict, overlap, necessity, and integration cost. English-only for rules and procedures."
version: 2.1.0
metadata:
  hermes:
    tags: [evaluation, triage, decision, rubric, research, conflict-analysis]
    category: research
---

# Finding Evaluation Pipeline

> **Core rule:** Labels are the OUTPUT of evaluation, not the evaluation itself.
> First research, then decide, then label.

## Workflow (4 Phases)

### Phase 1 — Discovery Analysis

Before touching the system, understand the finding itself:

1. **What is it exactly?** (tool, framework, technique, article, SaaS, pattern)
2. **What problem does it claim to solve?** (extract from source)
3. **Who made it?** (individual, company, open-source community)
4. **Is it actively maintained?** (last update, commit activity)
5. **Cost model:** (free, open-source, freemium, paid, trial-limited)

Research methods allowed:
- `web_extract` on the source URL
- `web_search` for reviews, alternatives, GitHub stars
- Reading comments/discussion on the original post

### 🔄 Batch Mode (5+ findings)

When evaluating 5+ findings in one session (common in Skool/GitHub cron runs), **do NOT run full Phase 2 per finding** — it wastes tool-call budget. Instead:

1. **Pre-triage by Phase 1 only:** Assign a preliminary Phase 4 label (Watch/Skip) based solely on Phase 1 discovery. If a finding is clearly off-topic, SaaS-only, or community chat, pre-label it Skip and skip Phase 2 entirely.
2. **Batch Phase 2 research ONCE per category:** Run one session_search, one wiki search, one skills audit per thematic group (e.g., all "agent orchestration" posts share one research pass), not per individual finding.
3. **Deep Phase 2 only for 🟢 ADAPTABLE / 🔵 TRY candidates:** Full per-finding research (2a–2e) is reserved for findings that survive pre-triage into the top two labels.
4. **Track budget per BATCH, not per finding:** The ~20 tool call budget applies to the entire evaluation batch. If batch budget is exhausted before all findings are evaluated, remaining unlabeled findings default to 🟡 WATCH — don't fabricate labels beyond budget.

This prevents 20+ findings × 5 research steps = 100+ tool calls. Findings correctly caught by pre-triage (challenge posts, SaaS promos, off-topic discussions) consume near-zero Phase 2 budget.

### Phase 2 — System Research (MANDATORY)

This is the critical phase. Before any decision, research Vanitas's system:

#### 2a. Session Search — Has this been discussed before?

```
session_search(query="<finding name/keyword>", limit=3)
session_search(query="<related concept>", limit=3)
```

Check:
- Was this exact finding already evaluated?
- Was a similar concept discussed and rejected?
- Is there context from a previous conversation that affects this decision?

#### 2b. Wiki Search — Is this already documented?

Use wiki search or `llm-wiki` skill to check:
```
wiki_fts query="<finding name>"
```

Check:
- Does a wiki page already cover this?
- Is there an existing analysis or rejection reason documented?

#### 2c. Skills Audit — Does a skill already cover this?

Search skills for the finding's domain:
```
skill_view(name="<relevant-skill>")
skills_list(category="<domain>")
```

Check:
- Does an existing skill provide this functionality?
- Would adding this create overlap or conflict with a skill?
- Is this a refinement of an existing skill rather than something new?

#### 2d. Cron Job Audit — Is a cron job already doing this?

If the finding relates to automation/monitoring:
```
cronjob(action='list')
```

Check:
- Does a cron job already cover this function?
- Would adding this duplicate an existing cron schedule?

#### 2e. Memory Check — Is this in persistent memory?

```
memory list (implied from context)
```

Check:
- Was this explicitly rejected or deferred before?
- Is there a known reason not to do this?

### Phase 3 — Conflict & Compatibility Analysis

After system research, evaluate each dimension:

#### Dimension 1: Necessity

| Score | Meaning | Evidence |
|-------|---------|----------|
| **Critical** | Solves an active problem or fills a documented gap | From session_search or Edel's direct request |
| **Valuable** | Meaningful improvement, not urgent | Clear benefit, no hard deadline |
| **Nice-to-have** | Minor quality-of-life improvement | Little cost, little benefit |
| **Unnecessary** | Already solved, or solves nothing | Existing solution found, or no real problem |

#### Dimension 2: Integration Risk

| Score | Meaning | Examples |
|-------|---------|----------|
| **None** | Standalone, no system changes needed | New skill, new wiki page, config addition |
| **Low** | Adds to existing system without modifying it | New cron job, new script, new reference file |
| **Medium** | Modifies an existing component | Skill patch, workflow change, script update |
| **High** | Changes a core or shared component | Config.yaml, gateway, core Hermes behavior, authentication flow |

#### Dimension 3: Cost (Selenium Fairness)

Calculate actual costs:

```
Setup cost:    <estimated hours>
Per-operation: <API calls, tokens, disk, time>
Maintenance:   <update frequency, accuracy monitoring, fix-on-break>
Total:         setup + (per-op × frequency) + maintenance/mo
```

Pass if: **total monthly cost < monthly value delivered**
Fail if: setup > 2 hours AND per-op cost > 0 (prefer zero-operational-cost solutions)

#### Dimension 4: Conflict Detection

Research each potential conflict:

- **Skill conflict:** Would this finding overlap with an existing skill? Would loading both cause ambiguity?
- **Cron conflict:** Would this compete for time/resources with an existing cron job?
- **Memory conflict:** Would this contradict an established fact or preference?
- **Workflow conflict:** Would this change an existing workflow that Edel relies on?
- **Cosmic conflict:** Would this break when another component updates (version coupling)?

Document ALL potential conflicts found. Use `session_search` to verify each concern.

### Phase 4 — Decision & Label

Only after completing Phases 1-3, assign ONE label:

---

## Labels

### 🟢 ADAPTABLE
**Meaning:** Integrate directly. Low risk, clear value, no conflicts.
**Requirements:**
- Necessity: Critical or Valuable
- Risk: None or Low
- Cost: Passes Selenium Fairness
- Conflicts: NONE found
**Output:** Write an actionable recommendation with exact integration steps.

### 🔵 TRY (PoC)
**Meaning:** Worth testing, rollback is easy, outcome uncertain.
**Requirements:**
- Necessity: Valuable or Nice-to-have
- Risk: None or Low (must be easily revertible)
- Cost: Setup < 1 hour, zero per-op cost preferred
- Conflicts: None found OR conflicts are minor and trivially resolved
**Output:** Propose a concrete test (max 30 min scope). If test passes → promote to ADAPTABLE. If fails → demote to WATCH or SKIP silently.

### 🟡 WATCH
**Meaning:** Potential exists, but not now. Collect information, re-evaluate later.
**Requirements:**
- Any of: Medium/High risk, High cost, Unnecessary today, Insufficient information
- Or: The field is evolving rapidly (wait 1 month for maturity)
**Output:** Document what would need to change for this to become ADAPTABLE (e.g., "when X happens, re-evaluate"). Set a re-evaluation trigger if possible.

### ⚪ SKIP
**Meaning:** Not worth our time. Reject with documented reason.
**Requirements:**
- Any of: Already exists, paid with no free alternative, conflicts irreconcilably, solves nothing, deprecated, scam/low-quality
**Output:** State the single strongest reason. Do NOT elaborate unless Edel asks.

---

## Evaluation Report Format (cron output)

### Phase 4 output — one line per finding:

```
• **[Title]** (Author) — **adaptable/try/watch/skip** — [one-line reason with system evidence]
```

### Full analysis (only for ADAPTABLE):

```
### 🎯 Adaptable Analysis

**1️⃣ [Title] — Priority: HIGH / MEDIUM**
- **What:** one line
- **Why:** gap filled, with session_search/wiki evidence
- **How:** technical approach
- **Conflicts found:** none — skill audit + session_search verified
- **Selenium Fairness:** Setup: Xh, Per-op: $0 (metadata tagging), Passes ✅
```

### Full analysis (for TRY):

```
### 🔵 Try: [Title]

**Proposed test:** [concrete 30-min test]
**Success criteria:** [what must happen to promote to ADAPTABLE]
**Revert plan:** [undo steps, guaranteed]
```

---

## Sample Decision Chains

### Example 1: "Loop Designer Skill" from today

```
Phase 1: AI Automation Society post by Alon Adelson. Auto-detects Anthropic's 4 loop types.
Phase 2: 
  2a. session_search → Loop Designer was found in today's cron, not evaluated yet
  2b. wiki → no wiki page
  2c. skills → supervisor-pattern skill exists (loop structure manual), no loop detection
  2d. cron → no relevant cron
  2e. memory → no prior rejection
Phase 3:
  Necessity: Nice-to-have (supervisor already handles loops manually)
  Risk: Medium (would patch supervisor-pattern skill or add new skill)
  Cost: Setup ~1h + ongoing accuracy monitoring
  Conflicts: Would partially overlap with supervisor-pattern's manual loop selection
Decision: TRY — test loop detection as standalone classifier, if >80% accurate → promote
```

### Example 2: "Local Whisper App" from today

```
Phase 1: macOS menubar local STT by Alon Adelson. Apple Silicon only.
Phase 2:
  2a. session_search → voice agent pipeline uses cloud Deepgram, local STT was discussed
  2b. wiki → no wiki page for local STT options
  2c. skills → vanitas-voice-agent uses cloud STT (Deepgram)
  2d. cron → no relevant cron
  2e. memory → no prior rejection
Phase 3:
  Necessity: Nice-to-have (cloud Deepgram works, privacy bonus but not a need)
  Risk: None (macOS app, standalone, doesn't affect server)
  Cost: $0 (open-source), but we don't use macOS as primary
  Conflicts: None — completely external to our system
Decision: SKIP — macOS-only, Apple Silicon exclusive. Our stack is Linux/WSL. If we eventually run on Mac, re-evaluate.
```

---

## Pitfalls

- **Do NOT skip Phase 2.** "I already know what this is" is the most common mistake. The system may have changed since you last researched it.
- **Do NOT assign ADAPTABLE without checking session_search.** If Edel rejected a similar idea before, you'll waste time re-proposing it.
- **Do NOT assign SKIP without a specific reason.** "Doesn't fit" is not a reason. "Paid $20/mo with free alternative in skill X" is a reason.
- **Do NOT write evaluation reports in Turkish.** Rules and procedures are English. Only the final delivery to Edel may be in Turkish if she prefers.
- **Do NOT over-research.** Phase 2 has hard limits:
  - 30 seconds max for session_search
  - 3 skills max for skill audit
  - If wiki search returns nothing in 2 queries, stop looking
  - If cron audit is not relevant, skip it entirely
  Total Phase 2 budget: **~60 seconds real time** or **~20 tool calls**, whichever comes first.
- **Do NOT fabricate evidence.** If session_search returns nothing, say "no prior discussion found." If wiki has no entry, say "not documented." Don't infer.
- **ADAPTABLE is the exception, not the default.** Most findings should land on TRY, WATCH, or SKIP.
- **🔵 TRY has a budget.** If a PoC takes more than 30 minutes, it should have been WATCH instead. Kill failing experiments early.
