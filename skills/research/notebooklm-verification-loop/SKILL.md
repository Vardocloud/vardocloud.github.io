---
name: notebooklm-verification-loop
description: "NotebookLM + LLM doğrulama döngüsü — kaynak besle → LLM analiz → doğrulama sorgula → kaynağa geri dön → final üretim. @mert_durmazer workflow'undan esinlenmiştir."
version: 1.1.0
tags:
  - notebooklm
  - verification
  - research
  - writing
  - anti-hallucination
---

# NotebookLM + LLM Verification Loop

**⚠️ GEREKLİLİK — NotebookLM MCP Hermes'e Kayıtlı Olmalıdır**  
Bu workflow, NotebookLM MCP araçlarına (`source_add`, `notebook_query`, vb.) erişim gerektirir. NotebookLM MCP, Hermes config.yaml'deki `mcp_servers` bölümünde kayıtlı olmalıdır.

**🔍 ADIM 0 — MCP Sağlık Kontrolü (Pre-flight)**

Workflow'a başlamadan önce MCP araçlarının gerçekten çalıştığını doğrula. **healthcheck tool'u güvenilir değildir** — navigation testi kullan.

**⚠️ MCP Server Auth Limitation:** `mcp_notebooklm_chat_with_notebook()` başarısız olup `mcp_notebooklm_navigate_to_notebook()` başarılıysa bu beklenen bir limitation'dır. notebooklm-mcp v2.0.11'in undetected_chromedriver'ı Selenium add_cookie ile cookie enjekte edemez (redirect → domain mismatch loop). Bu verification loop'u etkilemez — Adım 1-3 hala çalışır (NotebookLM'den sentez alınabilir). Alternatif query için `skill_view('cdp-notebooklm')` kullan.  
Workflow'a başlamadan önce MCP araçlarının gerçekten çalıştığını doğrula. **healthcheck tool'u güvenilir değildir** — navigation testi kullan:

```python
# 1. Tool'lar görünüyor mu? (session'da mcp_notebooklm_* var mı?)
# Varsa devam et, yoksa skill_view('notebooklm-mcp') ile setup yap

# 2. Navigation testi (en güvenilir auth kontrolü)
mcp_notebooklm_navigate_to_notebook(notebook_id="<bildiğin bir notebook ID>")
# ✅ success → auth çalışıyor, devam et
# ❌ failure → auth sorunu, VNC'den manuel re-login yap

# 3. Chat testi (browser driver kontrolü)
mcp_notebooklm_chat_with_notebook(message="test")
# ✅ success → MCP tam çalışır durumda
# ❌ "Not authenticated or browser not ready" → navigation çalışıyorsa
#    auth değil driver sorunu. MCP subprocess'i restart et.
```

**Tool prefix notu:** MCP araçları `mcp_notebooklm_` prefix'i ile gelir (örn. `mcp_notebooklm_source_add`), `mcp_notebooklm_mcp_` değil. Server adı config'de `notebooklm` olduğu için prefix bu şekilde oluşur.

**Kontrol et:** Aktif session'da MCP tool'ları (`mcp_notebooklm_source_add`, `mcp_notebooklm_notebook_query`, vb.) görünüyor mu?
- Görünüyorsa ve navigation testi geçtiyse → devam et
- Görünüyorsa ama navigation başarısızsa → auth sorunu, çöz
- Görünmüyorsa → ÖNCE `skill_view(name='notebooklm-mcp')` ile setup talimatlarını izle, MCP'yi Hermes'e kaydet, gateway restart yap, yeni session başlat

**Kaynak:** Instagram @mert_durmazer (Temmuz 2026)
**Mantık:** NotebookLM kaynağa sadık kalır (halüsinasyon yapmaz) ama yazma/akıl yürütme yeteneği sınırlıdır. LLM'ler mükemmel yazar/analizcidir ama kaynağa bağlı kalmaz. İkisini döngüye sok = güvenilir araştırma.

## Ne Zaman Kullanılır

- Akademik/APA makalesi analizi yaparken
- LinkedIn postu için kaynak doğrulama gerektiğinde
- NotebookLM'deki kaynaklardan derinlemesine içgörü çıkarmak için
- Halüsinasyon riskini minimize etmek için
- Uzun araştırma notlarını yapılandırılmış yazıya dönüştürürken

## 4 Adımlık Workflow

```
┌─────────────────────────────────────────────────────────┐
│               NOTEBOOKLM + LLM VERIFICATION LOOP         │
├──────────┬──────────┬──────────┬──────────┬──────────────┤
│  Adım 1  │  Adım 2  │  Adım 3  │  Adım 4  │              │
│  Besle   │  Analiz  │ Doğrula  │  Üret    │  ← Döngü     │
│          │          │          │          │              │
│ Notebook │   LLM    │ LLM→NB   │   LLM    │   3→1→2→3    │
│  LM      │ (Zenmux) │ (MCP)    │ (Zenmux) │  tekrarla    │
└──────────┴──────────┴──────────┴──────────┴──────────────┘
```

---

## Adım 1: NotebookLM'i Besle ve Sentezlet

**Amaç:** Ham kaynakları NotebookLM'e yükle, kaynağa sadık bir sentez çıkart.

**Yapılacaklar:**
- Kaynakları NotebookLM MCP ile ekle (`mcp_notebooklm_source_add`)
- Notebook sorgula (`mcp_notebooklm_source_query` veya `mcp_notebooklm_notebook_query`)
- İstek: "Şu kaynaklara dayanarak, her iddiayı kaynak göstererek bir sentez çıkart. Sadece kaynaklardaki bilgileri kullan, kendi bilgini ekleme."

**Çıktı:** Kaynak-gösterimli sentez metni (NotebookLM'in kaynağa sadık çıktısı)

---

## Adım 2: Sentezi LLM'e Getir ve Analiz Ettir

**Amaç:** NotebookLM'in sentezini LLM (Zenmux/Qwen3.7-Plus) ile analiz et — kıyasla, çelişkileri bul, yapılandır, çerçeve oluştur.

**Prompt şablonu:**
```
Sana bir araştırma sentezi veriyorum. Şunları yap:
1. Ana temaları çıkar
2. Çelişkili noktaları işaretle (varsa)
3. Boşlukları belirt (kaynakta olmayan bilgiler)
4. Bir yapı/çerçeve öner (makale, thread, post için)
5. Kıyasla: farklı kaynaklar aynı şeyi mi söylüyor?

SENTEZ:
[sentez metni]
```

**Çıktı:** Yapılandırılmış analiz + çerçeve önerisi

---

## Adım 3: "Ne Doğrulanmalı?" — Doğrulama Döngüsü (KRİTİK)

**Amaç:** LLM'in analizindeki iddiaları NotebookLM kaynaklarına geri götürerek doğrula. Bu adım, akıl yürütme ile dayanak arasındaki döngüyü kapatır.

**LLM'e sor:**
```
Analizindeki her ana iddia için "Bu iddia NotebookLM kaynaklarında doğrulanabiliyor mu?" diye işaretle.
- ✅ Kaynak destekli: hangi kaynak?
- ⚠️ Kısmi destek: hangi kısmı eksik?
- ❌ Kaynak yok: bu iddia kaynaklarda yok
- 🤔 Yorum: bu senin çıkarımın mı?
```

**NotebookLM'e geri götür:**
```
mcp_notebooklm_source_query(query="[doğrulanacak iddia]")
```
- ❌ işaretli iddiaları NotebookLM'de sorgula
- ⚠️ işaretlilerin eksik kısımlarını sorgula
- ✅ işaretlileri olduğu gibi bırak

**Çıktı:** Her iddianın doğruluk durumu (kaynak referanslı)

---

## Adım 4: Final Sürümü LLM Yazsın

**Amaç:** Doğrulanmış bilgilerle final metni üret.

**Prompt:**
```
Doğrulanmış iddiaları kullanarak şu formatta bir metin yaz: [makale/thread/post/rapor]

Kurallar:
- Sadece ✅ (kaynak destekli) iddiaları kullan
- ⚠️ (kısmi) iddiaları "şu kaynağa göre..." diyerek kullan
- ❌ (kaynağız) iddiaları KULLANMA
- 🤔 (yorum) varsa "benim yorumum:" diyerek ayır
- Her iddianın sonunda kaynak göster
```

---

## Döngü Tekrarı (Gerekirse)

Adım 3'te çok fazla ❌ çıkarsa:
- NotebookLM'e yeni kaynak ekle (Adım 1'e dön)
- Tekrar analiz et (Adım 2)
- Tekrar doğrula (Adım 3)

Bu döngü, tüm iddialar ✅ olana kadar devam edebilir.

---

## Kullanım Örneği (LinkedIn Postu)

1. APA makalesini NotebookLM'e ekle → sentez al
2. Sentezi Qwen3.7-Plus'a gönder → analiz et
3. "Ne doğrulanmalı?" sor → iddiaları NotebookLM'de sorgula
4. Doğrulanmış iddialarla LinkedIn postu yaz

## Kullanım Örneği (Akademik Not)

1. Ders kaynaklarını NotebookLM'e yükle
2. LLM ile çalışma soruları üret
3. Her sorunun cevabını NotebookLM kaynaklarında doğrula
4. Doğrulanmış cevaplarla çalışma kartı oluştur

## Araçlar

- **NotebookLM MCP:** `mcp_notebooklm_source_add`, `mcp_notebooklm_source_query`, `mcp_notebooklm_notebook_query` (prefix: `mcp_notebooklm_` — not `mcp_notebooklm_mcp_`; the server name in Hermes config is `notebooklm`, so tools appear as `mcp_notebooklm_<tool_name>`)
- **LLM (Zenmux):** Qwen3.7-Plus veya Gemini 3.1 Flash Lite — `custom:Zenmux` provider üzerinden
- **NotebookLM Studio:** Uzun format üretim için slide_deck (opsiyonel)

## Kaynak

- **Orijinal workflow:** @mert_durmazer Instagram karuseli (27 Haz 2026) — `references/source-mert-durmazer-workflow.md`
