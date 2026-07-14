# Build Explanation Into the Workflow — Source Reference

**Source:** AI Automation Society (Skool) discussion thread, 12 July 2026
**Contributors:** Jason Elam, Paul McDonald, Chetan Mishra

Integrated into supervisor-pattern v2.0 as the Provenance Layer.

---

## Framework Principles

### 1. The Trust Problem

> "Automation becomes easier to trust when the system exposes the inputs, assumptions, sources, limits, and trade-offs behind the recommendation."

### 2. The "Correct-Looking Trap" (Silent Failure)

> "A correct-looking answer does not prove that the intended process occurred... that's exactly how silent failures slip through, the output looks right so nobody questions how it got there until something eventually breaks downstream."
> — Chetan Mishra

### 3. Provenance as a First-Class Output

> "Most automations treat the answer as the deliverable and skip logging the provenance entirely, which is exactly what makes debugging painful later."
> — Jason Elam

### 4. The Systemic Solution

> "Traceable explanation works best when it is not treated as a comment box after the automation runs. I like making it a first-class output of the workflow: evidence used, source path, decision assumption, confidence limit, and the exact point where a human can override it."
> — Jason Elam

---

## Vanitas Integration (supervisor-pattern v2.0)

### What Was Added

| Principle | Implementation in Provenance Layer |
|-----------|-----------------------------------|
| Evidence used | `data_sources` array per subtask |
| Source path | `execution_method` (db_query, web_search, model_inference, etc.) |
| Decision assumptions | `decision_assumptions` array |
| Confidence limits | `confidence.per_field` with Anti-Hallucination Protocol tags |
| Override points | `override_points` array + explicit human review gates |
| Correct-looking trap | Silent failure detection patterns (stale data, hallucinated source, circular reasoning) |

### Related Skills

- `skill_view(name="supervisor-pattern")` — The Provenance Layer in full
- `skill_view(name="anti-hallucination")` — Confidence tag alignment
