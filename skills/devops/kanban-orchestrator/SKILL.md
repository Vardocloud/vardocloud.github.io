---
name: kanban-orchestrator
description: Decomposition playbook + anti-temptation rules for an orchestrator profile routing work through Kanban. The "don't do the work yourself" rule and the basic lifecycle are auto-injected into every kanban worker's system prompt; this skill is the deeper playbook when you're specifically playing the orchestrator role.
version: 3.0.0
platforms: [linux, macos, windows]
environments: [kanban]
metadata:
  hermes:
    tags: [kanban, multi-agent, orchestration, routing]
    related_skills: [kanban-worker]
---

# Kanban Orchestrator — Decomposition Playbook

> The **core worker lifecycle** (including the `kanban_create` fan-out pattern and the "decompose, don't execute" rule) is auto-injected into every kanban process via the `KANBAN_GUIDANCE` system-prompt block. This skill is the deeper playbook when you're an orchestrator profile whose whole job is routing.

## Profiles are user-configured — not a fixed roster

Hermes setups vary widely. Some users run a single profile that does everything; some run a small fleet (`docker-worker`, `cron-worker`); some run a curated specialist team they've named themselves. There is **no default specialist roster** — the orchestrator skill does not know what profiles exist on this machine.

Before fanning out, you must ground the decomposition in the profiles that actually exist. The dispatcher silently fails to spawn unknown assignee names — it doesn't autocorrect, doesn't suggest, doesn't fall back. So a card assigned to `researcher` on a setup that only has `docker-worker` just sits in `ready` forever.

**Step 0: discover available profiles before planning.**

Use one of these:

- `hermes profile list` — prints the table of profiles configured on this machine. Run it through your terminal tool if you have one; otherwise ask the user.
- `kanban_list(assignee="<some-name>")` — sanity-check a single name. Returns an empty list (rather than an error) for an unknown assignee, so this only confirms a name you're already considering.
- **Just ask the user.** "What profiles do you have set up?" is a fine first turn when the goal needs more than one specialist.

Cache the result in your working memory for the rest of the conversation. Re-asking every turn wastes a tool call.

## When to use the board (vs. just doing the work)

Create Kanban tasks when any of these are true:

1. **Multiple specialists are needed.** Research + analysis + writing is three profiles.
2. **The work should survive a crash or restart.** Long-running, recurring, or important.
3. **The user might want to interject.** Human-in-the-loop at any step.
4. **Multiple subtasks can run in parallel.** Fan-out for speed.
5. **Review / iteration is expected.** A reviewer profile loops on drafter output.
6. **The audit trail matters.** Board rows persist in SQLite forever.

If *none* of those apply — it's a small one-shot reasoning task — use `delegate_task` instead or answer the user directly.

## The anti-temptation rules

Your job description says "route, don't execute." The rules that enforce that:

- **Do not execute the work yourself.** Your restricted toolset usually doesn't even include terminal/file/code/web for implementation. If you find yourself "just fixing this quickly" — stop and create a task for the right specialist.
- **For any concrete task, create a Kanban task and assign it.** Every single time.
- **Split multi-lane requests before creating cards.** A user prompt can contain several independent workstreams. Extract those lanes first, then create one card per lane instead of bundling unrelated work into a single implementer card.
- **Run independent lanes in parallel.** If two cards do not need each other's output, leave them unlinked so the dispatcher can fan them out. Link only true data dependencies.
- **Never create dependent work as independent ready cards.** If a card must wait for another card, pass `parents=[...]` in the original `kanban_create` call. Do not create it first and link it later, and do not rely on prose like "wait for T1" inside the body.
- **If no specialist fits the available profiles, ask the user which profile to create or which existing profile to use.** Do not invent profile names; the dispatcher will silently drop unknown assignees.
- **Decompose, route, and summarize — that's the whole job.**

## Decomposition playbook

### Step 1 — Understand the goal

Ask clarifying questions if the goal is ambiguous. Cheap to ask; expensive to spawn the wrong fleet.

### Step 2 — Sketch the task graph

Before creating anything, draft the graph out loud (in your response to the user). Treat every concrete workstream as a candidate card:

1. Extract the lanes from the request.
2. Map each lane to one of the profiles you discovered in Step 0. If a lane doesn't fit any existing profile, ask the user which to use or create.
3. Decide whether each lane is independent or gated by another lane.
4. Create independent lanes as parallel cards with no parent links.
5. Create synthesis/review/integration cards with parent links to the lanes they depend on. A child created with unfinished parents starts in `todo`; the dispatcher promotes it to `ready` only after every parent is done.

Examples of prompts that should fan out (using placeholder profile names — substitute whatever exists on the user's setup):

- "Build an app" → one card to a design-oriented profile for product/UI direction, one or two cards to engineering profiles for implementation, plus a later integration/review card if the user has a reviewer profile.
- "Fix blockers and check model variants" → one implementation card for the blocker fixes plus one discovery/research card for config/source verification. A final reviewer card can depend on both.
- "Research docs and implement" → a docs-research card can run in parallel with a codebase-discovery card; implementation waits only if it truly needs those findings.
- "Analyze this screenshot and find the related code" → one card to a vision-capable profile for the visual analysis while another searches the codebase.

Words like "also," "finally," or "and" do not automatically imply a dependency. They often mean "make sure this is covered before reporting back." Only link tasks when one card cannot start until another card's output exists.

Show the graph to the user before creating cards. Let them correct it — including which actual profile name should own each lane.

### Step 3 — Create tasks and link

Use the profile names from Step 0. The example below uses placeholders `<profile-A>`, `<profile-B>`, `<profile-C>` — replace them with what the user actually has.

```python
t1 = kanban_create(
    title="research: Postgres cost vs current",
    assignee="<profile-A>",  # whichever profile handles research on this setup
    body="Compare estimated infrastructure costs, migration costs, and ongoing ops costs over a 3-year window. Sources: AWS/GCP pricing, team time estimates, current Postgres bills from peers.",
    tenant=os.environ.get("HERMES_TENANT"),
)["task_id"]

t2 = kanban_create(
    title="research: Postgres performance vs current",
    assignee="<profile-A>",  # same profile, run in parallel
    body="Compare query latency, throughput, and scaling characteristics at our expected data volume (~500GB, 10k QPS peak). Sources: benchmark papers, public case studies, pgbench results if easy.",
)["task_id"]

t3 = kanban_create(
    title="synthesize migration recommendation",
    assignee="<profile-B>",  # whichever profile does synthesis/analysis
    body="Read the findings from T1 (cost) and T2 (performance). Produce a 1-page recommendation with explicit trade-offs and a go/no-go call.",
    parents=[t1, t2],
)["task_id"]

t4 = kanban_create(
    title="draft decision memo",
    assignee="<profile-C>",  # whichever profile drafts user-facing prose
    body="Turn the analyst's recommendation into a 2-page memo for the CTO. Match the tone of previous decision memos in the team's knowledge base.",
    parents=[t3],
)["task_id"]
```

`parents=[...]` gates promotion — children stay in `todo` until every parent reaches `done`, then auto-promote to `ready`. No manual coordination needed; the dispatcher and dependency engine handle it.

If the task graph has dependencies, create the parent cards first, capture their returned ids, and include those ids in the child card's `parents` list during the child `kanban_create` call. Avoid creating all cards in parallel and linking them afterward; that creates a window where the dispatcher can claim a child before its inputs exist.

### Step 4 — Complete your own task

If you were spawned as a task yourself (e.g. a planner profile was assigned `T0: "investigate Postgres migration"`), mark it done with a summary of what you created:

```python
kanban_complete(
    summary="decomposed into T1-T4: 2 research lanes in parallel, 1 synthesis on their outputs, 1 prose draft on the recommendation",
    metadata={
        "task_graph": {
            "T1": {"assignee": "<profile-A>", "parents": []},
            "T2": {"assignee": "<profile-A>", "parents": []},
            "T3": {"assignee": "<profile-B>", "parents": ["T1", "T2"]},
            "T4": {"assignee": "<profile-C>", "parents": ["T3"]},
        },
    },
)
```

### Step 5 — Report back to the user

Tell them what you created in plain prose, naming the actual profiles you used:

> I've queued 4 tasks:
> - **T1** (`<profile-A>`): cost comparison
> - **T2** (`<profile-A>`): performance comparison, in parallel with T1
> - **T3** (`<profile-B>`): synthesizes T1 + T2 into a recommendation
> - **T4** (`<profile-C>`): turns T3 into a CTO memo
>
> The dispatcher will pick up T1 and T2 now. T3 starts when both finish. You'll get a gateway ping when T4 completes. Use the dashboard or `hermes kanban tail <id>` to follow along.

## Common patterns

**Fan-out + fan-in (research → synthesize):** N research-style cards with no parents, one synthesis card with all of them as parents.

**Parallel implementation + validation:** one implementer card makes the change while one explorer/researcher card verifies config, docs, or source mapping. A reviewer card can depend on both. Do not make the implementer own unrelated verification just because the user mentioned both in one sentence.

**Pipeline with gates:** `planner → implementer → reviewer`. Each stage's `parents=[previous_task]`. Reviewer blocks or completes; if reviewer blocks, the operator unblocks with feedback and respawns.

**Same-profile queue:** N tasks, all assigned to the same profile, no dependencies between them. Dispatcher serializes — that profile processes them in priority order, accumulating experience in its own memory.

**Human-in-the-loop:** Any task can `kanban_block()` to wait for input. Dispatcher respawns after `/unblock`. The comment thread carries the full context.

## Pitfalls

**Inventing profile names that don't exist.** The dispatcher silently fails to spawn unknown assignees — the card just sits in `ready` forever. Always assign to a profile from your Step 0 discovery; ask the user if you're unsure.

**Bundling independent lanes into one card.** If the user asks for two independent outcomes, create two cards. Example: "fix blockers and check model variants" is not one fixer task; create a fixer/engineer card for the fixes and an explorer/researcher card for the variant check, then optionally gate review on both.

**Over-linking because of wording.** "Finally check X" may still be parallel with implementation if X is static config, docs, or source discovery. Link it after implementation only when the check depends on the implementation result.

**Forgetting dependency links.** If the task graph says `research -> implement -> review`, do not create all tasks as independent ready cards. Use parent links so implement/review cannot run before their inputs exist.

**Reassignment vs. new task.** If a reviewer blocks with "needs changes," create a NEW task linked from the reviewer's task — don't re-run the same task with a stern look. The new task is assigned to the original implementer profile.

**Argument order for links.** `kanban_link(parent_id=..., child_id=...)` — parent first. Mixing them up demotes the wrong task to `todo`.

**Don't pre-create the whole graph if the shape depends on intermediate findings.** If T3's structure depends on what T1 and T2 find, let T3 exist as a "synthesize findings" task whose own first step is to read parent handoffs and plan the rest. Orchestrators can spawn orchestrators.

**Tenant inheritance.** If `HERMES_TENANT` is set in your env, pass `tenant=os.environ.get("HERMES_TENANT")` on every `kanban_create` call so child tasks stay in the same namespace.

## Decomposer model ve dil yonetimi

Kanban decomposer (`auxiliary.kanban_decomposer`), triage task'larini otomatik olarak alt gorevlere ayirir. Sistem prompt'u `hermes_cli/kanban_decompose.py` dosyasindaki `_SYSTEM_PROMPT` degiskenindedir. Decomposer `get_text_auxiliary_client("kanban_decomposer")` kullanir — **text-only**, multimodal/vision destegi YOKTUR.

**Dil kurali:** Sistem prompt'u Ingilizcedir ancak model input diline gore output dilini degistirebilir. Bunu engellemek icin prompt'a su satir eklenmistir: `IMPORTANT: ALL output MUST be in English, regardless of the language of the input task.`

Eger decomposer Turkce output uretirse, prompt'daki dil zorunlulugunu guclendir.

**Model secimi:** Decomposer icin DeepSeek V4 Flash onerilir — iki yoldan erisilebilir:
- **opencode-go (lokal proxy):** MIT lisansli, 13B aktif, sifira yakin gecikme
- **NVIDIA free tier:** Ucretsiz, model mapping `deepseek-ai/deepseek-v4-flash`
MiniMax M3 (NVIDIA) da calisir ama agir ve multimodal avantaji decomposer icin gereksizdir.

**Yeni provider izleme:** Atama sonrasi 1 hafta gozlem: JSON format, output dili, task sayisi, timeout/error orani.

Her iki model de test edilmis ve Ingilizce decomposition'da basarili olmustur (`see references/decomposer-model-comparison.md`).

**Custom provider config inheritance — `custom_providers` does NOT cascade.** When a profile's `config.yaml` sets `provider: custom:<name>`, the `custom_providers` block that defines the provider (endpoint, API key, model mappings) does NOT inherit from the main config. If the profile config only has `model:` and `provider:` lines without a matching `custom_providers` block, workers crash with `Unknown provider 'custom:<name>'`. Fix: copy the `custom_providers` block from the main config into the profile's config. After fixing, `unblock` + `dispatch` the blocked tasks.

Diagnostic: run `grep -A 15 custom_providers ~/.hermes/profiles/<profile>/config.yaml` — empty output means the block is missing.

**Skills-free task creation as fallback.** When skill resolution keeps failing (tasks `blocked` with `Unknown skill(s): X` even after symlinking), skip skill loading entirely: create replacement tasks without `--skill` and put explicit instructions in `--body` instead. This avoids the profile-scoped resolution problem altogether. Archive the old blocked tasks first, then:

```bash
hermes kanban create "TITLE" --assignee PROFILE --body "explicit instructions here..."
```

The task body can still tell the worker to use `web_search`, `web_extract`, `terminal` etc. — tools are available regardless of whether a skill is loaded.

**Profile-scoped skill resolution.** When a task has `skills: ['some-skill']` and is assigned to a non-default profile, the worker resolves skills from the **profile's** skills directory (`~/.hermes/profiles/<profile>/skills/`), NOT the global directory (`~/.hermes/skills/`). If the skill only exists globally, the worker crashes with `Unknown skill(s): some-skill` → `pid NNNN not alive` → `gave_up`. Fix: symlink the missing skill into the profile's directory:

```bash
ln -sfn ~/.hermes/skills/<category>/<skill-name> \
  ~/.hermes/profiles/<profile>/skills/<category>/<skill-name>
```

Then `unblock` + `dispatch` the blocked tasks. For batch recovery when many tasks share the same missing skill, loop over the task IDs (see `references/profile-skills-recovery.md` for the full recipe). This is one of the most common causes of "all tasks blocked, same profile" — check skill resolution before model/profile changes.

**CLI fallback when `kanban_create` isn't available.** The Python `kanban_create()` pseudo-API shown in examples is available to Kanban worker profiles, but orchestrator profiles (or any agent without the Kanban MCP toolset) must use the CLI: `hermes kanban create "TITLE" --body "..." --assignee "PROFILE" [--skill "SKILL"] [--json]`. NOTE: `title` is a **positional** argument — there is no `--title` flag. Using `--title` will fail with "unrecognized arguments."

**`create` + `dispatch` are two separate steps.** Creating tasks puts them in the board at `ready` status, but they won't run until the dispatcher picks them up. After creating tasks, run `hermes kanban dispatch --max N` to spawn workers. For parallel fan-out, set `--max` to the number of independent cards you just created. Without this step, tasks sit in `ready` indefinitely.

**Proxy overload under concurrent workers.** When 6+ workers hit the same proxy (e.g., `:19998`) simultaneously, the proxy's connection pool saturates and workers get `APITimeoutError` — even though the proxy itself is healthy. Symptom: some workers succeed, others time out with no pattern, `ss -tlnp | grep 19998` shows the port is up, a single `curl` test works fine. Root cause: the proxy (Python `http.server` or similar single-threaded proxy) can't handle N concurrent long-lived streaming connections. Fix: reduce dispatch concurrency (`hermes kanban dispatch --max 3` instead of `--max 6`), or stagger creation so workers don't all start in the same second. For cron-driven dispatches, add a `sleep 2` between `kanban dispatch` calls. Also check proxy health beforehand: if `curl -s http://127.0.0.1:19998/v1/models` times out under load but works when idle, the proxy is the bottleneck.

**Gateway drain timeout during restart.** When `hermes gateway restart` is issued while Kanban workers are active, the gateway enters drain mode — it waits for in-flight worker processes to finish before shutting down. If workers are stuck (model timeout, context overflow), drain never completes and workers are left in `running` state with no gateway to report back to. Symptom: after restart, `hermes kanban list` shows tasks stuck in `running`, `hermes kanban runs` shows zombie processes with no recent activity. Fix: before gateway restart, reclaim all running tasks first (`hermes kanban reclaim <task_id>` for each), verify board is clean (`hermes kanban list --status running` returns empty), then restart. After restart, re-dispatch. If tasks are already stuck post-restart, use `hermes kanban reclaim` then `hermes kanban dispatch`.

## Goal-mode cards (persistent workers)

By default a dispatched worker gets **one shot** at its card: it does its work, calls `kanban_complete`/`kanban_block`, and exits. For open-ended cards where one turn rarely finishes the job, pass `goal_mode=True` to wrap that worker in a Ralph-style goal loop — the same engine behind the `/goal` slash command:

```python
kanban_create(
    title="Translate the full docs site to French",
    body="Acceptance: every page translated, no English left, links intact.",
    assignee="<translator-profile>",
    goal_mode=True,        # judge re-checks the card after each turn
    goal_max_turns=15,     # optional budget (default 20)
)["task_id"]
```

How it behaves:
- After each worker turn, an auxiliary judge evaluates the worker's response against the card's **title + body** (treated as the acceptance criteria).
- Not done + budget remains → the worker keeps going **in the same session** (full context retained — not a fresh respawn).
- Worker calls `kanban_complete`/`kanban_block` itself → loop stops, normal lifecycle.
- Budget exhausted without completion → the card is **blocked** for human review (sticky), never a silent exit.

When to use it: long, multi-step, or "keep going until X is true" cards. When NOT to: cheap one-shot cards (translation of a single string, a quick lookup) — the judge overhead isn't worth it, and the dispatcher's existing retry/circuit-breaker already handles transient worker failures.

Write the body as **explicit acceptance criteria** — the judge is only as good as the goal text. "Translate the README" is weaker than "Translate every section of the README to French; no English sentences remain."

## Recovering stuck workers

When a worker profile keeps crashing, hallucinating, or getting blocked by its own mistakes (usually: wrong model, missing skill, broken credential), the kanban dashboard flags the task with a ⚠ badge and opens a **Recovery** section in the drawer. Three primary actions:

1. **Reclaim** (or `hermes kanban reclaim <task_id>`) — abort the running worker immediately and reset the task to `ready`. The existing claim TTL is ~15 min; this is the fast path out.
2. **Reassign** (or `hermes kanban reassign <task_id> <new-profile> --reclaim`) — switch the task to a different profile (one that exists on this setup) and let the dispatcher pick it up with a fresh worker.
3. **Change profile model** — edit `~/.hermes/profiles/<profile>/config.yaml` and change the `model:` field. The `hermes -p <profile> model` command opens an interactive picker — it does NOT accept CLI arguments for model/provider. For non-interactive fixes, use `patch` or direct file edit. After changing the model, use `hermes kanban unblock <task_id>` (not reclaim — reclaim resets to ready but doesn't clear the blocked sticky state) then `hermes kanban dispatch` to spawn fresh workers. If ALL tasks are blocked with the same profile, fix the profile model once, unblock all, then dispatch.

Hallucination warnings appear on tasks where a worker's `kanban_complete(created_cards=[...])` claim included card ids that don't exist or weren't created by the worker's profile (the gate blocks the completion), or where the free-form summary references `t_<hex>` ids that don't resolve (advisory prose scan, non-blocking). Both produce audit events that persist even after recovery actions — the trail stays for debugging.
