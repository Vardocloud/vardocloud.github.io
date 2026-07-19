# Laptop Parça Kurtarma Rehberi

Eski/arızalı laptopları sökerken hangi parçaların başka işlerde kullanılabileceğine dair referans.

**Tarih:** 19 Temmuz 2026 (HP EliteBook 2730p tamir seansından)

---

## Kurtarılmaya Değer Parçalar (Öncelik Sırası)

### 1. Adaptör (⭐ En değerli)
- Aynı voltaj (genelde 19V) ve yeterli amperli her laptopta kullanılır
- Konektör uyumluluğunu kontrol et
- HP adaptörler genelde diğer HP modellerle uyumlu

### 2. RAM (DDR2/DDR3 SODIMM)
- Aynı nesil (DDR2, DDR3) ve aynı pin sayılı (200-pin, 204-pin) laptopta çalışır
- Hız otomatik düşer (ör: 800MHz RAM 533MHz'de çalışır)
- DDR2 SODIMM: 2008-2010 arası laptoplar
- DDR3 SODIMM: 2010-2015 arası laptoplar

### 3. HDD/SSD
- **2.5" SATA**: Standart, USB kutusuyla harici disk yapılabilir
- **1.8" Micro SATA**: Sadece HP 2530P/2730P, IBM X300/X301, Dell XT1 gibi özel modellerde
- **mSATA / M.2**: Daha modern, adaptörle kullanılabilir
- USB kutusu maliyeti: 50-80 TL

### 4. LCD Panel (Harici Monitör)
- Panelin arkasındaki model numarasını bul (örn: SU-12W18A-04X)
- Aliexpress'te "`model no` + LVDS controller board" diye ara
- **LVDS kontrolcü kart maliyeti**: 300-500 TL
- Dokunmatik panel için ayrı USB touch kontrolcü gerekir
- Wacom EMR kalem digitizer'ı **kullanılamaz** (özel kontrolcü piyasada yok)
- Kullanım alanları: Raspberry Pi ekranı, duvar dashboard'u, taşınabilir monitör

### 5. Webcam (⭐⭐⭐)
- Çoğu laptop webcam'i **USB bağlantılıdır**
- 4-6 telli ribbon kablo → USB pinout bul → harici USB webcam
- DIY Perks YouTube kanalında "laptop webcam to USB" videosu var
- Raspberry Pi ile kullanılabilir

### 6. Parmak İzi Okuyucu (⭐⭐⭐)
- Çoğu laptop parmak izi okuyucusu **USB bağlantılıdır**
- USB pinout bul → harici USB fingerprint reader
- Windows Hello ile kullanılabilir
- Hackaday'de "USB keyboard mod to add fingerprint reader" projesi var

### 7. Soğutma Fanı (⭐⭐)
- 5V ise USB'ye bağlayıp mini masa fanı yapılabilir
- 12V ise harici güç kaynağıyla çalışır
- PWM kontrollü ise Arduino ile hız kontrolü yapılabilir

### 8. Hoparlörler (⭐⭐)
- Küçük DIY ses projelerinde kullanılabilir
- Empedansı düşük (4-8Ω), Arduino/ESP32 ile sürülebilir

### 9. BIOS Pili (CR2032) (⭐)
- Standart pil, her anakartta kullanılır
- Konektör farklı olabilir — lehimle değiştirilebilir

---

## Kurtarılmaya DEĞMEYEN Parçalar

| Parça | Neden |
|-------|-------|
| Anakart | Modele özel, başka işe yaramaz. Altın çıkarma pratik değil. |
| CPU (lehimli) | Anakartla entegre, sökülemez |
| GPU (lehimli) | Anakartla entegre |
| Klavye | Özel ribbon konektör, kullanımı çok zor |
| Touchpad | Özel konektör + sürücü |
| WiFi kartı | Eski standart, PCIe adaptörle bile düşük performans |
| Bluetooth modülü | Çok düşük güç, pratik değil |
| Soğutucu (heat pipe) | CPU/GPU'ya özel, başka işe yaramaz |
| ExpressCard/PC Card | Ölü standart |
| Menteşeler | Sadece mekanik projelerde |

---

## Söküm Sırası (Önem Sırası)

1. Adaptör (laptop dışında zaten)
2. RAM (genelde alt kapakta kolay erişim)
3. HDD/SSD (alt kapakta)
4. BIOS pili (alt kapakta)
5. LCD panel (çerçeveyi sök)
6. Webcam (LCD çerçevesinin üstünde)
7. Parmak izi okuyucu (palmrest altında)
8. Fan (anakart sökümü gerekir)
9. Hoparlörler (kasa içinde)

---

## Kaynaklar

- DIY Perks: "How to Convert Laptop Webcams to USB Webcams" (YouTube)
- Hackaday: "USB keyboard mod to add fingerprint reader"
- Reddit r/HomeAssistant: Duvar dashboard projeleri
- LVDS kontrolcü: Aliexpress "LCD controller board + model number"
