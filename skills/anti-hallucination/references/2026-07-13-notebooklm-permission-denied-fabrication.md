# Vaka: NotebookLM PERMISSION_DENIED Fabrication (13 Tem 2026)

## Özet
Skill'e yazılan bir pitfall, hiç test edilmeden "PERMISSION_DENIED" varsayımı yaptı. Cron ajanı bu pitfall'ı okuyunca NotebookLM kaynak eklemesini denemeden atladı. Oysa sistem çalışıyordu.

## Süreç

1. **Yanlış varsayım:** Skool cron'da NotebookLM'e kaynak eklenmesi gerekiyordu. Daha önce başka bir bağlamda (farklı bir Docker container'da) PERMISSION_DENIED görmüş olabilirim — ya da hiç görmeden varsaydım.
2. **Hiç test edilmeden skill'e yazıldı:** `skool-community-monitor` skill'ine "PERMISSION_DENIED = Docker path sorunu, sessizce geç" pitfall'ı eklendi.
3. **Cron'da kendi kendini doğrulayan kehanet:** Ajan skill'deki pitfall'ı okudu, ekleme yapmayı denemedi bile, "PERMISSION_DENIED" raporladı.
4. **Edel fark etti:** "Notebooklm aktif ve yükleme yapılabiliyor. Yanlış bilgi mi?"
5. **Kök neden bulundu:** Test edildiğinde MCP text source add VE CLI nlm source add --file İKİSİ de çalışıyordu. Hiç gerçek PERMISSION_DENIED hatası olmamıştı.
6. **Düzeltme:** Pitfall silindi, yerine "ÖNCE DENE" talimatı kondu. Hem `anti-hallucination` (Rule 1o) hem `agent-self-maintenance` (pitfalls) güncellendi.

## Alınacak Ders

| Hata | Düzeltme |
|------|----------|
| Skill'e test etmeden pitfall eklemek | Skill'e herhangi bir iddia eklemeden ÖNCE canlı test yap |
| "Şu an test edemiyorum ama yazayım" zihniyeti | "Şu an test edemiyorum" = "yazma" |
| Varsayımı doğrulamadan cron'a bırakmak | Varsayımları skill'de değil, test sonuçlarında sakla |
| Tek hata → çoğalan etki | Skill hatası, memory hatasından daha tehlikelidir (cron frekansı çarpanı) |

## Referans
- anti-hallucination Rule 1o — Skill Content Fabrication
- agent-self-maintenance pitfalls — verify skill claims before writing
