# LinkedIn Post Delege İş Akışı (30 Mayıs 2026)

## Kural
LinkedIn post araştırma ve yazım işi **TAMAMEN** alt ajana (`delegate_task`) devredilir. Vanitas (üst beyin) sadece onay alır ve paylaşır.

## Neden?
Post hazırlarken Vanitas'ın tüm dikkati oraya gidiyor, Edel ile sohbet duruyor. Alt ajanlar arka planda çalışırken Vanitas Edel ile iletişime devam eder.

## Delege Prompt Kalıbı
```
Bardo Psychology için LinkedIn post taslağı hazırla. 

1. APA Monitor on Psychology veya güncel psikoloji kaynaklarından ilginç bir makale bul
2. ~/.hermes/data/linkedin_posts.json dosyasını oku, duplicate kontrolü yap
3. Türkçe, Edel'in ses tonuna uygun 800-1500 karakter post yaz
4. Profesyonel ama samimi, psikolog kimliğine uygun
5. 3-5 hashtag ekle (#psikoloji #bardo vs)
6. Call-to-action sorusu ekle

Dönüş: Tam post metni + kaynak URL + başlık. Postu PAYLAŞMA, sadece taslak hazırla.
```

## Arşiv ve Zamanlama
- Hazırlanan post `~/.hermes/data/linkedin_posts_archive.json` dosyasına `status: pending_approval` ile eklenir
- Tüm pending postlar öğün aralarına yayılır (10-11, 14-16 saatleri)
- Her post ÖNCESİ Edel'e sorulur, onaysız ASLA paylaşılmaz
- Paylaşılan post `status: posted` olarak güncellenir

## Cron Job'lar
Cron job'lar da aynı kurala uyar: alt ajana devret, sonuç gelince Edel'e sor, onayla paylaş.
