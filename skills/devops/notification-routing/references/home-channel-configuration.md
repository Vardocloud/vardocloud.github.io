# Gateway Notification Channel — Home Channel Configuration

Gateway sistem bildirimlerinin (health alert, watchdog uyarısı, hata raporu) nereye gideceğini belirleyen ayar.

## Kavram

Gateway, cron scheduler'dan bağımsız çalışır. Health check sırasında bir servis down olduğunda (ör: Open WebUI, Docker), gateway doğrudan bir uyarı mesajı gönderir. Bu mesajlar cron job değildir — cron listesinde görünmezler.

## Varsayılan Davranış

Kurulumda HOME_CHANNEL kullanıcının Telegram DM'ine (user ID) ayarlanır. Bu nedenle tüm sistem bildirimleri kullanıcının özel sohbetine düşer.

## İstenen Davranış

Sistem bildirimleri bir kanala/topic'e yönlendirilir (ör: güvenlik/sistem kanalı). Böylece DM sadece sohbet için kalır.

## Değişiklik Adımları

1. Yeni hedef kanalın chat_id ve thread_id'sini belirle
2. HOME_CHANNEL ayarını değiştir
3. Gateway'i yeniden başlat

## Etkileri

| Etkilenen | Açıklama |
|:----------|:---------|
| Sistem bildirimleri | ✅ Yeni kanala gider |
| Cron job'lar | ❌ Etkilenmez — kendi `deliver` alanlarını kullanır |
| DM sohbetleri | ❌ Etkilenmez — aktif konuşmalar ayrı yönetilir |
| Topic konuşmaları | ❌ Etkilenmez |

## Doğrulama

Değişiklik sonrası bir sistem bildirimi tetiklenene kadar test etmek zordur. Şu yöntemlerle doğrulanabilir:

1. Yapılandırma dosyasını kontrol et — yeni değer görünüyor mu?
2. Gateway log'unda hata var mı?
3. Bir dahaki health check bildirimini bekle

## Sık Sorulanlar

**S: Cron job'umu da bu ayar etkiler mi?**
C: Hayır. Cron job'lar kendi `deliver` ayarlarını kullanır. HOME_CHANNEL sadece gateway bildirimlerini etkiler.

**S: DM'ime gelen tüm mesajlar kesilir mi?**
C: Hayır. Sadece gateway sistem bildirimleri yön değiştirir. Senin yazdığın mesajlar, benim cevaplarım, cron job çıktıları etkilenmez.

**S: Eski haline nasıl döndürürüm?**
C: Aynı adımlarla eski değeri geri yaz ve gateway'i restart et.
