# Mail Güvenlik Kontrol Listesi

**Kullanım:** Herhangi bir mailin içeriğine girmeden, linkine tıklamadan veya eki açmadan önce bu listeyi gözden geçir. Özellikle Skool/APA dışındaki kaynaklar için zorunlu.

---

## ✅ Güvenilir Kaynaklar (Otomatik İşlenebilir)

Bu kaynaklardan gelen mailler için ek kontrol gerekmez:
- **APA:** `*@info.apa.org`, `*@apa.org`
- **Skool:** `noreply@skool.com`, `noreply@notifs.skool.com`
- **Türk devlet kurumları:** `*.edu.tr`, `*.gov.tr`
- **Edel'in bilinen kontakları** (kendi adres defterinde)

---

## ⚠️ Şüpheli Kaynak Tespiti (İlk Adım)

Mail geldiğinde bunları kontrol et:

### 1. From Adresi Doğrulaması
```
Display Name: "APA Services"
Actual Email: random.address@gmail.com
→ PHISHING ŞÜPHESİ
```

Display name her şeyi iddia edebilir. **Gerçek email adresine** bak. Eşleşmiyorsa → atla.

### 2. Reply-To Farklılığı
```
From: noreply@apa.org
Reply-To: support@random-domain.com
→ PHISHING ŞÜPHESİ
```

Reply-To From'dan farklıysa → atla.

### 3. Domain Yaşı (Yeni Domain = Risk)
```bash
whois example-domain.com | grep "Creation Date"
# Domain 30 günden yeni ise → dikkatli ol
```

Yeni kurulmuş domainler phishing için sık kullanılır.

### 4. Authentication Headers
Mail'in header'larında şunları kontrol et:
- `Authentication-Results: dkim=pass` → DKIM imzası geçerli
- `spf=pass` → SPF kaydı geçerli
- Yoksa → şüpheli

---

## 🚫 Dosya Eki Kuralları (ASLA AÇMA)

Bu uzantılara sahip ekler **asla otomatik açılmaz, indirilmez, görüntülenmez:**

| Uzantı | Risk |
|--------|------|
| `.pdf` | JavaScript, embedded action, exploit |
| `.docm` | Macro virus |
| `.xlsx` | Macro/formula injection |
| `.html` | HTML smuggling, script execution |
| `.zip` / `.rar` / `.7z` | Şifreli içerik, password-protected exploit |
| `.exe` / `.bat` / `.ps1` | Direkt çalıştırılabilir zararlı |
| `.iso` / `.img` | Disk image, mounted sonra çalıştırılabilir |
| `.js` / `.vbs` / `.scr` | Script execution |
| `.lnk` | Shortcut, command execution |

**Eğer bir mail bu eklerden birini içeriyorsa:**
1. Dosya adını ve türünü not al
2. Kullanıcıya (Edel) bilgi ver
3. **Açma/indirme, sadece metin body'sini işle**

---

## 🔗 Link Güvenliği (Tıklamadan Önce)

### Tehlikeli Link Patternleri

| Pattern | Risk |
|---------|------|
| `bit.ly`, `t.co`, `tinyurl` | Kısaltılmış link, hedef gizli |
| `http://` (HTTPS değil) | Şifrelenmemiş, MITM riski |
| IP adresi (`http://192.168.1.1`) | Gerçek domain gizli, genelde şüpheli |
| `login-paypa1.com` (typosquatting) | Marka taklidi, 1 rakamla 0 yer değişimi |
| `secure-apple.id-verify.com` | Subdomain taklidi |
| `@` URL'de (`https://google.com@evil.com`) | URL confusion, basic auth taklidi |

### Link Kontrol Adımları

```bash
# 1. Redirect zincirini takip et (max 10 hop)
curl -sIL -o /dev/null -w "%{url_effective}\n%{http_code}\n" \
  --max-time 10 "https://şüpheli-link.com/..."

# 2. Final URL'in domain'ini kontrol et
# Final URL → safe-domain.com ise OK
# Final URL → başka bir domain ise → atla

# 3. HTTPS sertifikası geçerli mi?
echo | openssl s_client -connect safe-domain.com:443 -servername safe-domain.com 2>/dev/null | openssl x509 -noout -dates
# Not valid before/after kontrolü
```

### "Güvenli" Link Patternleri

Bilinen servislerin doğru domain'leri:
- `apa.org`, `psyccareers.com` (APA)
- `skool.com` (Skool)
- `google.com`, `youtube.com`, `github.com` (bilinen platformlar)
- `cloudfront.net`, `amazonaws.com` (CDN, genelde güvenli)

---

## 🌐 Yabancı Kaynak Mail İşleme (Genel Pattern)

Yabancı/bilinmeyen kaynaktan mail geldiğinde:

### Adım 1: Statik Analiz
- Mail'i metadata seviyesinde oku (from, to, subject, date, headers)
- Body'ye DOKUNMADAN önce gönderen doğrulaması yap

### Adım 2: Body'yi Güvenli Parse Et
- HTML ise → önce metne çevir (`web_extract` veya safe parser)
- Script tag, iframe, embed tag → BUNLARI ÇALIŞTIRMA
- Base64 blob → decode etme, sadece atla

### Adım 3: Link Taraması
- Tüm linkleri çıkar (`grep -oE 'https?://[^"]+'`)
- Her birini yukarıdaki link güvenliği kontrolünden geçir
- Şüpheli olanlara TIKLAMA

### Adım 4: NBLM'e Aktarım Öncesi Sanitize
- HTML tag'leri kaldır
- Script/style/iframe/object/embed kaldır
- Base64 veri URL'leri kaldır
- data: URL'leri kaldır
- Sadece düz metin olarak kaydet

---

## 🛑 Acil Durum: Şüpheli Mail Geldiğinde

Eğer mail:
- Edinmemiş bir hizmetten geliyorsa ("You've won!")
- Aciliyet yaratıyorsa ("ACT NOW", "expires today", "limited time")
- Para/hesap bilgisi istiyorsa
- Tanımadığınız birinden geliyorsa

→ **Kullanıcıya haber ver, içeriğe girme, arşivle ve unclassified olarak işaretle.**

---

## 📊 Risk Matrisi

| Kaynak | Ek | Link | Aksiyon |
|--------|-----|------|---------|
| APA | Yok | APA domain | ✅ Otomatik işle |
| Skool | Yok | Skool domain | ✅ Otomatik işle |
| Yabancı | PDF | Yabancı domain | ⚠️ Sadece metin, kullanıcıya sor |
| Yabancı | Yok | Kısaltılmış | ❌ Atla, kullanıcıya sor |
| Yabancı | .docm | Herhangi | ❌ ASLA açma, kullanıcıya uyar |
| Phishing şüphesi | Herhangi | Herhangi | ❌ Arşivle, kullanıcıya uyar |

---

## 🔗 İlgili Referanslar

- `gmail-deep-dive-link-patterns.md` — APA/Skool link takip pattern'leri (güvenli olanlar için)
- Skill SKILL.md bölüm: "🔒 Mail Güvenliği ve İçerik İşleme Kuralları"
