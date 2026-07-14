# Türk Üniversite Araştırma — Oturum Dersleri (24 Haziran 2026)

## Kritik Pitfall'lar

### 1. Alt Ajanla Araştırma YAPMA
Coder model (north-mini-code-free) araştırma için uygun değildir. Halisünasyon yapar:
- Var olmayan programlar uydurur
- Başvuru tarihlerini yanlış aktarır
- GPA/ALES şartlarını yanlış bildirir

**Çözüm:** Araştırmayı DOĞRUDAN kendin yap. web_search + web_extract + browser ile.
Alt ajan kullanman gerekiyorsa Analist (mimo-v2.5, port 19998) veya deepseek-v4-flash-free (OpenCode Zen) kullan. Asla coder model kullanma.

### 2. Sayfanın Sonunu Atlama
web_extract çıktıyı 5000 karakterde keser. Tezsiz program listeleri, ücretler ve kontenjanlar GENELLİKLE sayfanın EN SONUNDA yer alır.

**Çözüm:** Sayfayı browser ile aç, en aşağı scroll yap, tezsiz tablosunu kontrol et.

### 3. Accordion Menüler
Türk üniversite siteleri sıkça accordion/toggle menü kullanır. web_extract bu menülerin kapalı halini görür, içeriği okumaz.

**Çözüm:** `browser_click` ile her başlığı tıkla, sonra `browser_snapshot` ile içeriği oku.

### 4. Sadece web_extract ile yetinme
SharePoint altyapılı sayfalar (İstanbul Aydın gibi) web_extract ile sadece menü gösterir, içerik göstermez.

**Çözüm:** Browser dene. Olmazsa farklı bir sayfa (PDF, duyuru) bul.

## Halüsinasyonlu Alt Ajan Tespitleri (24 Haz 2026)

Aşağıdaki üniversitelerde alt ajanlar KP olduğunu söyledi ama Edel bizzat kontrol ettiğinde YOKTU:
- Aydın Adnan Menderes Üni. — alt ajan "ilan var" dedi, link çalışmıyor
- Balıkesir Üni. — alt ajan "ilan var" dedi, yok
- Muğla Sıtkı Koçman — alt ajan "ilan var" dedi, yok
- Çukurova Üni. — alt ajan "ilan var" dedi, Edel PDF'i açtı, yok

**Kural:** Alt ajanın söylediği her bilgiyi bizzat doğrula. Edel "görmedim" dediğinde alt ajana değil Edel'e inan.

## Elenen Üniversiteler (Gerekçeleriyle)

### GPA 2.50 Şartı Yüzünden Elenenler (Edel GPA 2.33)
- Işık Üni. — GPA 2.50 (tezsiz dahil)
- İstanbul Kültür Üni. — GPA 2.50
- İstanbul Okan Üni. — GPA 2.50
- Altınbaş Üni. — GPA 2.50
- Nişantaşı Üni. — GPA 2.50
- Yeditepe Üni. — GPA 2.50
- Bahçeşehir Üni. — GPA 2.50
- Marmara Üni. — GPA 2.50
- İstanbul Üni. — GPA 2.50
- Başkent Üni. — GPA 2.50
- Çankaya Üni. — GPA 2.50
- Bursa Uludağ Üni. — Psikoloji YL GPA 2.75

### Başvurusu Bitenler
- Beykoz — 21 Mayıs
- Gedik — mülakatlar Haziran'da yapıldı (1. başvuru süreci bitti)
- Medipol — 15 Nisan
- Ankara Medipol — başvuru bitmiş

### Pahalı Olanlar ( > 1.5M TL)
- Üsküdar — 1.675M tezsiz
- İstanbul Bilgi — 1.88M
- Acıbadem — 1.6M tezli

### Sistemde/İlanda Olmayanlar
- İEÜ — öğrenci sisteminde deneysel psikoloji var, KP yok
- İstanbul Arel — öğrenci sisteminde "Psikoloji" var, "Klinik Psikoloji" yok
- Ege Üni. — bu dönem açılmamış
- İzmir Bakırçay — enstitü sayfası 404
- İzmir Tınaztepe — portalda aktivite yok
- Ankara Üni. — KP doktora var, YL yok
- Hacettepe — KP YL var (10 kişi) ama Edel istemiyor

## Aktif Seçenekler (24 Haz 2026 itibarıyla)

### Beklemede
1. **FSMVÜ** — KP Tezli 700K (%50 ind.), mail atıldı, cevap bekleniyor
2. **DEÜ** — 29 Haziran'da kontenjanlar açıklanacak (EN KRİTİK)

### İletişim Devam Ediyor
3. **York Europe Campus (Selanik)** — €7.900/1 yıl, Stefania Hazna cevap verdi, uyruk+ikamet sordu

## Mail Stratejisi (GPA Muafiyet Talebi)
GPA şartını karşılamayan durumlarda:
- GPA'yı savunma, diğer güçlü yanları öne çıkar
- ALES puanı, iş deneyimi, İngilizce lisans
- "Değerlendirmeye alınabilir miyim?" diye kısa sor
- Akademisyenler kısa mail okur, uzatma
