---
name: apa-referenced-content
description: "APA kaynaklı içerik üretimi — LinkedIn post, blog, podcast. Spesifik referans kullanımı, makale tamamından beslenme, infographic görsel üretimi."
version: 2.1.0
metadata:
  hermes:
    tags: [apa, linkedin, content, psychology, writing]
    category: linkedin-post
---

# APA Kaynaklı İçerik Üretimi

APA (American Psychological Association) kaynaklarından beslenen içerik üretimi için workflow ve kurallar.

## Kullanım

Bu skill, APA makalelerinden içerik üretirken uygulanması gereken kuralları ve workflow'u tanımlar:

1. LinkedIn postları (500-750 karakter, Hakan Türkçapar üslubu)
2. Blog yazıları (1500-2000 karakter)
3. Podcast script'leri (10 dakika)

## ⚠️ ZORUNLU KURALLAR

### 1. Spesifik APA Referans
"APA'nın araştırmasına göre" gibi genel ifadeler **KESİNLİKLE YASAK**. Bunun yerine:

| Yanlış | Doğru |
|--------|-------|
| "APA'nın araştırmasına göre..." | "Hertenstein ve arkadaşlarının 2019'da Sleep Medicine Reviews'da yayımladığı meta-analize göre..." |
| "Bilimsel çalışmalar gösteriyor ki..." | "APA Monitor on Psychology'nin Haziran 2026 sayısındaki 'Sharenting' yazısı..." |
| "Araştırmalar diyor ki..." | "Blom ve ekibinin 2017'de Sleep dergisinde gösterdiği gibi..." |

**Format:** Yazar(lar) ve ark., Yıl, Dergi Adı

### 2. Makalenin Tamamından Beslen
Sadece giriş bölümüne takılıp kalma. Makalenin TÜM bölümlerinden beslen:
- Giriş / Arka plan
- Mekanizmalar (stres-uyku döngüsü, ödül sistemi, duygusal reaktivite)
- İstatistikler ve veriler
- Tedavi yöntemleri
- Klinisyen çıkarımları
- Özel popülasyonlar

### 3. Rakam ve İstatistik Kullan
Makalede geçen somut rakamları kullan:
- "Tek bir uykusuz gece bile sistemik inflamasyonu tetikliyor"
- "%73'ü depresif belirtiler gösteriyordu, CPAP sonrası sadece %4"
- "100'den fazla randomize kontrollü çalışma"

## LinkedIn Post Formatı (AKTİF)

### Yazım Stili: Hakan Türkçapar
Akademik altyapılı ama günlük dilden, sıcak, samimi, okuyucuyu zorlamayan, bilgiyi sohbet havasında veren bir anlatım. Karmaşık psikoloji kavramlarını herkesin anlayabileceği şekilde sadeleştir. Otoriter değil, "birlikte düşünelim" havasında olsun.

### Post Yapısı (6 Katman — ZORUNLU AKIŞ)
```
1. Vurucu giriş       — 1 cümle, okuyucuyu içine çeken
2. APA kaynak         — "APA Monitor on Psychology'nin X sayısındaki 'Y' yazısı"
3. Yani / çıkarım     — "Yani..." ile kaynağı yorumla
4. Araştırma detayı   — Spesifik atıf: "Yazar ve ark., YIL, DERGİ"
5. Dahası / ek detay  — "Dahası..." ile bağlanan ikincil bulgu
6. Vurucu kapanış     — "Bu demek oluyor ki..." / "Belki..." ile biten son
```

**Örnek (uyku post'u):**
> Uyku dediğimiz şey, sandığımızdan çok daha fazlası.
> 
> APA Monitor on Psychology'nin Haziran 2026 sayısındaki "The New Science of Sleep" yazısı, uyku ile ruh sağlığı arasındaki ilişkinin çift yönlü olduğunu net bir şekilde ortaya koyuyor.
> 
> Yani uyku bozukluğu çoğu zaman psikolojik bir sorunun sonucu değil — bizzat onun habercisi.
> 
> Hertenstein ve arkadaşlarının 2019'da Sleep Medicine Reviews'ta yayımladığı meta-analiz bunu doğruluyor: insomniya; depresyon, anksiyete, alkol bağımlılığı ve hatta psikoz için anlamlı bir öngörücü.
> 
> Dahası, tek bir uykusuz gece bile duygusal regülasyonumuzu — özellikle amigdala tepkilerimizi — belirgin şekilde zayıflatıyor.
> 
> Bu demek oluyor ki uykuyu iyileştirmek sadece bir konfor meselesi değil, ruh sağlığına müdahalenin ta kendisi.

### Kurallar
- Dil: **Türkçe**, doğal sohbet havası
- Uzunluk: **500-750 karakter**
- **Hashtag KULLANMA** — hiç ekleme
- Hitap: **doğrudan anlatım** (ne "sen" ne "siz" — direkt anlat)
- KISA paragraflar (maks 1-2 cümle)
- Doğal bağlaçlar: "Yani...", "Dahası...", "Bu demek oluyor ki..."
- Referanslar APA formatında: "Yazar ve ark., YIL, DERGİ"

### YASAKLAR
- ❌ Emoji
- ❌ Hashtag
- ❌ #terapi veya "terapi" kelimesi
- ❌ CTA/soru ("ne düşünüyorsun?", "yorumlarda buluşalım")
- ❌ Genel referans (\"APA'nın araştırmasına göre\")
- ❌ "siz" hitabı

### Edel'in Ağzından Yazma
Post "Edel'in ağzından" yazılacaksa AI tell'lerinden kaçın. Doğal: "emanet ettim", "hoşuma gitti", "Yani ne bileyim". Yasak: "üstleniyor", "cabası", "Kısacası". Özellik listesi değil, kişisel deneyim olarak anlat.

## Workflow

### 0. KAYNAK VE KONU TEKRAR KONTROLÜ (ZORUNLU — atlanmaz!)
Yazmaya başlamadan ÖNCE iki seviyeli kontrol yap:

**Seviye 1 — Kaynak URL kontrolü:** `~/.hermes/data/linkedin_posts.json` dosyasını oku. Bu makalenin kaynak URL'si veya başlığı daha önce kullanılmış mı? Kullanılmışsa farklı bir makale seç.

**Seviye 2 — Konu kontrolü:** `session_search` ile konu adını ara. Kullanılmış bir konuyu tekrarlama.

⚠️ **"En son düzenlenen dosyayı bul" yaklaşımı kısır döngü yaratır** — aynı makale defalarca işlenir. Bunun yerine linkedin_posts.json'daki kayıtlarla çapraz kontrol yap.

### 1. KAYNAĞI OKU
`~/wiki/apa-articles/` altındaki ilgili .md dosyasını oku. Makalenin TÜM bölümlerinden beslen.

### 2. POSTU YAZ (6 Katmanlı Yapı)
Yukarıdaki 6 katmanlı yapıyı takip et. İlk taslak genellikle 1000+ çıkar — bu normal, kısalt ve akışı düzelt.

### 3. KARAKTER SAYISINI KONTROL ET (ZORUNLU)
```python
print(f'Karakter sayısı: {len(post)}')
```
750'yi aşıyorsa kısalt. 500'ün altındaysa genişlet. İlk taslakla ASLA gitme.

### 4. KONTROL ET
Yasaklı kelimeler, emoji, CTA, genel referans, "sen"/"siz" hitabı kontrolü.

### 5. ÇIKTI VER
Post metnini Edel'e sun. Onay al. Onaylanırsa LinkedIn'de paylaş.

## Tuzaklar

### Karakter Sınırı Aşımı
İlk taslaklar genellikle 1000+ karakter çıkar. **Her zaman** `len(post)` ile kontrol et. Gereksiz bağlaçları ve tekrar eden ifadeleri kısalt.

### Konu Tekrarı
Edel, daha önce işlenmiş bir konuyu tekrarlanmasını REDDEDER. Yazmadan önce `session_search` kontrolü ZORUNLU.

### Bağlam Kopukluğu (Sığ Yazı)
Post sığ kalıyorsa ("sığ kalmış", "bağlamı kopuk") sebebi genelde 6 katmanlı yapının eksik uygulanmasıdır. Özellikle "Yani" (katman 3) ve "Dahası" (katman 5) katmanları atlanır. Her seferinde 6 katmanı da kontrol et.

### "En Son Düzenlenen Dosya" Kısır Döngüsü
Cron job prompt'larında `~/wiki/apa-articles/` içinde "en son düzenlenen dosyayı bul" talimatı, aynı APA makalesinin her cron çalıştığında tekrar seçilmesine yol açar. Sonuç: aynı post defalarca üretilir.

**Çözüm:** Prompt'ta "en son düzenlenen" YERİNE "daha önce post yazılmamış (linkedin_posts.json'da kaydı olmayan) bir makale seç" kullan. Kaynak takibini `~/.hermes/data/linkedin_posts.json` ve `linkedin_posts_archive.json` üzerinden yap. `status: posted` veya `status: pending_approval` kayıtlarında source_url'si geçen makaleleri atla.

**Cron job prompt'ları skill'den bağımsız yaşar** — skill'i güncellemek cron prompt'unu güncellemez. Her güncellemede İKİ cron job'un (sabah + akşam) prompt'larını ayrıca güncelle.

### Pollinations API Key Hatası
`mcp_pollinations_generateText` "Authentication failed" dönerse postu kendin yaz.

## Cron Job Prompt Tasarımı

### Kural: Kaynak Seçiminde "En Son" KULLANMA
Cron prompt'ında "en son düzenlenen dosyayı bul" YERİNE:
- "daha önce post yazılmamış bir makale seç"
- Kaynak URL'sini `linkedin_posts.json`'da ara, kullanılmışsa atla
- `read_file(path='~/.hermes/data/linkedin_posts.json')` ile mevcut postları kontrol et

### Cron Job Prompt Şablonu

Model: `gpt-5.4-mini` / `custom:Pollinations`
enabled_toolsets: `["terminal", "web", "file", "search", "delegation"]`

### ⚠️ Cron Prompt'ları Skill'den Bağımsızdır
Skill güncellendiğinde cron prompt'ları otomatik güncellenmez. İKİ cron job'un (sabah + akşam) prompt'larını AYRI AYRI güncelle:
```bash
cronjob(action='update', job_id='272dc0178605', prompt='# LinkedIn Sabah Postu ...')
cronjob(action='update', job_id='79aa6f693b23', prompt='# LinkedIn Akşam Postu ...')
```
Prompt güncellemesi yaparken kaynak seçim mantığını da güncellemeyi unutma.
