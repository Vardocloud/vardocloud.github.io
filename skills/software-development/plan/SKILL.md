---
name: plan
description: "Plan mode: write markdown plan to .hermes/plans/, no exec."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [planning, plan-mode, implementation, workflow]
    related_skills: [writing-plans, subagent-driven-development]
---

# Plan Mode

Use this skill when the user wants a plan instead of execution.

## Core behavior

For this turn, you are planning only.

- Do not implement code.
- Do not edit project files except the plan markdown file.
- Do not run mutating terminal commands, commit, push, or perform external actions.
- You may inspect the repo or other context with read-only commands/tools when needed.
- Your deliverable is a markdown plan saved inside the active workspace under `.hermes/plans/`.

## Output requirements

Write a markdown plan that is concrete and actionable.

Include, when relevant:
- Goal
- Current context / assumptions
- Proposed approach
- Step-by-step plan
- Files likely to change
- Tests / validation
- Risks, tradeoffs, and open questions

If the task is code-related, include exact file paths, likely test targets, and verification steps.

## Save location

Save the plan with `write_file` under:
- `.hermes/plans/YYYY-MM-DD_HHMMSS-<slug>.md`

Treat that as relative to the active working directory / backend workspace. Hermes file tools are backend-aware, so using this relative path keeps the plan with the workspace on local, docker, ssh, modal, and daytona backends.

If the runtime provides a specific target path, use that exact path.
If not, create a sensible timestamped filename yourself under `.hermes/plans/`.

## Interaction style

## Tetiklenme ve Komut

- Eğer kullanıcı “**delegate task yap**” veya “aynı anda / paralel / concurrently” gibi eşzamanlılık niyetiyle birden fazla alt işi ima ediyorsa:
  - Uygulama yapma.
  - Plan içinde, hangi alt işlerin paralel ayrılacağını ve her alt iş için beklenen çıktıların ne olacağını netleştir.
  - “Sadece plan; yürütme yok” uyarısını planın üst bölümüne ekle.

- Eğer test amaçlı bir doğrulama isteniyorsa (ör. Telegram gateway komutlarının çalışması):
  - Planın adımlarında “beklenen çıktı/kanıt” maddeleri mutlaka olsun (ekran çıktısı mı, dosya üretimi mi, status kodu mu).



- If the request is clear enough, write the plan directly.
- If no explicit instruction accompanies `/plan`, infer the task from the current conversation context.
- If it is genuinely underspecified, ask a brief clarifying question instead of guessing.
- After saving the plan, reply briefly with what you planned and the saved path.

## Pitfall: Zaman bazlı aksiyon beklentisi
- `/plan` sadece markdown plan üretir; **zamanlayıp mesaj gönderen bir icra** yapmaz.
- “5 dk sonra hatırlat / mesaj gönder” gibi zaman bazlı aksiyonlarda uygun skill: `cronjob` (veya aynı aracın zamanlama özelliği).
- Bu skill’de “mesajın gelmesi” başarı kanıtı değildir; başarı kanıtı: plan dosyasının `.hermes/plans/` altında oluşması ve içeriğin doğrulanabilir olmasıdır.

## Pitfall: Check server capabilities before suggesting manual intervention
When planning automation/setup tasks, **always probe the server first**:
- What tools are already installed? (Node, Python, Playwright, etc.)
- What permissions/configurations exist?
- Can the task be done without manual intervention from the user?

**Example:** User asked "önce buradan yapılabilir mi yoksa ben opencode açıp sunucuya girip mi yapayım onu bul" — this was a signal that I should have proactively checked `which node`, `which playwright`, etc. before suggesting manual setup.

Rule: Probe → Report → Then suggest manual intervention only if server cannot do it.

## Pitfall: Cron hatırlatmalarında içerik filtresi (content_filter) riski
- Bazı cronjob akışlarında metin/prompt içeriği LLM üzerinden işlenirken Azure OpenAI **content_filter** ile engellenebilir (örn. hatırlatma metni “riskli çağrışım” tetikleyebilir).
- Bu gibi durumlarda plan, “LLM üretimi” gerektiren metin işleme yerine **direct message/send** yolunu hedeflemelidir.
- Eğer kullanıcı “hatırlatma” istiyorsa planın önerdiği icra adımı şu olmalı:
  - zamanlama için cronjob
  - gönderim için mümkünse **LLM’siz / direkt send** yaklaşımı (özel hatırlatma skill’i veya doğrudan send mesaj aracı).
