# YouTube Backlink Pipeline (WIP)

Julian Goldie yöntemiyle YouTube → AI backlink stratejisi.
Bardo için ücretsiz trafik kaynağı.

## İş Akışı

```
APA/psikoloji içeriği
      ↓
NotebookLM veo video (Türkçe, kawaii, açıklayıcı)
      ↓
YouTube'a yükle (Bardo kanalı)
      ↓
Açıklamaya bardopsikoloji.com.tr linki koy
      ↓
AI blog'ları otomatik backlink üretsin
```

## Google OAuth YouTube Scope

### Pitfall: setup.py `--services` yok

`google-workspace/scripts/setup.py` `--services` parametresini desteklemiyor.
YouTube upload scope'u (`youtube.upload`) için OAuth URL'ine manuel ekleme yap:

```bash
$GSETUP --auth-url
# Çıkan URL'deki scope parametresini değiştir:
# scope=https://www.googleapis.com/auth/gmail.readonly+... → 
# scope=https://www.googleapis.com/auth/gmail.readonly+...+
#       https://www.googleapis.com/auth/youtube.upload
```

**Dikkat:** URL encode edilmiş + işaretleri `%2B` olarak geçer. URL'de `scope=...%2Bhttps%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyoutube.upload` şeklinde ekle.

1 Haz 2026: Denendi ama Edel "dene" dedi, sonuç bekleniyor.

### Alternatif: Ayrı OAuth client

YouTube API için ayrı bir OAuth client oluşturup sadece youtube scope'ları ile yetkilendir. Bu, mevcut token'ı bozmaz.

## NotebookLM veo Video

```python
# Türkçe kawaii açıklayıcı video
mcp_notebooklm_mcp_studio_create(
    notebook_id="...",
    artifact_type="video",
    video_format="explainer",
    visual_style="kawaii",
    language="tr",
    focus_prompt="psikoloji konseptini basit ve eğlenceli şekilde anlat",
    confirm=True
)
```

- Süre: 2-3 dakika
- Format: MP4
- Dil: Türkçe (BCP-47: `tr`)
- Stil: kawaii (alternatif: whiteboard, anime, watercolor)

## YouTube Upload (henüz yapılmadı)

OAuth scope alındıktan sonra:
- `google-api-python-client` ile `youtube.videos().insert()`
- Video: NotebookLM'den indirilen MP4
- Başlık: Türkçe, SEO'lu
- Açıklama: bardopsikoloji.com.tr linki + anahtar kelimeler

## Julian Goldie Analizi (1 Haz 2026)

- YouTube kanalı: ~281K abone, AI SEO nişi
- Yöntem: Uzun videolar → blog post → backlink
- Paralel EKİP analizi başarılı: delegate_task ile transcript + ürün sayfası aynı anda
- Rapor: `/home/ubuntu/julian_goldie_ozet.md`
