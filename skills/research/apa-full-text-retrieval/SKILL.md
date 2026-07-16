---
name: apa-full-text-retrieval
description: "APA Monitor makalelerinin tam metnini browser ile çekme — CAPTCHA retry, write_file ile güvenilir kayıt, hata raporlama"
version: 1.0.0
metadata:
  hermes:
    tags: [apa, full-text, browser, web-scraping, monitor]
    category: research
---

# APA Full Text Retrieval

APA Monitor makalelerinin tam metnini browser ile çekip wiki'ye kaydetme workflow'u.

## Ne Zaman Kullanılır

- APA Monitor makalelerini full metin olarak wiki'ye kaydederken
- Özet formatındaki makaleleri full metne çevirirken
- Subagent ile paralel işleme yaparken

## Subagent Talimatları (Template)

Aşağıdaki talimatları subagent `context` veya `goal` alanına kopyala:

### CRITICAL RULES

```
## ADIM 1: browser_navigate
- browser_navigate(url) ile sayfaya git
- SAYFA BOYUTUNU KONTROL ET: Eğer snapshot çok küçükse (<2000 byte snapte element yoksa), CAPTCHA yemişsindir
- CAPTCHA VARSA: 10 saniye bekle, browser_navigate'ı tekrar dene
- 3 kez dene, hâlâ CAPTCHA'da kalıyorsa → ATLA (bu makaleyi işleme, link ekle)
- CAPTCHA YOKSA: devam et

## ADIM 2: browser_console ile metin çek
- Şu JS kodunu çalıştır: (()=>{const m=document.querySelector('main')||document.querySelector('[role="main"]');return m?m.innerText:document.body.innerText})()
- Eğer çıktı <500 char ise → sayfa yüklenmemiştir, CAPTCHA var demektir → ADIM 1'deki retry'i yap
- Çıktı varsa → adım 3'e geç

## ADIM 3: Wiki dosyasına kaydet
- write_file KULLAN (patch KULLANMA — patch sessizce başarısız olur!)
- Mevcut wiki dosyasını oku (read_file ile)
- Frontmatter'ı (--- ... --- arası) koru, şunları güncelle:
  - type: summary → type: full-text
  - sources'a URL ekle (eğer yoksa)
  - updated: bugünün tarihi
- İçerik olarak şu formatı kullan:
  ```
  ---
  [güncellenmiş frontmatter]
  ---

  # [Başlık]

  **Source:** [kaynak bilgisi]
  **Author:** [yazar] | **Reading time:** [süre]
  **URL:** [kaynak URL]

  ## Full Article Text

  [browser_console çıktısının TAMAMI — kısaltma yapma]
  ```

## ADIM 4: Doğrulama
- write_file sonrası read_file ile dosyayı tekrar oku
- Boyut KONTROL ET: Eski dosyadan büyük olmalı (full text > 5KB, özet < 3KB)
- Eğer dosya boyutu değişmemişse → yazma başarısız olmuştur, RAPOR ET

## ADIM 5: Hata durumunda (CAPTCHA devam ederse veya dosya yazılamazsa)
- Makaleyi ATLA
- Çıktı olarak şunu raporla: "ARTICLE_FAILED: [dosya adı] — sebep: [CAPTCHA / write_error]"
```

## Subagent Gönderme Şablonu

```python
delegate_task(
    tasks=[{
        "goal": "APA Monitor makalesinin tam metnini browser ile çek ve wiki dosyasını güncelle. CAPTCHA varsa 3 kere dene, olmazsa link ekle.",
        "context": f"""Wiki dizini: ~/wiki/apa-articles/

Makale: '{title}'
URL: {url}
Dosya: {filename}

{self_correction_rules}""",
        "toolsets": ["browser", "file", "terminal"]
    }]
)
```

## Hata Raporlama Formatı

```
SUCCESS: filename.md → full-text (X KB)
FAILURE: filename.md → CAPTCHA after 3 retries
FAILURE: filename.md → write_file error: [mesaj]
SKIP: filename.md → no web page available (newsletter)
LINK_ONLY: filename.md → URL added, couldn't extract full text
```

## Manuel Çekim (Subagent Çalışmazsa)

Subagent CAPTCHA'ya takılıp 3 denemede de başaramazsa, makaleyi manuel olarak ana oturumda aç:

1. `browser_navigate(url)` — ana oturum genelde çalışır
2. `browser_console(JS)` ile metni al
3. `write_file(path, content)` ile kaydet

Not: Bu skill'i kullanırken subagent'ların hata raporlarını KONTROL ET. Subagent'lar "✅" diyebilir ama aslında yazmamış olabilir — her zaman file size ile doğrula.
