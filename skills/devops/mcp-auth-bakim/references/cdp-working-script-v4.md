# NotebookLM CDP Sorgu v4 (5 Tem 2026 — Çalışan Sürüm)

Kanıtlanmış çalışan CDP sorgu script'i. Keepalive Chrome CDP (port 18800)
üzerinden doğrudan NotebookLM'e soru sorar, cevap alır.

## Önemli Detaylar

- NotebookLM SPA — sayfa yüklendikten sonra DOM JavaScript ile render'lanır.
  `Page.loadEventFired` beklenmeli, sonra 5-10sn ek render süresi verilmeli.
- 2 textarea var (çakışmayı önlemek için `document.querySelector('textarea')`
  ilkini seçer — genelde chat input'udur).
- Cevap selector'u: `[class*=message]` (geniş kapsamlı, spesifik selector'lar
  NotebookLM güncellemeleriyle değişebilir).
- Yeni cevabı ayırt etmek için önceki mesajları `JSON.stringify` ile kaydet,
  yeni gelen mesaj karşılaştır.

## Kullanım

```bash
python3 cdp_notebooklm_query.py "Soru metni" bdt
# İkinci argüman: bdt | apa | veya direkt notebook UUID
```

## Notebook ID'leri

| Kısa ad | UUID | Hesap |
|---------|------|-------|
| bdt | a4fe729d-c561-4238-9bea-81bea8e3dcbc | pro (authuser=1) |
| apa | c44469fe-a69a-4a86-8dd8-756c2f365109 | legacy (authuser=0) |

## Kritik Dersler

1. **loadEventFired bekle.** frameNavigated hemen gelir ama DOM boştur.
   loadEventFired sonrası 1.5M karakter DOM oluşur, 3985 div, 2 textarea.
2. **Mesaj selinde evaluate.** 15 saniyede 550+ CDP mesajı gelir. Evaluate
   yanıtını sel içinde yakalamak için frameNavigated'te hemen evaluate gönder.
3. **Headi Chrome = --disable-gpu YOK.** `--disable-gpu` headed Chrome'da
   X11 bağlantısını engeller, process hemen ölür. Sadece headless modda güvenli.
4. **"Erişim izni gerekiyor" ≠ auth sorunu.** Notebook başka hesaba ait.
   authuser değiştir (0 isimgorulsunn, 1 kenshin4155).
