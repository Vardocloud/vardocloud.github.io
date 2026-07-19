# Session Index Kullanım Formatı

## Nerede?
- Dosya: `~/wiki/references/session-index.md`
- Oluşturan: Edel (19 Tem 2026)
- Amaç: FTS5 tokenizer'ın ıskaladığı önemli konuşmaları manuel indekslemek

## Neden Gerekli?
`session_search` FTS5 index'i bazı sorguları yakalayamıyor (tokenizer sınırlaması).
Özellikle Türkçe kelimeler, birleşik ifadeler veya nadir terimler içeren konuşmalar
FTS5'te görünmez olabiliyor.

Bu indeks, session ID ile doğrudan erişim sağlar — FTS5'e bağımlılığı ortadan kaldırır.

## Format

```markdown
## N. Başlık

- **etiket1, etiket2, etiket3** → `session_id` (tarih, N mesaj)
  - *Detay:* Kısa açıklama
  - *Session title:* orijinal_session_adı
```

## Ne Zaman Ekle?

Aşağıdaki durumlardan HERHANGİ BİRİ gerçekleştiğinde:

1. `session_search` önemli bir konuşmayı bulamadıysa
2. Edel "bu konuyu daha önce konuşmuştuk" dedi ve session_search boş döndüyse
3. Edel önemli bir karar/plan/vizyon paylaştıysa (kimlik, lokal PC, güvenlik, strateji)
4. SQLite fallback ile bulunan ama session_search'ün ıskaladığı konuşmalar

## Nasıl Kullan?

```bash
# Önce indeksi oku
read_file(path="~/wiki/references/session-index.md")

# Etiketlerle eşleşen session ID'yi bul

# Doğrudan session ID ile oku
session_search(session_id="20260711_123750_3bff2c24")
```

## Mevcut İndeks (19 Tem 2026 itibarıyla)

| # | Konu | Session ID |
|---|------|-----------|
| 1 | Kimlik derinleştirme, SOUL.md, lokal PC, karanlık ikiz | `20260711_123750_3bff2c24` |
| 2 | Oracle → Lokal PC geçiş düzeltmesi | `20260712_105103_b00a60c7` |
| 3 | HP EliteBook 2730p tamir, dokunmatik ekran | `20260719_132501_ce344774` |
| 4 | Google OAuth & Himalaya IMAP fallback | `20260719_111311_71653a76` |
| 5 | LinkedIn duplicate post bug | `20260719_100932_b688deec` |
| 6 | DeepSeek V4 Flash model boyutu | `20260719_015501_9f4f6b53` |
| 7 | Klinik Psikoloji YL başvuruları | `20260625_113612_c4bfd8b9` |

## Önemli Noktalar

- Session ID'ler **state.db**'deki gerçek kayıtlardır — değişmez
- İndekse eklenen konuşmalar silinmez (referans bütünlüğü)
- Aynı anda hem session-index.md'ye hem de SIN #3 protokolüne uy (SQLite fallback yap)
- Yeni önemli konuşma tespit edildiğinde indeksi güncelle
