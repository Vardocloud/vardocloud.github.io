---
name: study-app
description: "Create interactive single-HTML study/practice apps for Edel — flashcards, quizzes, gamification. Content sourced from NotebookLM, delivered as standalone offline HTML files. All practice materials should be delivered as apps: 'Tüm pratikleri böyle app şeklinde yap.'"
version: 1.0.0
author: Vanitas
tags: [html, study, quiz, flashcards, gamification, education, notebooklm, edel-preference]
---

# Study App Builder

Create interactive, visually appealing HTML study applications for Edel's learning workflow.

## Edel's Preferences — MANDATORY
- **Göze hoş görünmeli** — dark tema, canlı renkler (mor/yeşil gradient), modern temiz tasarım
- **Eğlenceli olmalı** — gamification: skor takibi, ilerleme çubuğu, tamamlama badge'i
- **Mobil uyumlu** — telefon ekranında da çalışmalı (@media max-width:480px)
- **Tek dosya** — bağımsız çalışan tek HTML, ek kütüphane/CDN yok, offline çalışır
- **İki bölümlü yapı:** Öğrenme materyali (kartlar) + Alıştırma (quiz)
- **Hedef:** Her çalışma konusu için bir app üret (YAB, PTE, diğer klinik konular)
- **Araştırma:** İnternet/YouTube'dan en iyi uygulama pattern'lerini araştır, entegre et

## Components

### Öğrenme Kartları (📖 Section)
- Her kavram/kriter için ayrı kart (accordion/toggle pattern)
- Renk kodlu letter badge'leri (A=#a78bfa, B=#6ee7b7, C=#fbbf24, D=#f472b6, E=#60a5fa, F=#fb923c)
- Kısa başlık + alt başlık
- Tıklanınca açılan detay içeriği
- Tip/İpucu kutuları (bordered left accent, pastel bg)
- Her kartta ▾ toggle indicator

### Quiz (❓ Section)
- 5 soru, çoktan seçmeli (A/B/C/D)
- Anında feedback: doğru ✅ / yanlış ❌ + açıklama metni
- Seçenekler cevaplanınca disable edilsin (tekrar tıklama yok)
- Doğru şık: yeşil vurgu (#6ee7b7), yanlış seçilen: kırmızı vurgu (#f87171)
- Doğru cevap her zaman gösterilsin (öğretici olsun)

### Skor Takibi (📊 Bar)
- Progress bar (gradient: #a78bfa → #6ee7b7)
- Canlı skor metni "3/5"
- 🔄 Tekrar butonu (quiz'i sıfırla)
- Tüm sorular bitince: completion badge 🎉 + kişiselleştirilmiş mesaj
  - 5/5: "Mükemmel! ✨"
  - 3-4/5: "İyi iş! 👏"
  - 0-2/5: "Tekrar dene 📖"

### Aksiyonlar (Events)
- Tab switching: nav butonlarıyla 📖 / ❓ arası geçiş
- Card toggle: tıklayınca open/close
- Quiz answer: cevaplayınca feedback göster + skor güncelle
- Reset: tüm quiz state'ini sıfırla, kartları kapatma

## CSS Paleti
```css
/* Dark tema core */
body     { background: #0f0f1a; color: #e0e0e0; }
.card    { background: #1a1a2e; border: 1px solid #252540; border-radius: 14px; }
.nav-active { background: #2a2a3a; border-color: #a78bfa; }
.correct { border-color: #6ee7b7; background: #065f4622; color: #6ee7b7; }
.wrong   { border-color: #f87171; background: #7f1d1d22; color: #f87171; }
.gradient-text { background: linear-gradient(135deg,#a78bfa,#6ee7b7); -webkit-background-clip: text; }
.feedback-bg-correct { background: #065f4622; border: 1px solid #6ee7b755; }
.feedback-bg-wrong   { background: #7f1d1d22; border: 1px solid #f8717155; }
```

## JS Pattern
```javascript
// Tab switching
function showTab(tab) { /* hide .section, remove .active from nav buttons */ }

// Card toggle
function toggleCard(el) { el.classList.toggle('open'); }

// Quiz lifecycle
let answered = new Array(quizData.length).fill(false);
let score = 0;

function answer(qIdx, optIdx) {
  if(answered[qIdx]) return;
  answered[qIdx] = true;
  /* disable all option buttons */
  /* highlight correct (green), mark wrong if selected (red) */
  /* show feedback div */
  updateScore();
}

function updateScore() {
  /* update progress bar width */
  /* update score text */
  /* if all answered: show completion badge */
}

function resetQuiz() { /* reinitialize state, re-render */ }
```

## Workflow

### 1. Research Content
- Check NotebookLM for relevant notebooks → `notebook_query(notebook_id, "topic")`
- Topics likely: BDT (256 sources), APA Bilgi (24), PTE Academic notebook
- If no notebook exists or auth stale: `web_search` + `web_extract` for authoritative source
- Extract structured info: lists, definitions, key points, numbered criteria
- For DSM/APA content: BDT notebook has authoritative Turkish DSM-5 translations

### 2. Build App Structure
- **Cards section:** her konsept/kriter için bir kart
- **Quiz section:** 5 soru, derived from card content
- Sorular ezber değil, anlama test etsin
- Her soruya açıklama ekle (neden doğru/yanlış)

### 3. Generate HTML
- `write_file(path, content)` ile tek HTML oluştur
- CSS + JS tamamen inline gömülü
- Background: `~/.hermes/skills/education/study-app/references/` altındaki referans app'leri incele
- Quiz cevaplarını mutlaka doğrula

### 4. Deliver
- `MEDIA:/path/to/file.html` ile Telegram'da native dosya olarak gönder
- Kısa bir kullanım talimatı ekle
- "Nasıl kullanılır: 1. İndir 2. Tarayıcıda aç 3. Çalış"

## NotebookLM Content Integration
- **Birincil kaynak:** NotebookLM'deki mevcut notebook'lar
- Query pattern: `notebook_query(notebook_id, "topic maddeler halinde açıkla")`
- Structured answer'dan kart ve quiz içeriği oluştur
- **Auth stale ise:** Fallback: `web_search` + `web_extract`
- Auth yenileme: `python3 ~/.hermes/scripts/nb_keepalive.py` (auto-heal, BWS+TOTP+CDP)

## Reference Files
- `references/yab-dsm5-study-app.html` — YAB DSM-5 app (2 July 2026, pilot implementation)

## Pitfalls
- **Quiz answers MUST be correct** — DSM/APA kriterlerini yazmadan önce kaynaktan doğrula
- **Mobile first** — 480px altı ekranlarda padding'i 14px'e düşür, font boyutlarını küçült
- **No external dependencies** — CDN, framework, kütüphane yok. Her şey inline.
- **Content accuracy** — Klinik kriterlerde hata kabul edilmez, kaynak göster
- **Telegram delivery** — MEDIA:<path> kullan, send_message ile origin hedefleme çalışmaz
- **Quiz reset** — sadece quiz state'ini sıfırla, kartları kapatma / sekmeyi değiştirme
- **Feedback metinleri** — öğretici olsun, sadece doğru/yanlış demek yerine nedenini açıkla
