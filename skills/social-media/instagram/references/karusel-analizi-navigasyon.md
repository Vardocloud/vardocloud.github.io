# Karusel Navigasyon Pattern'i — Browser Snapshot ile Slayt Tarama

**Tarih:** 12 Temmuz 2026
**Örnek:** @soztech.ai — "Claude'da Sınırsız Özel Öğretmen" (10 slayt)

## Akış

1. **Post'u browser'da aç** — `browser_navigate(url)` ile
2. **Login popup'ını kapat** — Instagram "Join @kullanici on Instagram" dialog'u açılır:
   - Snapshot'ta `button "Close" [ref=e178]` bulunur → `browser_click(ref="e178")`
   - Popup kapandıktan sonra post içeriği görünür kalır
3. **Snapshot'ta karusel slaytlarını tespit et**:
   - Karusel slaytları `listitem` olarak DOM'da görünür (snapshot'ta `listitem [level=1]`)
   - Her slayt bir `image` elementi içerir, alt text'i slaytın metnini verir
   - **Standart görünüm:** 3 slayt aynı anda listede görünür (örn. 1-2-3, 4-5-6, vb.)
4. **"Next" / "Go back" butonları ile gezin**:
   - Snapshot'ta `button "Next" [ref=e178]` ve `button "Go back" [ref=e177]` bulunur
   - Her tıklamada listedeki 3 slayt kayar (ileri veya geri)
   - **10 slaytlık karuselde:** ~4 "Go back" tıklaması başa dönmek için yeterli
5. **Her slayda ayrıca tıkla:** Slaytın listitem'ine tıklamak büyük görünüm açar:
   - `browser_click(ref="e..." )` ile slaydın bulunduğu listitem'a tıkla
   - Büyük görünümde daha detaylı snapshot alınabilir
   - Kapatmak için tekrar tıkla veya "Close" butonunu kullan

## Snapshot'ta Slayt İçeriğini Okuma

Karusel slaytları snapshot'ta `image` olarak görünür. Alt text (`May be an image of ...` veya `Photo by ...`) slaytın başlığını ve özetini verir:

```
image "Photo by Kullanıcı on Tarih. May be an image of text that says 
'5/ Claude'a dağınık kodu temiz, ölçeklenebilir bir mimariyle yeniden inşa ettir 
Dağınık bir üretim kod tabanını temiz mimari ilkeleriyle yeniden inşa eden...'"
```

- **img alt text'i** = çalışan tek metin kaynağı (Instagram slide_deck image-based olduğu için)
- **Slayt başlığı + özet** birlikte alt text'te okunabilir
- Instagram otomatik alt text ürettiği için bazen kesik/eksik olabilir

## Caption Okuma

Caption snapshot'ta `StaticText` olarak aşağıda görünür:
- Kullanıcı adı: `StaticText "soztech.ai"`
- Caption: `StaticText "Buradaki promptlar türkçeleştirildi..."` (birden çok LineBreak ile ayrılmış)
- Yorumlar: `StaticText "TEACH"`, `StaticText "Teach"` gibi

## Yorumları Okuma

- "Load more comments" butonu varsa: `browser_click(ref="e...")` ile tıkla
- Yorumlar snapshot'ta kullanıcı adı + yorum metni olarak görünür:
  ```
  link "brk.arrs" → StaticText "brk.arrs"
  link "1h" → time → StaticText "1h"
  StaticText "TEACH"
  ```

## Örnek: @soztech.ai 10 Slaytlı Karusel

| Adım | İşlem | Sonuç |
|------|-------|-------|
| 1 | `browser_navigate(url)` | Sayfa yüklendi, login popup görünüyor |
| 2 | `browser_click(ref="e178")` (Close) | Popup kapandı, slaytlar görünür |
| 3 | `browser_snapshot(full=true)` | Slayt 8-9-10 listitem olarak görünür |
| 4 | `browser_click(ref="e177")` (Go back) ×6 | Slayt 1-2-3'e kadar geri gelindi |
| 5 | Her adımda snapshot al | Tüm slaytların alt text'i toplandı |

**Tespit edilen slaytlar:**
1. Kapak: "CLAUDE'DA SINIRSIZ ÖZEL ÖĞRETMEN MODU"
2. Kod tabanı denetleme prompt'u
3. Hata ayıklama mühendisi prompt'u
4. Performans optimizasyon mühendisi prompt'u
5. Kod mimarisi yeniden inşa prompt'u
6. Startup backend sistem tasarımı prompt'u
7. Frontend mühendisi prompt'u
8. AI Teknik Lider Modu prompt'u
9. Üretim Güvenlik Denetimi prompt'u
10. DevOps Dağıtım Mühendisi prompt'u

## Pitfall: Slaytlar DOM'da Sabit Kalıyor

Instagram karusel slaytları DOM'da **tüm slaytlar aynı anda** yüklenir. "Next"/"Go back" sadece hangi 3'lü grubun göründüğünü değiştirir. Yani:
- Slayt 1 ve Slayt 10 aynı anda DOM'da var
- Herhangi birine tıklayıp büyük görünümde inceleyebilirsin
- "Go back" ile başa döndüğünde tekrar snapshot almana gerek yok — tüm slaytlar zaten orijinal snapshot'ta listitem olarak duruyor olabilir

## Pitfall: img_index Parametresi

Linkte `?img_index=9` varsa, o slayda odaklanmak istendiğini gösterir. Browser bu parametreyle o slaydı açmaya çalışır ama Instagram her zaman saygı duymaz. Önce "Go back" ile başa dön, sonra sırayla "Next" ile ilerle.
