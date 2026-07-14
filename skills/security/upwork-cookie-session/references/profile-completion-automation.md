## Profile Completion Automation

### Skills Page (`/nx/create-profile/skills`)
- **Input selector:** `input[placeholder="Enter skills here"]`
- **Dropdown selector:** `[role="option"]` — click the first match (exact match usually first)
- **Add skills one by one:** type → wait 2s for dropdown → click first option → wait 1.5s
- **Verification:** check `page.locator('button').filter({ hasText: 'Remove' }).count()` after each add
- **Next button:** `page.locator('button').filter({ hasText: /Next/i })`

### Profile Title Page (`/nx/create-profile/title`)
- **Input selector:** `input[type="text"][placeholder="Example: Writing"]`
- **⚠️ Auto-fill trap:** Upwork auto-fills a suggestion (e.g. "Personal & Professional Coaching | Counseling Psychology, Psychology"). Must click **"Clear Input"** button FIRST, then type.
- **Keyboard type required:** `page.keyboard.type(title, { delay: 30 })` — `fill()` does NOT trigger Vue `v-model` and Next stays disabled. Keyboard typing fires keydown/keyup events Vue needs.
- **Next button location:** Buried among many "Edit"/"Delete" buttons for skills. May be at index 30+. List ALL buttons with `page.locator('button')` and find one containing "Next" AND "experience". Do NOT use `.filter({ hasText: /Next/i })` — it matches "Next item. Update list" (typeahead nav).
- **Verification:** Check `isDisabled()` on Next before clicking. If disabled, keyboard-typing didn't register — try again with slower delay.
- Format example: "Psychology Researcher & Academic Writer"

### Available Psychology Skills
Search "psycholog" → Psychology, Counseling Psychology, Industrial Psychology; "mental" → Mental Health; "counseling" → Counseling, Child Counseling; "academic" → Academic Research, Academic Editing, Academic Proofreading; "research" → Research Paper Writing, Research Methods; "behavioral" → Cognitive Behavioral Therapy; "thesis" → Thesis, Thesis Writing.