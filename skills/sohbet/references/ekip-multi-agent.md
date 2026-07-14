# Ekip Multi-Agent Sistemi (31 Mayis 2026)

5 uzman ajan ile paralel gorev dagitimi.

## Guncel Ajanlar

| Ajan | Model | Platform | Erisim | Token |
|------|-------|----------|--------|-------|
| 🔬 Analist | GLM-5.1 | OpenCode Go | curl :19998 | 2000 |
| ✍️ Yazar | GPT-5.4-mini | Pollinations | curl :19999 | 1000 |
| 📦 Yardimci | Gemma 4-26B | Pollinations | curl :19999 | 200 |
| 🔧 Kodcu | MiniMax M2.7 | OpenCode Go | curl :19998 | 1500 |
| 🧠 Degerlendirici | StepFun 3.5 Flash | Zenmux | ctx_execute_file | 8000 |

## StepFun Ozel
- Erisim: ctx_execute_file ile /tmp/.or_key uzerinden OpenRouter
- ALL_PROXY="" zorunlu (WARP OpenRouter'i bloklar)
- max_tokens=4000 (reasoning yapabilir, dusuk token'da bos doner)
- Kullanim: sohbet kalitesi puanlamasi, Edel ogrenme analizi
- Model: stepfun/step-3.7-flash (OpenRouter'da ucretsiz)

## Cron Job'lar (Ekip Adapte)
- LinkedIn sabah/aksam: Analist -> Yazar -> Yardimci
- APA icerik: Analist -> Yazar
- Gmail pipeline: Analist -> Yazar
- Sohbet degerlendirme: Degerlendirici (StepFun)
