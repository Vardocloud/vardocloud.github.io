# LinkedIn Post Delegation Pattern

## Why delegate?
Vanitas is the orchestrator, not the worker. When preparing LinkedIn posts directly, the conversation with Edel stalls for 3-5 minutes while research and drafting happens. Delegation solves this.

## Pattern

```
Edel: "post hazırla" veya cron trigger
        │
Vanitas: delegate_task(goal="LinkedIn post taslağı hazırla...")
        │
        ├── Alt ajan: APA/Monitor tara → duplicate kontrol → Türkçe taslak yaz
        │
Vanitas: Edel ile sohbete devam eder
        │
Alt ajan: Taslak hazır, döner
        │
Vanitas: Taslağı Edel'e gösterir, onay bekler
        │
Edel onaylarsa → linkedin_api.py post
```

## delegate_task goal template (güncel: v0.15.1 delegation fix çalışıyor)

**Delegation config:** `provider: pollinations`, `model: gemini-flash-lite-3.1` (ücretsiz)
```
Bardo Psychology için LinkedIn post taslağı hazırla.

1. APA Monitor on Psychology veya güncel psikoloji kaynaklarından ilginç bir makale bul
2. ~/.hermes/data/linkedin_posts.json dosyasını oku, duplicate kontrolü yap
3. Türkçe, Edel'in ses tonuna uygun 800-1500 karakter post yaz
4. Profesyonel ama samimi, psikolog kimliğine uygun
5. 3-5 hashtag ekle (#psikoloji #bardo vs)
6. Kapanış DOĞAL olsun — asla zorlama CTA sorusuyla bitirme (\"Siz en son ne zaman...\" YASAK)

Dönüş: Tam post metni + kaynak URL + başlık. Postu PAYLAŞMA, sadece taslak hazırla.
```

## Anti-pattern (YAPMA)
- ❌ Kendin araştırıp kendin yaz
- ❌ Edel'i beklet
- ❌ Taslak hazırlarken sessiz kal

## Cron jobs should also use this
LinkedIn cron job'ları da bu pattern'i kullanmalı: cron ajanı → delegate_task → sonucu Edel'e ilet.
