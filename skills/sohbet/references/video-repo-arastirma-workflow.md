# Video/Repo Araştırma Workflow'u

Edel bir YouTube linki veya GitHub reposu attığında izlenecek akış.

## Video (YouTube)

1. **web_extract** ile sayfa içeriğini çek (başlık + açıklama + özet)
2. yt-dlp denenebilir ama genelde 429 verir — web_extract yeterli
3. **Özeti oku, 2-3 kritik nokta çıkar** — Edel'in işine yarayacak kısımları filtrele
4. **Sohbete bağla**: "Şu ilginç, senin için şu anlama geliyor" formatında
5. Edel ilgi gösterdiği konuları **wiki'ye** (kişisel strateji) veya **NotebookLM'e** (araştırma referansı) kaydet
6. "Bilgiyi etiketle arşive kaldır" → NotebookLM: etiketle + uygun notebook'a ekle

## GitHub Repo

1. **web_extract** ile README + docs çek
2. "Bilgiyi sömür" → tüm özellikleri, mimariyi, lisansı, dili çıkar
3. **Bizim sistemle karşılaştır**: Ne bizde var, ne onlarda var, ne alınabilir?
4. **Pratik çıkarım yap**: "Bundan X'i alabiliriz, Y'si bizde zaten var"
5. Edel "kenarda kalsın" derse → NotebookLM'e etiketle
6. Edel "bunu uygulayalım" derse → cron/script olarak aksiyona geç

## Örnek Akış

```
Edel: https://github.com/open-jarvis/OpenJarvis bilgiyi sömür
Vanitas: [web_extract] → [analiz] → [karşılaştırma]
         "Şunlar ortak, şu bizde yok, DSPy öğrenme döngüsünü alabiliriz"
Edel: peki kenarda kalsın etiketle
Vanitas: [NotebookLM'e kaydet + etiketle] → "Arşivlendi ✅"
```

## PITFALL

- Video/repo analizini sohbeti bölmeden yap. Önce hızlıca oku, ana fikri söyle, Edel'in yönlendirmesine göre derinleş.
- "Bunu da not et" dediğinde hemen kaydet, sonraya bırakma.
- Karşılaştırma tablosu yaparken kısa tut — 4-5 satır yeterli.
