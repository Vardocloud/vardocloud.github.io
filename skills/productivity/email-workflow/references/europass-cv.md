# Europass CV Oluşturma Rehberi

## Ne Zaman Kullanılır
Akademik başvurular (YL, doktora), iş başvuruları, hocalara referans talebi.

## Kaynak Veri
- LinkedIn profili (PDF çıktısı) — **uyarı:** PDF her zaman tüm bölümleri içermez
- Transkript
- Edel'in sözlü olarak paylaştığı ek bilgiler

## Europass CV Bölümleri (Sırasıyla)

1. **Personal Information** — İsim, lokasyon, telefon, email, LinkedIn URL, varsa website
2. **Work Experience** — Tarih sırası ters (en yeni en üstte), her pozisyon için:
   - Kurum adı, pozisyon, tarih aralığı
   - 3-5 bullet point ile sorumluluklar ve başarılar
3. **Education** — En son mezuniyet en üstte
4. **Certifications** — Sertifika adı, kurum
5. **Language Skills** — Tablo formatında (CEFR seviyeleri)
6. **Digital Skills** — Kategorilere ayrılmış (Data, AI, Therapy Tech, Productivity, Research)
7. **Additional Information** — CV'ye sığmayan ama değerli bilgiler

## PITFALL: LinkedIn PDF Eksik Bölümler (17 Haziran 2026)

LinkedIn'den "Save to PDF" ile alınan çıktıda şu bölümler eksik çıkabilir:
- Projects
- Volunteer
- Recommendations
- Courses (LinkedIn Learning)

**Çözüm:** Edel'den tam profil çıktısı iste. Veya LinkedIn profiline tarayıcıdan erişip kontrol et.
Ancak **LinkedIn scraping zordur** — web_extract LinkedIn'i desteklemez, puppeteer login duvarı gösterir, CDP 9222'deki Chrome'da da LinkedIn cookie'si yoksa login gerekir.

**Fallback:** Edel manuel olarak eksik bölümleri söyler veya LinkedIn'den bölüm bölüm kopyalar.

## GPA Stratejisi
- Düşük GPA'yı CV'de belirtmek zorunlu değil (transkriptte zaten görünür)
- CV'de GPA yazılacaksa sadece son dönem değil, kümülatif CGPA yaz
- SOP'ta GPA'yı savunma — sessiz geç
