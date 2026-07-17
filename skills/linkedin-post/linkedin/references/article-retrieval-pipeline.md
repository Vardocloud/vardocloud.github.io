# APA Makale Edinme Pipeline'ı

APA kaynaklı içerik üretimi (LinkedIn post, blog) için önce makalelerin **tam metin** olarak elde edilmesi gerekir. Bu doküman, email tracking linklerinden başlayarak PsycNET full text'e kadar olan pipeline'ı açıklar.

## Akış

```
APA Email (IMAP) → Tracking Linkler → curl -sI -L ile Çözümle
    → APA Login (BW şifre) → PsycNET Full Text → Wiki Kaydı
```

## 1. APA Email'lerine Erişim (IMAP)

Himalaya CLI, Gmail App Password ile yapılandırılmıştır:

```bash
# Config: ~/.config/himalaya/config.toml
# Password: ~/.config/himalaya/gmail_pass (App Password)
# Hesap: isimgorulsunn@gmail.com

# APA email'lerini listele
himalaya envelope list --account gmail from "apa.org" order by date

# Email içeriğini oku (tracking linkler için)
himalaya message read <ID> --account gmail

# Raw email export
himalaya message export <ID> --account gmail
```

**Not:** Himalaya App Password (`uazv jjlh ceba xksj`) Google hesabı için oluşturulmuş kalıcı bir şifredir. Gmail OAuth token'ı expired olsa bile IMAP çalışır.

## 2. Tracking Link Çözümleme

APA email'lerindeki linkler `click.info.apa.org/?qs=...` formatındadır. Bunlar tracking linkleridir ve asıl URL'ye yönlendirir:

```bash
# Tracking linki çöz
curl -sI -L --max-redirs 5 "https://click.info.apa.org/?qs=..." | grep -i "^location:"
```

**Beklenen hedefler:**
- `psycnet.apa.org/fulltext/<id>.html` → APA dergi makaleleri (login gerekir)
- `psycnet.apa.org/fulltext/<id>.pdf` → PDF versiyonu
- `www.apa.org/topics/...` → APA genel sayfaları (public, login gerekmez)
- `convention.apa.org/...` → APA Convention sayfaları (public)
- `www.apa.org/education-career/ce/...` → CE webinarları (public)
- Dış haber siteleri (CNN, CNBC, Forbes) → APA Media Watch bülteni

## 3. APA Login (Bitwarden)

APA üyelik bilgileri Bitwarden Password Manager'da "APA" adıyla saklıdır:

```bash
# 1. BWS'den master password al
export BW_PW=$(~/.hermes/bin/bws secret list | python3 -c "
import json,sys
data = json.load(sys.stdin)
for s in data:
    if s['key'] == 'BW_MASTER_PASSWORD':
        print(s['value'], end='')
")

# 2. BW unlock
SESSION_KEY=$(~/.hermes/bin/bw unlock --passwordenv BW_PW --raw 2>&1)
unset BW_PW

# 3. APA şifresini çek
APA_DATA=$(BW_SESSION="$SESSION_KEY" ~/.hermes/bin/bw list items --search "APA")
# username: isimgorulsunn@gmail.com
# password: APA SSO şifresi
# URI: https://sso.apa.org/apasso/idm/apalogin
```

**APA login URL:** `https://sso.apa.org/apasso/idm/apalogin?ERIGHTS_TARGET=https://www.apa.org`
- Kullanıcı adı: `isimgorulsunn@gmail.com`
- Şifre: Bitwarden "APA" item'indeki password
- Login sonrası sağ üstte "Vatinas Reister" yazar (Edel'in APA profili)

**Alternatif — Google ile login:** APA SSO sayfasında "Log in with Google" butonu da vardır. Google hesabı ile login daha hızlı olabilir.

## 4. PsycNET Full Text Erişimi

APA login yapıldıktan sonra browser cookie'leri sayesinde PsycNET'teki makalelere tam metin erişimi sağlanır.

**Full text HTML URL patterni:**
```
https://psycnet.apa.org/fulltext/<ID>.html
```

**PDF URL patterni:**
```
https://psycnet.apa.org/fulltext/<ID>.pdf
```

**Record sayfası (abstract + metadata):**
```
https://psycnet.apa.org/record/<ID>
```

Record sayfasında "PDF" ve "Full Text HTML" butonları login sonrası aktif olur.

**Makale metnini çekme:**
Browser JavaScript ile sayfa içeriğini al:
```javascript
// HTML sayfasındaki makale metnini al
let article = document.querySelector('main') || document.querySelector('.full-text-content');
article.innerText
```

PDF'i browser'da açıp MarkItDown ile dönüştür:
```bash
# Önce PDF'i indir (browser ile), sonra işle
skill_view(name='markitdown-mcp')
mcp_markitdown_convert_file path=/tmp/article.pdf
```

## 5. Editor's Choice Makaleleri (Email #564 — 9 Temmuz 2026)

Bu email'de 4 PsycNET makalesi gelir:
1. `2027-37562-001` — "Before the war: Minority stress on Palestinian Muslim women" (Translational Issues in Psychological Science, Jun 2026)
2. `2027-91146-001` — (içerik bilinmiyor)
3. `2027-92882-001` — (içerik bilinmiyor)
4. `2027-47688-001` — (içerik bilinmiyor)

## 6. Public APA Sayfaları (Login Gerekmez)

Bazı APA sayfaları herkese açıktır:
- `www.apa.org/topics/...` — APA topic sayfaları
- `www.apa.org/events/...` — Etkinlik sayfaları
- `www.apa.org/education-career/ce/...` — CE webinarları
- `convention.apa.org/...` — Convention içeriği

Bunlara login olmadan web_extract veya browser ile erişilebilir.

## 7. Wiki'ye Kaydetme

Makaleler `~/wiki/apa-articles/` altına tarih ve başlıkla kaydedilir:

```
~/wiki/apa-articles/2026-07-09-psycnet-before-the-war-minority-stress.md
```

**İçerik şablonu:**
```markdown
# Başlık

**Kaynak:** APA PsycArticles, [DOI linki]
**Tarih:** Yayın tarihi
**Erişim:** Tam metin (APA üyeliği ile)

## Abstract

[Abstract metni]

## Method

[Method bölümü]

## Results / Discussion

[Results ve Discussion]

## References

[Varsa referanslar]
```

## Önemli Uyarılar

1. **PsycNET makalelerine login olmadan erişilmez** — 403 Forbidden döner
2. **APA email'leri sadece 14 gün görünür** — IMAP'te silinmez ama eski email'leri archive yapabilir
3. **APA Media Watch bülteni dış kaynaklara yönlendirir** (CNN, CNBC, Forbes) — bunlar APA'ya ait değildir, ayrıca işlenir
4. **Tracking linkleri zaman aşımına uğrayabilir** — email gönderildikten sonra ~30 gün geçerlidir
