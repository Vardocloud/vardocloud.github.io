# Cron + Telegram hatırlatma mesajı: Azure content_filter sorununda pratik workaround

## Problem belirtileri
- Cron job çalışırken **HTTP 400** döner.
- Hata metninde `content_filter` geçer ve “Azure OpenAI content management policy” yanıt filtrelemesi belirtilir.

## Gözlenen yaklaşım (bu oturumdan)
1) Cron prompt’unu daha **nötr ve tamamen sabit** bir metne indir.
   - Örn. istek metnini sadece tek satırda hedef mesajla sınırla: `ocağın altını kapat`.
2) Açıklama cümlelerini kaldır.
   - “hatırlatma yap / Edel’e şu ilet / Telegram’da gönder” gibi LLM’in yorum üretmesine alan açan fazlalıkları azalt.
3) Tek seferlik repeat + kısa aralık dene.

## Kural (genelleme)
- Amaç yalnızca **mesaj iletmek** ise cron prompt’u **LLM üretimi beklemeyecek kadar düz/sabit** tut.
- Amaç **içerik üretmek** ise (özet/plan/yazı), prompt’u tone/claim minimizasyonu ve “riskli ifade” azaltımı ile filtreye takılmayacak hale getir.

## Doğrulama / Kanıt
- Job başarısızsa log’ta `code: content_filter` var mı bak.
- Prompt sadeleştirince tekrar dene; önceki job’u iptal et.

