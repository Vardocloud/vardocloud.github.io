# Cron Haber Farkındalığı — Hızlı Başvuru

## Neden?
Edel "haberde yazmışsın" dedi — kronik bir hatayı düzeltiyor. Bundle Gündem cron'u
günde 3 kez (06:15, 10:15, 16:15) haber toplar. Vanitas bu haberleri bilmeden
konuşursa, Edel'in bildiği şeyleri kaçırmış olur → güven kaybı.

## Hangi Cron İşleri?

| Cron | Job ID | Sıklık | Ne Toplar? |
|------|--------|--------|------------|
| Bundle Gündem İşleme | `93582f1545d2` | 06:15, 10:15, 16:15 (UTC+3) | Haberler, gündem, bilim |
| Günlük Sentez | `3ef33fe37449` | 23:00 (UTC+3) | Günün tüm çıktılarının sentezi |

## Hızlı Kontrol (Edel soru sorduğunda)

```bash
# 1. Son Bundle çıktısını bul
ls -lt ~/.hermes/cron/output/93582f1545d2/ | head -5

# 2. Son 60 satırı oku (Response bölümü sonda)
tail -60 ~/.hermes/cron/output/93582f1545d2/2026-06-11_10-23-53.md

# 3. Konuyla ilgili keyword ara
grep -i "kuantum\|quantum" ~/.hermes/cron/output/93582f1545d2/2026-06-11_10-23-53.md

# 4. Günlük Sentez için de aynı
ls -lt ~/.hermes/cron/output/3ef33fe37449/ | head -5
```

## Dosya Yapısı

Cron output dosyaları çok büyük olabilir (1000-5000+ satır).
- İlk kısım: skill prompt'u (önemsiz, geç)
- Son kısım: Response (asıl içerik — `tail -60` ile oku)
- Response formatı genelde markdown başlıkları + madde listeleri

## Ne Zaman Kontrol Et

- Edel bilim/haber/gündem sorduğunda → **her zaman kontrol et**
- Edel "X konusunda ne biliyorsun?" dediğinde → **önce cron, sonra kendi bilgin**
- Edel kısaca "kuantum" gibi bir kelime söylediğinde → **şüphelen, cron'da haber olabilir**
- Edel'in sorusu normal bilginin ötesindeyse → **cron'u kontrol et**

## Ne Zaman KONTROL ETME

- Kişisel/duygusal konular (nasılsın, ne yaptın, vs.)
- Edel'in kendi hayatıyla ilgili sorular
- Zaten bildiğin güncel bilgiler (bugünün tarihi, vs.)

## Doğal Kullanım

Haber buldun → cevabın içinde doğal geçir:

> "Stuttgart Üniversitesi'ndeki kuantum noktası deneyiyle ilgili okumuştum,
> iki foton arasında %70+ başarıyla iletişim kurmuşlar. Kuantum internet
> için büyük adım. Ama temel prensip şöyle işliyor:..."

Uzun uzun "Bundle'da şu haberi gördüm" deme. Haberi cevabın içinde erit.

## Pitfall: Job ID Değişebilir

Cron job ID'leri bir noktada değişebilir (Bundle ID `4cb28605521c` → `93582f1545d2`
değişmişti). Her seferinde `cronjob(action='list')` ile doğrula.
