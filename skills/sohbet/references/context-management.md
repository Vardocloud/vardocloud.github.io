# Context Management & Task Tracking

## Problem

After context window compaction, the agent loses track of active tasks and can:
1. Repeat already-completed work
2. Misinterpret "Active Task" from the compaction summary
3. Start a different task than what the user is currently focused on

## Solution: Todo List + Orientation Rule

### Rule 1: Always Use Todo List
Add every new task to the todo list immediately. Even simple tasks.

```python
todo([{"content": "Task description", "id": "1", "status": "pending"}])
```

### Rule 2: Context Compaction Orientation
After any context window reset, follow this sequence:
1. Check `todo` list for pending tasks
2. Look at the user's LATEST message — that is the current request
3. Ask user "Neye yardımcı olabilirim?" rather than following stale "Active Task" from summary
4. The compaction summary's "Active Task" is NOT authoritative — it reflects the PREVIOUS context window

### Rule 3: User's Current Message Is Always Primary
```
Old context window → compaction → new context window
                                                    ↑
                                         User's latest message = ACTIVE REQUEST
                                         Compaction summary = BACKGROUND CONTEXT
```

The user's newest message takes priority over any summary.

## When User Says "That was an old request, it's done"

1. Apologize briefly
2. Check todo list
3. Mark that task as completed
4. Ask what they need now

## Example Anti-Pattern

```
User (new message): "Update my calendar"
Context summary had: "Active Task: Email client setup"
Agent: "Continuing with email client setup..." ← WRONG
Agent should: Check todo → ask "Neye yardımcı olabilirim?"
```

## Example Correct Pattern

```
User (new message): "Update my calendar"
Agent:
1. Check todo (empty or has unrelated tasks)
2. Say: "Güncel tutuyorum, todo'ları kontrol ediyorum"
3. Mark calendar task as in_progress
4. Execute the calendar update
```

## Real Session Example (2026-05-21)

**What happened:**
- Context window compacted, summary showed "Active Task: LinkedIn-post feature"
- User's NEW message was about calendar — old "Active Task" was stale
- Agent followed stale summary instead of checking todo + latest message
- User corrected: "Bunları takip etme yetini geliştir eski isteği hala devam ediyor sanıp bir anda atıldın. To do list'in yok mu senin?"

**Lesson:**
Always check todo FIRST, then ask "Neye yardımcı olabilirim?" — user's latest message is always authoritative.

## Memory Entry Template

After session, if context management issue occurred, add to memory:

```
Context compaction sonrası: todo list'i kontrol et, eski summary'deki "Active Task" güvenilir değil. Her zaman mevcut mesaja odaklan.
```