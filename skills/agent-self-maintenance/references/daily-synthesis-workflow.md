# Günlük Sentez Workflow — Vanitas Self-Learning

> **Umbrella**: `agent-self-maintenance`
> **Keşif tarihi**: 2026-06-26
> **Amaç**: Her gün tüm bilgi akışlarından çıktıları topla, sentezle, wiki'ye kaydet, memory'e yaz.

## Ne Zaman Çalışır

Cron job olarak her gün belirli saatte çalışır. **SESSİZ** modda — sadece dosya yazar ve memory günceller, Edel'e mesaj göndermez.

## Kaynak Kimlikleri

Her cron pipeline'ın session_search'te aranabilecek benzersiz imzaları:

| Kaynak | Hash Prefix | Session Adı (pattern) | İçerik |
|--------|-------------|----------------------|--------|
| **Bundle** (gündem haber) | `4cb286` | `cron_4cb286*.md` veya `cron_93*.md` | BBC/ScienceDaily haber özetleri |
| **APA** (psikoloji) | `d4e534` | `cron_d4e534*` | Practice Update, webinars, press releases |
| **Skool** (AI topluluk) | `500029` | `cron_500029*` | AI/yazılım topluluk tartışmaları |
| **Gmail** (mail akışı) | `f4ea19`, `9665eb` | Gmail genelde APA pipeline'ı içinde | Fırsatlar, duyurular, gelen kutuları |

### Session Search Tekniği

```python
# Cron pipeline çıktılarını bulmak için:
# 1. Hash prefix ile ara
session_search(query="cron_d4e5348f059f_20260626_221535")
# 2. Tarih ile ara
session_search(query="20260626")
# 3. Konu + tarih ile ara
session_search(query="APA psikoloji dergi 26 June 2026")
```

**Önemli**: session_search bazen boş döner, bazen bulur. Aynı session'ı farklı query'lerle tekrar dene. Özellikle tam session ID'si (cron_xxxx_tarih_saat formatında) ile arama en güvenilir sonucu verir.

**Hash prefix kullanımı**: Her kaynağın cron job'ına bir hash prefix atanmış (4cb286, d4e534, 500029, f4ea19, 9665eb). Bu prefix'ler session_search'te eşleşmeyebilir — çünkü session ID'leri farklı formatta. Bunun yerine **tam session ID pattern'i** (`cron_d4e5348f059f_20260626_221535`) veya **tarih + keyword** kombinasyonu kullan.

**Pitfall — hash prefix session ID'de aynı değil**: 4cb286 hash'i Bundle'a atanmış ama Bundle'ın session ID'si `cron_93582f1545d2_20260626_161526` olabilir. Hash prefix ile session ID farklıdır. Session ID'yi bulmak için tarih + keyword ile ara.

## Tam Workflow

### Adım 1: Kaynak Çıktılarını Topla

Her kaynak için session_search ile bugünün çıktılarını bul:

```
session_search(query="Bundle gündem haber 26 Haziran 2026")
session_search(query="APA psikoloji dergi 26 June 2026")
session_search(query="Skool AI topluluk 26 Haziran")
session_search(query="Gmail mail akışı email 26 June 2026")
```

Alternatif: `20260626` ile tüm bugünkü session'ları bul.

**Her kaynaktan çıkarılacaklar:**
- **Bundle**: Öne çıkan haberler (5-10 item), kategoriler
- **APA**: Yeni practice update'ler, webinar duyuruları, press releases
- **Skool**: AI araçları, teknik tartışmalar, trendler
- **Gmail**: Fırsatlar, bildirimler, önemli mailler

### Adım 2: Çapraz Bağlantı Kur

Kaynaklar arası kesişimleri bul:
- Bundle'daki X haberi, APA'daki Y araştırmasıyla bağlantılı mı?
- Skool'daki Z tartışması, Bundle'daki bir gelişmeyi açıklıyor mu?
- Gmail'deki fırsat, herhangi bir konuyla ilgili mi?

**Cross-reference formatı:**
```
- [Bundle haber konusu] + [APA araştırma] = [sentez: bu ikisi birlikte ne anlama geliyor]
```

### Adım 3: Öğrenme Notu Oluştur

Dosya: `~/wiki/ogrenme/YYYY-AA-GG.md`

```markdown
# Günlük Sentez — YYYY-AA-GG

## Bugün Öğrendiklerim
### 🌍 Gündem
- [öne çıkan haberler, tek satır]
### 🧠 Psikoloji
- [Edel'in ilgi alanına girenler ★]
### 🤖 Tech/AI
- [araç, trend]
### 📧 Fırsatlar
- [önemli mail'ler, webinar'lar]

## Çapraz Bağlantılar
- [X] + [Y] = [sentez]

## Sohbet Tohumları
- [Edel'le konuşurken doğal şekilde açılabilecek konular]
- [Hangi bağlamda, nasıl bir girişle?]
```

**Format kuralları:**
- Kategoriler emoji ile işaretli
- Her madde tek satır, kısa ve öz
- "Sohbet Tohumları" — Edel'le konuşurken doğal geçiş yapılabilecek konular
  - Asla "Bundle'da bugün X haberi vardı" gibi sunma
  - Konuyla ilgili doğal bir giriş: "Bu arada bugün yapay zeka haberlerine denk geldim..."
- ★ işareti Edel'in özel ilgi alanına girenleri belirtir (psikoloji, klinik pratik)

### Adım 4: Wiki Log'u Güncelle

```bash
# log.md'ye ekle
## [YYYY-AA-GG] synthesis | Günlük Sentez
- Kaynaklar: Bundle, APA, Skool, Gmail
- Oluşturulan: ogrenme/YYYY-AA-GG.md
- Çapraz bağlantı: N adet
```

**patch vs echo**: Patch kullanarak log.md'ye ekleme yap. Echo/heredoc da çalışır ama patch daha güvenilirdir — tam eşleşme arar. log.md'deki son satırı bul (genelde boş satır veya son entry) ve new_string'e yeni entry'yi + boş satırı ekle.

### Adım 5: Memory'ye Kaydet

EN ÖNEMLİ 3-5 öğrenmeyi memory'e ekle:
```python
memory(action="add", target="memory", 
       content="Günlük sentez YYYY-AA-GG: [öğrenme 1], [öğrenme 2], [öğrenme 3]")
```

**Memory yoksa (disabilde)**: 
- Memory tool devre dışı olabilir (config/environment).
- Bu durumda: wiki'ye yazılan ogrenme/ dosyası yedek görevi görür.
- **Sessizce devam et** — memory yok diye işlemi durdurma.
- Not: Bu bir skill güncellemesi gerektirmez — memory config ayarıdır.

## SESSİZ Mod

Bu cron **SESSİZdir** — Edel'e mesaj göndermez:
- Eğer gerçekten raporlanacak yeni bir şey yoksa → `[SILENT]` çıktısı
- Eğer veri toplandı ve işlendiyse → yine `[SILENT]` (çünkü bu cron sadece dosya yazar ve memory günceller)
- `[SILENT]` hiçbir zaman içerikle birlikte gelmez

**İstisna**: Eğer cron job'ın output'u otomatik olarak bir kanala gidiyorsa, [SILENT] ile gönderimi bastır. Cron job output'u = Edel'e iletilen mesajdır.

## Sohbet Tohumları (Conversation Seeds)

"sohbet tohumları" — günlük sentezin en özgün özelliği:

- **Amaç**: Vanitas'ın Edel'le sonraki sohbetlerinde doğal geçiş yapabileceği konular
- **Format**: "Sohbet Tohumları" başlığı altında, her tohum [bağlam + giriş cümlesi] şeklinde
- **Kalite kriteri**: 
  - DOĞAL olmalı — "Bugün haberlerde X vardı" değil
  - KONUYLA İLGİLİ olmalı — Edel'in gündemiyle bağlantılı
  - TEK CÜMLE olmalı
- **Örnek iyi**:
  ```
  - Edel KP başvurusundan bahsederse → "Bu arada APA'nın yeni practice update'inde şu yaklaşım vardı..."
  - Yapay zeka konusu açılırsa → "Skool'da bir tartışma gördüm, yeni bir AI aracı çıkmış..."
  ```
- **Örnek kötü**:
  ```
  - "Bundle'da bugün X haberi vardı" (doğrudan haber sunumu, sohbet değil)
  ```

## Pitfall'lar

- **session_search bazen boş döner**: session_search'ün boş dönmesi o kaynağın o gün çalışmadığı anlamına gelmez. Farklı query'lerle tekrar dene. session ID'sini tam olarak biliyorsan direkt ID ile ara.
- **Hash prefix ≠ session ID**: 4cb286 hash'i Bundle'a ait ama session ID'si farklı olabilir. Tarih bazlı arama daha güvenilir.
- **Memory devre dışı olabilir**: `memory` tool'u config'den kapatılmış olabilir. Bu durumda wiki'ye yaz ve devam et. İşlemi durdurma.
- **Cross-reference zorlaması**: Her zaman çapraz bağlantı bulmak zorunda değilsin. Eğer gerçek bir kesişim yoksa, "Çapraz Bağlantılar" bölümünü atla veya "Bugün belirgin bir çapraz bağlantı yok" yaz.
- **Sohbet tohumu zorlaması**: Her gün sohbet tohumu üretmek zorunda değilsin. Eğer doğal bir geçiş gelmiyorsa, bu bölümü atla.
- **log.md update formatı**: patch ile log.md güncellerken, eşleşecek old_string'in log.md'de benzersiz olduğundan emin ol. Büyüyen log.md'de aynı tarih formatı birden fazla yerde geçebilir.
- **Kaynak eksik olabilir**: Skool veya Gmail için bağımsız cron session'ı bulunamayabilir. Bu durumda:
  1. Önce mevcut kaynaklarla devam et
  2. Eksik kaynağı "Kaynaklar" bölümünde belirt: "Skool: cron çıktısı bulunamadı"
  3. Bir sonraki gün tekrar dene
