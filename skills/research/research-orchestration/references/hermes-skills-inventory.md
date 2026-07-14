# Hermes Skills Inventory Phase — Prompt Template

For orchestration projects where Vanitas will manage systems autonomously.
Copy this template and customize PROJECT_NAME and FOCUS_AREA.

## Prompt Template

```markdown
# PROJECT_NAME: Hermes Skills Envanteri & Eksik Haritası

Amaç: Vanitas'ın FOCUS_AREA'yı yönetebilmesi için Hermes'te hangi skill'ler var, hangileri yok, hangileri oluşturulmalı?

## ADIM 1: Mevcut Skill'leri Listele
skills_list() çağır ve TÜM skill'leri listele.

## ADIM 2: Hermes Agent Dökümantasyonunu İncele
- hermes-agent skill'ini skill_view ile yükle
- Özellikle: cron job, delegate_task, process, skill_manage yetenekleri
- context-mode MCP nasıl çalışıyor?

## ADIM 3: Eksik Haritası Çıkar
FOCUS_AREA için HERMES'te OLMASI GEREKEN ama OLMAYAN yetenekler

## ADIM 4: Oluşturulması Gereken Skill'lerin Taslağı
Her yeni skill için: İsim, araçlar, trigger, I/O formatı, tahmini süre

## ÇIKTI
~/research_PROJE/skills_inventory.md
```

## Key learnings from Bardo 2026-05-24

- skills_list() shows 97+ available skills across categories
- For Google Ads automation, NO existing skill covers it → need 3-4 new skills
- Skill creation uses skill_manage(action='create') with YAML frontmatter
- Each skill should be class-level (e.g., "google-ads-manager", not "bardo-ads")
- Existing relevant skills: subagent-driven-development, hermes-agent-skill-authoring
