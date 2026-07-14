# Cost-Benefit Evaluation Gate

> **Köken:** Edel, 5 Temmuz 2026 — Meta-prompting audit önerisine karşı çıkış.
> **İlke:** Bir sistem "çalışıyor" olması yetmez — harcadığı kaynağa değmeli.

## Gate Soruları (Her extension için zorunlu)

### 1. Bu sistem ne kadar kaynak harcayacak?
| Kalem | Tahmin |
|-------|--------|
| Kurulum süresi | saat/gün bazında |
| İşletim maliyeti (LLM) | çağrı/hafta × token × $ |
| İşletim maliyeti (infra) | disk, CPU, RAM, API |
| Bakım yükü | güncelleme, hata ayıklama sıklığı |

### 2. Karşılığında ne kazanacağız?
- Şu an sahip olmadığımız hangi bilgi/kabiliyeti veriyor?
- Bu bilgi olmadan ne kaybediyoruz? (ölçülebilir: zaman, para, kalite)
- Bu fayda parayla/time'la ölçülebilir mi?

### 3. Daha basit bir alternatif var mı?
- Mevcut bir sisteme ince bir katman eklemek yeterli mi?
- Sıfırdan sistem yerine tool'a ekleme mi?
- "Şu an nasıl yapıyoruz?" sorusuna cevap: manuel mi, otomatik mi, yok mu?

### 4. Testi geçse bile değer mi?
- İşletim maliyeti < sağladığı fayda? (zorunlu eşik)
- Fayda "iyi olur" seviyesinde mi, "olmazsa olmaz" seviyesinde mi?
- 6 ay sonra hala kullanıyor olacak mıyız?

## Karar Matrisi

| İşletim Maliyeti | Fayda | Karar |
|:----------------:|:-----:|:-----:|
| $0 | Düşük | 🟢 **Kabul** (zarar yok) |
| $0 | Orta | 🟢 **Kabul** |
| $0 | Yüksek | 🟢 **Kabul** |
| Düşük ($) | Yüksek | 🟢 **Kabul** |
| Düşük ($) | Orta | 🟡 **Değerlendir** |
| Düşük ($) | Düşük | 🔴 **Reddet** |
| Yüksek ($$) | Yüksek | 🟡 **Değerlendir** (kritikse) |
| Yüksek ($$) | Orta/Düşük | 🔴 **Reddet** |

## Örnek Kararlar

### ✅ Heartbeat Sistemi (SQLite log)
- Kurulum: ~30 dk
- İşletim: **$0** (SQLite, ek API yok)
- Fayda: Task görünürlüğü + hata takibi
- **Karar: KABUL** — sıfır maliyetle task görünürlüğü kazanıldı

### ❌ Haftalık Skill Audit (Meta-Prompting)
- Kurulum: ~1 saat
- İşletim: ~40 LLM çağrısı/hafta
- Fayda: Skill kalite metrikleri (ama zaten hata anında fark ediyoruz)
- **Karar: REDDET** — çözdüğü problem yok, maliyeti var

### 🟡 Skill Patch Cycle (Hata Anında Structured Müdahale)
- Kurulum: ~15 dk (şablon)
- İşletim: **$0** (sadece hata anında)
- Fayda: Disiplinli hata yönetimi, onay mekanizması
- **Karar: KABUL** — zaten yaptığımızı structured hale getirir, ek maliyet yok

## Dersler

1. **Thin katmanlar önce düşünülür:** Zero-operational-cost eklemeler (heartbeat gibi) heavy sistemlerden önce denenir.
2. **"Çalışıyor" ≠ "Değer":** Bir sistemin testi geçmesi, sisteme girmesi için yeterli değildir. Önce Gate'ten geçmeli.
3. **Operasyonel maliyeti olan her extension Gate'ten geçer:** Haftada 1 kuruş bile harcıyorsa, neden harcadığını açıklayabilmelisin.
4. **Her şeyi otomatikleştirme:** Bazen manuel süreç yeterlidir. Otomasyonun ek maliyeti > manuelin maliyeti ise yapma.
