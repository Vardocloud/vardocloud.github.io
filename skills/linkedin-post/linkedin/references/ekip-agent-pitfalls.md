# EKİP Ajan Pitfall'ları

Cron job sırasında EKİP multi-agent sisteminde karşılaşılan hatalar.

## GLM-5.1 İkili Başarısızlık Modu (2 Haz 2026)

GLM-5.1 (Analist, OpenCode Go port 19998) iki farklı şekilde başarısız olabilir:

### Tip A — Boş Dönme (1 Haz)
BAZI içerik tiplerinde max_tokens yeterli olsa bile content BOŞ döner. `finish_reason` gelmez, ham yanıt 1 byte.
- **Belirti:** `curl` yanıtı 1 byte (boş), `jq '.choices[0].message.content'` null/boş, exit code 0

### Tip B — Timeout (2 Haz)
OpenCode Go proxy üzerinden GLM-5.1 hiç yanıt vermez, `--max-time 45` ve `--max-time 60` ile bile exit code 28.
- **Belirti:** `curl` exit code 28, çıktı tamamen boş

### Çözüm (Her İki Tip İçin Aynı)
GPT-5.4-mini fallback (ZORUNLU). GLM-5.1 başarısız olursa hemen port 19999'a aynı prompt ile dene:
```bash
curl -s --max-time 60 http://127.0.0.1:19999/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-5.4-mini","messages":[...],"max_tokens":2000}'
```
GPT-5.4-mini her iki durumda da sorunsuz çalışır. İkinci kez GLM-5.1 deneme.

## Yardımcı/Gemma #terapi Sabotajı (2 Haz 2026)

Gemma 4-26B (Yardımcı, port 19999), "#terapi kullanma" kuralına rağmen post metnine #terapi EKLEYEBİLİR.

### Belirti
Yardımcı kontrol çıktısında: `"#terapi Kontrolü: Metinde \"#terapi\" kelimesi eksikti, içeriğin bağlamına uygun şekilde eklendi."`

Gemma, kuralı görmezden gelip "eksik" olarak algılayıp ekliyor.

### Çözüm
- Gemma kontrolüne ASLA güvenme — postu her zaman manuel kontrol et
- #terapi hashtag'i varsa SIL (Gemma eklemiş olabilir)
- Hashtag sayısı kontrolü de güvenilmez — Gemma "8 hashtag var, 4'e indirdim" deyip hala fazla bırakabiliyor
- Final postu Vanitas kendisi gözden geçirip hashtag'leri 3-4'e indirmeli
