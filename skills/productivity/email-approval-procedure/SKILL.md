---
name: email-approval-procedure
description: "Mandatory approval workflow + natural writing guidelines before sending any email"
version: 1.1.0
author: Vanitas
tags: [email, approval, safety, procedure, writing-style]
---

# Email Approval Procedure (MANDATORY)

**Rule:** No email is sent without explicit user approval. No exceptions.

## Steps (apply in order every time):

### Step 0 — Pre-Flight Checklist (MANDATORY)
**Before showing the draft to the user, run this checklist in your head:**
- [ ] **Recipient correct?** (named contact > generic inbox)
- [ ] **All open questions included?** (especially **deadline** — most commonly missed)
- [ ] **Context about the user included?** (their background, university, program)
- [ ] **Tone natural?** Read the draft aloud — does it sound like you?

If the draft is a **university inquiry email**, also run the University Inquiry Checklist below before showing it. **Do not skip this — having the checklist in the skill is useless if you don't actually use it.**

### Steps 1-4

1. **Show the complete draft** — To, From, Subject, Body fully displayed to user.
2. **Ask for approval** — "Shall I send this?" / "Onaylıyor musun?" / "Gönderayım mı?"
3. **Wait** — Do not send until user explicitly says "yes", "send", "approved", "go ahead", "evet", "gönder", "onaylıyorum", "tamam".
4. **If edits requested** — Incorporate changes, return to step 0.

## Scope:
- Gmail (google-workspace skill)
- Outlook / SMTP
- Any email sending tool
- Also applies to cron jobs that send emails

## Rationale:
- Prevents robotic/unwanted emails
- Gives user full tone/preference control
- Reduces wrong-recipient risk

## Violation Handling:
- If user asks "why did you send without approval?" → Acknowledge error, apologize, re-read this skill
- Re-read this skill before any future email task

---

# Natural Email Writing Guidelines (PREVENT ROBOTIC TONE)

**Core Principle:** Write like a real person, not a template. The recipient should feel a human wrote this.

## Before Writing — Context Check:
- Who am I writing to? (admissions officer, professor, admin staff, peer)
- What's my real goal? (get info, build rapport, request action, follow up)
- What's the relationship? (cold, warm, existing conversation)

## Style Rules (Apply Every Time):

### 1. Opening — Human, Not Header
- ❌ "Dear Sir/Madam," / "To Whom It May Concern,"
- ✅ "Hi [Name if known]," / "Hello," / "Good morning,"
- ✅ If cold: "Hi there," or "Hello [Department] team,"

### 2. Introduction — One Sentence, Personal
- ❌ "My name is X and I am writing to inquire about Y program."
- ✅ "I'm [Name], a psychology graduate from Turkey, and I've been researching your Clinical Psychology master's — the IQAA accreditation caught my eye."

### 3. Body — Conversational, Not Numbered Lists (Unless Truly Needed)
- ❌ Bullet points for everything (looks like a form)
- ✅ Group related questions into short paragraphs
- ✅ Use "I'd love to know..." / "Could you clarify..." / "One thing I'm unsure about..."
- ✅ If 5+ distinct questions → numbered list is OK, but keep language human

### 4. Tone Markers — Sprinkle Naturally
- "I'd really appreciate..."
- "Thanks in advance for any guidance"
- "Even a quick pointer to the right page would help"
- "I know this is a long list — sorry about that!"
- "No rush at all"

### 5. Closing — Warm, Not Stiff
- ❌ "Sincerely," / "Best regards," / "Yours faithfully,"
- ✅ "Thanks so much," / "Best," / "Cheers," / "Warmly,"
- ✅ Add one personal line: "Hope you have a good week" / "Enjoy the rest of your day"

### 6. Signature — Minimal
- Name
- Email (only if not obvious from From:)
- Phone/WhatsApp ONLY if relevant (e.g., "happy to hop on a quick call")

## Red Flags — Rewrite If You See These:
- "I am writing to inform you that..." → "Just wanted to let you know..."
- "Please find attached..." → "Attached is..." / "Here's the..."
- "Kindly advise..." → "Could you let me know..." / "What do you think?"
- "As per our conversation..." → "Following up on our chat..."
- "Per your request..." → "As you asked..."

## Quick Test Before Sending:
Read it aloud. Does it sound like YOU talking to a colleague? If it sounds like a corporate bot → rewrite.

## Special Cases:
- **Follow-up to no reply:** "Hi [Name], just floating this to the top of your inbox — no pressure, know you're busy!"
- **Professor/admissions:** Slightly more formal but still human: "Dear Professor [Last Name]," not "Dear Sir/Madam"
- **Complaint/issue:** Direct but polite: "I'm a bit concerned about..." not "I wish to lodge a formal complaint..."

---

# University / Program Inquiry Emails (MANDATORY CHECKLIST)

**Context:** When writing to a university (admissions, program coordinator, department head) to gather info about a program — master's, PhD, exchange — you MUST check all items below in the draft before showing the user. Missing any of these will likely result in a correction.

## Pre-Draft — Identify the Recipient
- Find the **right person**: program coordinator, department head, international office (not generic info@ if a named contact exists)
- Check the university website for a specific contact page under the department/faculty
- If a named director/coordinator exists → write to them directly, CC the general address

## Mandatory Checklist for University Inquiry Emails

Read the draft against this list before showing the user. Ask yourself: **"Did I ask about ALL of these that are still unknown?"**

| # | Item | Example phrasing |
|---|------|-----------------|
| 1 | **Language of instruction** | "Is the full program available in English?" |
| 2 | **Tuition fee** | "What is the tuition for international students?" |
| 3 | **Application deadline** | "When is the final deadline for international applicants?" |
| 4 | **Admission requirements** | "What GPA / prerequisites are needed?" |
| 5 | **Required documents** | "What documents must be submitted beyond the application form?" |
| 6 | **Nostrification / equivalency** | "Does the university assist with degree equivalency/nostrification?" |
| 7 | **Duration & format** | "Full-time? How many semesters?" (if not already known) |

**⚠️ Deadline is the most commonly missed item.** Always double-check: "Did I include the deadline question?"

## When to Use This Checklist
- ANY email to a university/program about admission
- Follow-up emails: check which items from the previous email were answered, only ask the ones still open

## Pitfalls
| Pitfall | Fix |
|---------|-----|
| Asking everything in the first email is fine — don't split into 3 emails | Bundle all open questions into ONE natural email |
| Missing deadline = user will correct you | Run the checklist before showing the draft |
| Writing to the wrong person | Verify contact page before drafting |
| CC'ing irrelevant addresses | Only CC the general office, not random faculty |

---

## Alignment:
This procedure aligns with SOUL.md "Plan-Before-Execute" (3+ tool calls = plan → approval → execute) and "Security Rules". Email sending = draft + show + approve + send = 4 steps, requires explicit approval gate.