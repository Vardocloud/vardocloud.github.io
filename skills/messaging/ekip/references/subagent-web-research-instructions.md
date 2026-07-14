# Subagent Web Araştırması Talimat Yazma Kuralları (24 Haz 2026)

Alt ajanlar (delegate_task) web araştırmasında sistematik halüsinasyon üretir: snippet'tan çıkarım yapar, boşlukları uydurarak doldurur, Instagram/blog'u kaynak sanar.

## Kötü Talimat → Uydurma

```
❌ "Ege Bölgesi'nde klinik psikoloji araştır"
-> Üniversite adı geçen her yeri "program var" diye raporlar
-> Gerçek başvuru sayfasına bakmaz
-> Instagram'daki eski bir gönderiyi "resmi kaynak" sanar
```

## İyi Talimat → Doğru Sonuç

```
✅ SADECE şu 2 URL'yi aç:
1) https://sbe.deu.edu.tr/duyurular/...
2) https://sosyalbilimler.ikcu.edu.tr/...

2026-2027 GÜZ ilanında Klinik Psikoloji geçiyor mu bak.
HER BİLGİNİN YANINA LİNK KOY.
Varsayım YAPMA. Görmediysen 'BULUNAMADI' yaz.
Instagram, blog, psikolojiarsiv.com gibi kaynakları KULLANMA.
```

## Zorunlu Talimat Bileşenleri

1. **DAR KAPSAM:** 2-3 spesifik URL ver, "araştır" deme
2. **TEK GÖREV:** "2026-2027 Güz ilanında KP var mı" gibi net bir soru
3. **KAYNAK KISITI:** "SADECE resmi sayfa, Instagram/blog KULLANMA"
4. **LİNK ZORUNLULUĞU:** "HER BİLGİNİN YANINA LİNK KOY"
5. **VARSAYIM YASAĞI:** "Varsayım yapma, görmediysen BULUNAMADI yaz"
6. **DOĞRULAMA ŞARTI:** "Alt ajan çıktısını önce kendin kontrol et, sonra Edel'e sun"

## Test Edilmiş Şablon

```
SADECE şu [sayfa] URL'yi aç. [spesifik görev] kontrol et.
HER BİLGİNİN YANINA LİNK KOY.
Varsayım YAPMA. Görmediysen 'BULUNAMADI' yaz.
[YASAKLI KAYNAKLARI] kullanma.
```

## Kategorik Yasaklı Kaynaklar

- Instagram, Facebook, Twitter/X gönderileri
- Blog siteleri (psikolojiarsiv.com, yetiskinterapisti.com vb.)
- 3. parti toplayıcı siteler (hotcourses, educations.com)
- 1 yıldan eski sayfalar
