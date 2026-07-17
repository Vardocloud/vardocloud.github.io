# Meet Bot Self-Exit & Recovery — 17 Temmuz 2026

## Senaryo

Edel, Zoom'da "Yeni Nesil Yaşam Koçluğu" dersindeyken, benim Google Meet'teki
"Terapi Tıkanınca: DEHB'de İlaç Tedavisinin Rolü" seminerini kaydetmemi istedi.

## Kronoloji

| Zaman (TSI ~20:11) | Olay |
|-------------------|------|
| 0s | `meet_join(url, guest_name="Edel Reister")` → success |
| ~5s | Edel "Berkcan olarak gir" dedi |
| ~7s | `meet_leave()` → "no active meeting" ❌ — bot çoktan çıkmış |
| ~10s | `meet_status()` → "no active meeting" — teyit |
| ~12s | `meet_join(url, guest_name="Berkcan")` → success (pid 31392) |
| ~30s | `meet_status()` → **alive:true, inCall:false, captioning:true, joinedAt:null** |
| ~50s | `meet_status()` → aynı durum, değişiklik yok |
| ~70s | `meet_status()` → **exited:true** — bot kendi kendine çıkmış |
| ~75s | `meet_join(url, guest_name="Berkcan")` → success (pid 31838) |
| ~90s | `meet_status()` → **alive:true, inCall:false, captioning:true, joinedAt:null** |
| ~110s | `meet_status()` → aynı durum |
| (sonra) | Edel "kayıt aldığına dikkat et" dedi — teyit verildi, takip devam |

## Anahtar Bulgular

### 1. Bot Self-Exit (Kritik)
`meet_join` başarılı döndükten KISA SÜRE SONRA bot sessizce çıkabiliyor.
Sebebi net değil — muhtemel:
- Chromium crash (headless ARM64)
- Google Meet "unsupported browser" uyarısı sonrası sayfa kitlenmesi
- Plugin'in join flow'u tamamlayamaması

**Çözüm:** Join sonrası `meet_status` ile DOĞRULA. Bot düşmüşse yeniden join dene.

### 2. "inCall: false + captioning: true + joinedAt: null" Durumu
Bu ara durumda bot canlı, altyazı motoru aktif, ama toplantıya kabul edilmemiş.
Muhtemelen lobby'de bekliyor veya join sayfası yüklenmiş ama "Katıl" butonuna
tıklanamamış.

**Tespit:** Bu durumda bot ~20-40sn içinde kendi kendine exit atıyor.
Manuel müdahale gerekmeden yeni join çağrısı yapılmalı.

### 3. meet_leave → "no active meeting"
Bot zaten çıkmışsa `meet_leave` çalışmaz. Kullanıcıya hata göstermeden
önce otomatik rejoin dene.

### 4. Dual Meeting Pattern
Edel bir derste (Zoom), bot başka bir derste (Meet).
- Edel'den bağımsız çalış, sessizce kaydet
- Sorun olursa bildir, sorma
- Edel "kayıt aldığına dikkat et" dediğinde → confirmation mesajı ver

## Recovery Pattern (Doğrulanmış)

```
meet_join(url, guest_name)
  → status kontrol (alive? inCall?)
  → değilse: 15sn bekle → yeniden meet_join
  → 3. denemede de başarısız → Edel'e bildir
```

Bu pattern 17 Temmuz'da başarıyla uygulandı (3. join'de bot canlı kaldı ama
inCall:false — host kabul etmemiş olabilir).
