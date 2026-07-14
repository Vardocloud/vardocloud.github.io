# Profile-Scoped Skill Resolution — Recovery Recipe

## Problem

Kanban workers running under a non-default profile (e.g., `analist`) crash with:
```
Error: Unknown skill(s): unified-search
```
in their logs (`hermes kanban log <task_id>`). The task event log shows:
- `crashed` → `pid NNNN not alive` or `exited with code 1`
- `gave_up` after 1-2 attempts

## Root Cause

Workers resolve skills from the **profile's own skills directory**:
`~/.hermes/profiles/<profile>/skills/`

They do NOT see the global `~/.hermes/skills/`. When a task is created with
`skills: ['some-skill']` and that skill only exists globally, the worker fails
at startup — before it even begins the task body.

## Diagnosis

1. List blocked tasks: `hermes kanban list`
2. Check one task's log: `hermes kanban log <task_id>`
3. If log shows `Error: Unknown skill(s): X` — this is a profile-skills mismatch
4. Verify: `ls ~/.hermes/profiles/<profile>/skills/<category>/<skill-name>` — missing

## Fix (Batch)

```bash
# 1. Symlink missing skills from global to profile
PROFILE="analist"  # or whatever profile name
SKILLS_DIR=~/.hermes/profiles/$PROFILE/skills

for skill in unified-search brave-search serper-search tavily-search; do
  CATEGORY=$(find ~/.hermes/skills/ -maxdepth 2 -name "$skill" -type d | head -1)
  if [ -n "$CATEGORY" ]; then
    CAT_NAME=$(basename $(dirname "$CATEGORY"))
    mkdir -p "$SKILLS_DIR/$CAT_NAME"
    ln -sfn "$CATEGORY" "$SKILLS_DIR/$CAT_NAME/$skill"
    echo "✓ $skill → $PROFILE"
  fi
done

# 2. Unblock all tasks on the board
for tid in $(hermes kanban list 2>/dev/null | grep -oP 't_[a-f0-9]+'); do
  hermes kanban unblock "$tid"
done

# 3. Dispatch (daemon picks up automatically, or force with:)
# hermes kanban dispatch --max 6
```

## Prevention

When creating tasks with `skills: [...]`, verify the skill exists in the
target profile's skills directory first:

```bash
hermes kanban create "title" --assignee "analist" --skill "unified-search"
```

If the skill doesn't exist in the profile, symlink it BEFORE creating the task.
Or omit `--skill` entirely and include the necessary instructions directly in
the task body.

## Related

- Kanban workers auto-load `kanban-worker` skill (it's bundled)
- Any other skill referenced via `--skill` flag or `skills: [...]` must exist
  in the ASSIGNED PROFILE's skills tree, not just globally
- The `default` profile is special: it uses `~/.hermes/skills/` directly
