# Security Audit Checklist — Paralel Teşhis Akışı

Günlük güvenlik raporu veya "güvenlik önlemlerini kontrol et" talebinde kullanılacak
hızlı paralel teşhis pattern'i. 2-3 turda tam resim.

## Round 1: Kurulu Bileşenler + Firewall (paralel)

```bash
# Üçünü tek terminal komutunda birleştir:
echo "=== PAKETLER ===" && dpkg -l | grep -E 'fail2ban|ufw'
echo "=== IPTABLES ===" && sudo iptables -L INPUT -n --line-numbers | head -30
echo "=== UFW ===" && sudo ufw status verbose
```

**Kontrol noktaları:**
- fail2ban ve ufw paketleri kurulu mu?
- iptables INPUT policy: DROP mu ACCEPT mi?
- UFW active mi? Default policy ne?
- Hangi portlar ALLOW/DENY? 22, 8080, 9119 durumu?

## Round 2: SSH + fail2ban + Portlar + Loglar (paralel)

```bash
echo "=== SSH CONFIG ===" && sudo sshd -T | grep -iE 'permitrootlogin|passwordauth|pubkeyauth|maxauthtries|clientalive|allowusers|usedns|permitemptypasswords'
echo "=== FAIL2BAN ===" && sudo fail2ban-client status sshd
echo "=== LISTENING PORTS ===" && sudo ss -tlnp | grep -E ':(22|80|443|8080|9119|22000) '
echo "=== RECENT AUTH FAILS ===" && sudo journalctl -u ssh --since '1 hour ago' --no-pager | grep -i 'fail' | tail -15
echo "=== BTMP ===" && ls -la /var/log/btmp && echo "size: $(sudo ls -lh /var/log/btmp | awk '{print $5}')" && sudo lastb -n 5
```

**Kontrol noktaları:**
- `sshd -T` ile effective SSH config (sshd_config grep'lemekten iyidir — varsayılanları da gösterir)
- `PasswordAuthentication no` → brute force imkansız
- `PermitRootLogin without-password` → root sadece key ile
- `AllowUsers` → sınırlı kullanıcı listesi
- fail2ban: Currently banned sayısı, Total banned, jail aktif mi?
- btmp: dosya var mı, boyutu, loglama çalışıyor mu?
- Dinleyen portlar: hangi interface'te dinliyor (0.0.0.0 vs localhost vs Tailscale IP)?

## Round 3: Spesifik IP Takibi (ihtiyaç halinde)

```bash
# Raporda belirtilen şüpheli IP'leri tek tek kontrol et
for ip in <IP1> <IP2> <IP3>; do
  echo -n "$ip -> "
  sudo fail2ban-client status sshd 2>/dev/null | grep -q "$ip" && echo "BANNED" || echo "NOT in jail"
done

# Auth log'da iz ara
sudo grep -E '<IP1>|<IP2>' /var/log/auth.log | tail -20

# Son N dakikadaki hatalı SSH denemesi sayısı
sudo journalctl -u ssh --since '30 min ago' --no-pager | grep -c 'Failed password'
```

## Değerlendirme Matrisi

| Katman | Güvenli | Şüpheli | Tehlikeli |
|--------|---------|---------|-----------|
| SSH auth | `PasswordAuthentication no` | — | `yes` + port 22 açık |
| Root login | `without-password` veya `no` | — | `yes` |
| Kullanıcı | `AllowUsers` set | — | tüm kullanıcılar |
| fail2ban | Aktif + banlı IP var | Kurulu ama inaktif | Kurulu değil |
| UFW | Aktif + default deny | — | İnaktif veya kurulu değil |
| btmp | Dosya var, loglanıyor | Dosya var ama boş | Dosya yok |
| Web portları | DENY IN (Tailscale hariç) | — | ALLOW IN Anywhere |
| SSH port | 22 standart | 22 + yüksek deneme | 22 + şifre açık |

## Pitfalls

- **`sshd_config` grep'leme:** Sadece açıkça yazılanları gösterir, varsayılan değerleri kaçırır. `sshd -T` kullan.
- **`lastb` komutu:** btmp dosyası root:utmp izinleriyle gelir (`-rw-rw----`). `sudo` ile çalıştır.
- **fail2ban log sessizliği:** `journalctl -u fail2ban` son 1 saat boş dönebilir — banlanan IP yoksa normaldir, jail boş değil demek değildir (mevcut banlar duruyordur).
- **iptables vs UFW:** UFW, iptables üstüne yazılır. `iptables -L` ile görünen REJECT/DROP kuralları UFW'den gelir. İkisini de kontrol et — UFW "active" görünüp iptables'ta kural eksik olabilir (nadir).
- **Syncthing 22000:** P2P dosya senkronizasyonu için varsayılan port. Dışarıya açık olması normaldir (NAT traversal + cihaz keşfi için gerekli). TLS + cihaz kimlik doğrulaması ile korunur. Config: `~/.local/state/syncthing/config.xml` (Ubuntu'da `~/.config/syncthing/` değil — XDG durum dizini).
