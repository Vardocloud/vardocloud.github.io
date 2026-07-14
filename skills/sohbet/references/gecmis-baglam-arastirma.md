# SIN #13: Yeni mesaj/görevde önce geçmiş bağlamı araştırmamak

**Tarih:** 1 Temmuz 2026
**Olay:** Edel "Seminerde ne anlatılmış bilmek için..." dediğinde, direkt olarak NotebookLM işlemine başlandı. Oysa önceki oturumda (30 Haz 2026) bu seminere dair kayıt, transkript ve NotebookLM planı zaten yapılmıştı.
**Uyarı:** *"Bir önceki oturumu araştırmalısın konuşulanları."*

## Belirtiler

- Edel bir konu hakkında soru sorar ve bu konu daha önce işlenmiş bir sürece (kayıt, transkript, podcast, seminer, başvuru, araştırma) atıfta bulunur
- Cevabın başında "daha önce X yapmıştık" gibi bir referans geçmesi gerekir
- Edel "bir önceki oturum" veya "daha önce konuşmuştuk" der

## Çözüm

1. **Önce bağlamı yokla.** Edel'den yeni bir talimat/mesaj geldiğinde, konunun daha önce konuşulup konuşulmadığını kontrol et.
2. **session_search ile tara.** 2-3 farklı query ile dene. Örn: "seminer notebooklm", "transkript", "30 haziran"
3. **Compaction mesajını atlama.** Context compaction içindeki "Active State", "Completed Actions", "Remaining Work" bölümleri değerli bağlam bilgisi içerir.
4. **Yarım kalmış işi raporla.** Önceki oturumda yarım kalmış bir iş bulursan: "30 Haziran'da X yapılmış, Y kısmı yarım kalmıştı" diye raporla, sonra devam et.
5. **Dosya yollarını kullan.** "Active State" bölümünde ilgili dosya yolları varsa onları kullan — yeniden keşfetme.
6. **Doğrudan sor.** session_search sonuç vermezse: "Daha önce bu konuda bir şey yapmış mıydık?" diye sor, varsayım yapma.

## Test

Mesajına başlamadan önce kendine sor: *"Bu konuda daha önce bir şey yapıldı mı?"*
- Cevap evetse → session_search yap, geçmiş bağlamı bul
- Cevap hayırsa → devam et

## İlgili SIN'ler

- SIN #1: Topic/Thread körlüğü (oturumlar arası hafıza karıştırma)
- SIN #3: Session araştırma başarısızlığında doğrudan sor
- SIN #8: Talimatı anlayınca durmadan aynı şeyi sorma
