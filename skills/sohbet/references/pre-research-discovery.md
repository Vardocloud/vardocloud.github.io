# Pre-Research Discovery Pattern

**Lesson learned:** 2026-05-24 — Edel explicitly corrected Vanitas for launching broad research without asking clarifying questions first.

## The Pattern

When Edel asks for research (market analysis, strategy development, tool evaluation, competitor analysis), DO NOT immediately launch into broad web searches. Instead:

### Step 1: Discovery Questions (2-4 questions)
Ask focused questions to narrow scope:
- What existing resources does she have? (website, tools, campaigns)
- What has she already tried and failed? (saves time, avoids reinventing)
- What's the budget/time constraint?
- What's the specific target audience/problem?

### Step 2: Verify Existing Assets
- Check her website if she has one
- Review current tools/configs she mentions
- Look at what's already running (cron jobs, active campaigns)

### Step 3: THEN research
Only after answers, launch targeted research with the specifics baked in.

## Why This Matters

Edel said: "çok geniş alan gelen bilgiler genel geçer olabilir."

Broad research without context produces generic results. Focused research with her specifics produces actionable strategy.

## Anti-Pattern (What NOT to do)
```
Edel: "Geniş çaplı araştırma yap, strateji düşünelim"
Vanitas: [Immediately creates 4 cron jobs with broad research prompts]
Edel: "...bana sorular sor çünkü çok geniş alan" ✗
```

## Good Pattern
```
Edel: "Geniş çaplı araştırma yap, strateji düşünelim"
Vanitas: "Önce birkaç soruyla netleştireyim. Web siten hangisi? Bütçe ne kadar?"
Edel: [Gives specifics]
Vanitas: [Creates targeted research with those specifics] ✓
```

## Example Discovery Questions

- "Web siten var mı? Adresi nedir?"
- "Şu ana kadar neler denedin, hangisi çalıştı/çalışmadı?"
- "Aylık bütçe aralığın ne kadar?"
- "Hedef kitlen tam olarak kim?"
- "Şu an hangi araçları kullanıyorsun?"
