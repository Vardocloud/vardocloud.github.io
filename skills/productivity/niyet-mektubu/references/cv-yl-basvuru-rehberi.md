# CV Yapımı — YL Başvurusu İçin (Edel'in Notları)

## Kaynak: Claude.ai Analizi (21 Haz 2026)

Edel, referans mektubu ve CV stratejisini Claude.ai'e danıştı. Claude'nin analizi ve
Vanitas'ın uygulaması sonucunda şu prensipler oluştu.

---

## CV'ye Referans Eklemek — GENEL KURAL: EKLEME

### Neden eklenmez?
1. **Uyumsuzluk:** Başvuruya ekli gerçek referans mektupları (akademik hocalardan) ile
   CV'de listelenen referanslar (staj kurumları, HR) birbirini tutmaz. Kabul komitesi
   "asıl güçlü referanslar bunlar değil mi?" sorusunu sorabilir.
2. **İçerik uyumsuzluğu:** Sport Center Academy HR stajı, klinik psikoloji başvurusuyla
   ilgisiz. Akademya Psikoloji ilgili ama bir hoca değil, staj sağlayıcısı.
3. **Modern CV pratiği:** "References available upon request" / referans listesi artık
   çoğu akademik CV rehberinde gereksiz kabul edilir. Başvuru formu zaten referans
   bilgisini ayrı alanda ister.
4. **Ters etki riski:** GPA'nın zayıf olduğu bir dosyada, "en güçlü referansım bir HR
   stajı" gibi algılanabilir.

### İstisna: Elde somut yazılı referans mektubu varsa
Sport Center Academy veya Akademya'dan yazılı referans mektubu varsa ve başvuru
"ek destekleyici belge" kabul ediyorsa, CV'ye değil başvuruya ayrı PDF eki olarak
eklenebilir. Ama her başvuru için gerekip gerekmediği kontrol edilmelidir.

---

## Research Interests — GENEL KURAL: EKLE

### Neden eklenir?
1. Akademik CV'lerde standart bir bölümdür
2. Motivasyon mektubundaki AI/dijital ruh sağlığı temasını CV'de de görünür kılar
3. Zayıflatmaz, güçlendirir
4. Kısa (1-2 satır) olduğu için kalabalık yapmaz

### Örnek format:
```
## RESEARCH INTERESTS
Digital mental health interventions, cognitive behavioral therapy (CBT),
clinical applications of artificial intelligence, neuropsychology
```

---

## Edel'in Mevcut Referansları (CV'ye eklenmeyecek)

| Kaynak | Tip | Klinikle İlgisi |
|--------|-----|-----------------|
| Sport Center Academy | HR stajı (yazılı referans) | ❌ İlgisiz |
| Akademya Psikoloji | Staj sağlayıcı | ⚠️ Kısmen ilgili |
| Institutus | ? | ? (Edel detay vermedi) |

---

## CV Bölüm Sırası (Edel'in Final Yapısı)

1. Personal Information
2. Profile
3. **Research Interests** ← Claude önerisiyle eklendi
4. Work Experience
5. Education & Training
6. Clinical & Research Projects (psikoloji projeleri burada — I/O Psych, nöropsikoloji katılımı, ABCD app)
7. Technology Projects (fine-tuning, RAG, n8n, AI System — LOTR elfçe çıkarıldı)
8. Clinical & Interpersonal Skills
9. Technical Skills
10. Language Skills
11. Certifications & Training
12. Additional Information

---

## Edel'in Çalışma Akışı (Claude.ai + Vanitas)

Edel YL başvurusu için şu hibrit akışı kullanır:
1. **Araştırma/Danışma:** Claude.ai'e sorar (referans mektubu stratejisi, CV formatı)
2. **Sentez/Uygulama:** Claude'nin çıktısını bana (Vanitas) iletir, ben özet çıkarır
   ve uygularım
3. **Onay:** Son halini Edel'e gösteririm, o son rötuşları yapar

Bu akış, Edel'in "Claude'yi araştırma için, Vanitas'ı uygulama için" kullandığını
gösterir. İkisi rekabet değil, tamamlayıcıdır.

---

## Europass CV Formatı (Resmi — 2025 Şablonu)

### Genel Yapı

Europass CV, Avrupa Birliği'nin resmî CV formatıdır. Resmî şablon:
`europass.europa.eu` (online editor) veya DOCX şablonu:
`https://www.eeas.europa.eu/sites/default/files/documents/2025/Annex%203%20Europass-cv-en%20template.docx`

### Format Özellikleri

- **Tek sütunlu** (iki kolonlu DEĞİL — yaygın bir yanlış anlama)
- **Tablo bazlı** düzen (python-docx ile doldurulabilir)
- **Mavi (#2b5797) bölüm başlıkları** — kalın, beyaz yazı, koyu mavi arka plan
- **CEFR dil tablosu** — Listening/Reading/Spoken interaction/Spoken production/Writing kolonları, A1-C2 seviyeleri
- **Kronolojik sıra** — en güncelden eskiye

### Bölüm Sırası

1. **Personal Information** — İsim (büyük), adres, telefon, e-posta, uyruk (tablo formatında)
2. **Work Experience** — Tarih | Pozisyon → Employer → Activities (bullets) → Business sector
3. **Education and Training** — Tarih | Derece → Okul → Detaylar
4. **Personal Skills**
   - **Language skills** — CEFR tablosu (anadil + diğer diller, her beceri için seviye)
   - **Communication skills** — Kutu içinde bullet list
   - **Organisational/managerial skills** — Kutu içinde bullet list
   - **Job-related skills** — Kutu içinde bullet list
   - **Other skills** — Kutu içinde bullet list

### PDF Çıktısı (Vanitas için — Önemli)

**Container'da LibreOffice yok** → DOCX'ten direkt PDF'e çeviremezsin.

**Doğru yöntem: HTML + WeasyPrint**

```python
from weasyprint import HTML
HTML('cv_europass.html').write_pdf('CV_Ad_Soyad_Europass.pdf')
```

**Adımlar:**
1. Europass stilinde HTML hazırla (şablon: `templates/europass-cv.html`)
2. WeasyPrint ile PDF'e çevir (`pip3 install weasyprint`)
3. Her şey tek sayfaya sığmalı (A4 için %65 genişlik yeterli)

**HTML şablon olarak** `templates/europass-cv.html` kullanılır → içine CV verilerini göm, PDF'e çevir.

### Yanlış Yaklaşımlar

- ❌ İki kolonlu tasarım (sol sidebar + sağ içerik) — Europass DEĞİL, özel tasarım
- ❌ DOCX → LibreOffice ile PDF — container'da libreoffice yok, root yetkisi yok
- ❌ python-docx ile resmî şablonu doldurup PDF'e çevirmek — LibreOffice gerekir, çalışmaz
- ✅ HTML + WeasyPrint → doğru ve çalışan yöntem

### WeasyPrint HTML Şablonu

`templates/europass-cv.html` dosyası Europass stilinde hazırlanmış HTML şablonudur.
İçine doğrudan verileri göm (dinamik değil, statik HTML) ve PDF'e çevir.

Önemli CSS sınıfları:
- `.section-header` — mavi arka planlı bölüm başlıkları
- `.entry-date, .entry-title, .entry-org` — iş/eğitim girişleri
- `.lang-table` — CEFR dil tablosu
- `.box` — beceri kutuları (iletişim, organizasyon, vb.)

---

## Kaynaklar

- Claude.ai analizi (21 Haz 2026) — referans mektubu stratejisi
- Stanford Career Education — referans mektubu yapısı
- MIT Drennan Lab — başvuru belgeleri yönetimi
- Politecnico di Milano — referans mektubu formatı
