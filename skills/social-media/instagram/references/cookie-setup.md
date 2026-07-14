# Instagram Cookie Alma

## Chrome'dan Manuel Cookie Export

1. PC'de Chrome ile `instagram.com`'a giriş yap
2. F12 → **Application** sekmesi
3. Sol menü → **Cookies → instagram.com**
4. Tüm cookie'leri seç (Ctrl+A) → kopyala

## Netscape Formatına Çevirme

Kopyalanan cookie'ler şu formatta olmalı:

```
.instagram.com	TRUE	/	FALSE	<expiry>	<name>	<value>
```

Örnek:
```
.instagram.com	TRUE	/	FALSE	1795765260	sessionid	78089668165%3Ad90JZ...
.instagram.com	TRUE	/	FALSE	1795766685	csrftoken	9D3KRgTTqYrmu...
.instagram.com	TRUE	/	FALSE	1785690678	ds_user_id	78089668165
.instagram.com	TRUE	/	FALSE	1785690261	mid	aYEtdQALAAHbng8...
```

## Gerekli Cookie'ler

| Cookie | Zorunlu | Not |
|---|---|---|
| `sessionid` | ✅ | Oturum anahtarı |
| `csrftoken` | ✅ | CSRF koruması için, header'da da kullanılır |
| `ds_user_id` | ✅ | Kullanıcı ID'si |
| `mid` | ✅ | Machine ID |
| `ig_did` | ✅ | Device ID |
| `rur` | ✅ | Rate limiting token'ı |
| `datr` | Önerilen | Browser fingerprint |
| `ps_l`, `ps_n` | Önerilen | Platform session |

## Güvenlik

- Dosya HER ZAMAN chmod 600: `chmod 600 ~/.hermes/instagram_cookies.txt`
- Cookie'leri ASLA log/terminal/chat çıktısında gösterme
- Kullanıcıdan kopyaladıktan hemen sonra chat geçmişini temizleme öner
- Cookie süresi: `sessionid` genelde 6 ay, diğerleri 1-2 yıl
