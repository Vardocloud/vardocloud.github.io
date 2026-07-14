# Audio Overview (Podcast) Oluşturma — nlm CLI Workflow (1 Temmuz 2026)

## Tam Workflow

Transkript/dökümandan NotebookLM Audio Overview (Deep Dive podcast) oluşturma:

```bash
# 1. Yeni notebook oluştur
nlm notebook create "Başlık" --json
# → notebook_id al: örn. f24a58e3-a613-468d-825f-ef8ac9579d98

# 2. Kaynak olarak transkript/dosya/URL yükle
nlm source add NOTEBOOK_ID \
  --url "https://ornek.com/sayfa" \   # Web sayfası (yeni alternatif)
  --file /path/to/transkript.md \     # Yerel dosya
  --title "Kaynak Başlığı" \
  --wait
# --wait ile işlenmesini bekle (timeout 600sn)

# 3. Audio Overview oluştur
nlm audio create NOTEBOOK_ID \
  --format deep_dive \    # deep_dive, brief, critique, debate
  --length long \         # short, default, long
  --confirm               # onay sorusunu atla
# → Artifact ID al: örn. 48085236-dbce-4184-b26d-8c3a0ee97301

# 4. İndir (işlem 5-15 dk sürebilir)
nlm download audio NOTEBOOK_ID \
  --output /path/to/output.m4a \
  --no-progress
```

## Önemli Tespitler

### `nlm studio status` ve `nlm list artifacts` güvenilmez
Bu komutlar sıklıkla "Error: Could not retrieve studio status" hatası verir.
**Çözüm:** Direkt `nlm download audio` dene — eğer audio hazırsa indirir, değilse hata döner.
Studio status çalışmıyor diye audio oluşmamış değildir.

## Background + Notify Pattern (Polling Yapma)

Edel sürekli polling mesajı istemez. Audio generation 5-15 dk sürebilir.

Doğru yöntem: `nlm audio create`'i `terminal(background=true, notify_on_complete=true)` ile çalıştır. İşlem bitince otomatik bildirim gelir, arada mesaj yağdırma.

### `nlm audio create` async çalışır
Audio oluşturma hemen döner, arka planda işlenir. Polling için:
- `nlm download audio` dene → başarılıysa hazır
- 5-10 dk bekle, tekrar dene
- Alternatif: 10dk sonra kontrol edecek one-shot cron job kur

### Format seçenekleri
- `deep_dive` — iki sunucu derinlemesine tartışır (önerilen)
- `brief` — kısa özet
- `critique` — eleştirel bakış
- `debate` — tartışma formatı

### Yerel dosya yükleme
`nlm source add --file yerel_dosya.md --wait` ile .md, .pdf, .txt dosyaları yüklenebilir.
`--wait` flag'i işleme tamamlanana kadar bekler (önemli — sonraki adım için kaynağın hazır olması gerekir).
