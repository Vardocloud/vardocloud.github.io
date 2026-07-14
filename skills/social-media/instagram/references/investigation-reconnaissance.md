# Instagram Investigation & Reconnaissance

Profil keşfi, burner hesap tespiti, sosyal mühendislik ve bilgi çıkarma taktikleri.

## Burner Hesap Tespiti (Hızlı)

5 işaret → %95 burner hesap:
- `is_private: true`
- `edge_followed_by.count: 0` (sıfır takipçi)
- `edge_follow.count: ≥25` (25+ takip)
- `full_name: ""` (boş isim)
- `biography: ""` (boş bio) + `media_count: 0`

Örnek: minipak3223 — hepsi tuttu.

## Cover Story Tasarımı

**İlkeler:**
- Doğal ama anonim: yüzü kısmen gizleyen fotoğraf (güneş gözlüğü, yan profil)
- Profil adı gerçek isim, kullanıcı adı nötr/yaratıcı (`melkora_` gibi)
- Bio minimal: "İzmir ☕ | müzik 🎧" — çok detay verme
- Takipçi/takip oranı dengeli olsun

**Fotoğraf stratejisi:**
- AI swapped → cilt dokusu, ışık tutarsızlığı, kenar geçişleri AI'ı ele verir
- Pexels gerçek foto → yüzü tamamen görünenler riskli (reverse image search)
- Nanobanana-2 (Pollinations) → en gerçekçi AI seçeneği
- Prompt anahtarları: "candid iphone photo", "amateur snapshot", "natural light", "no makeup", "slightly blurry"

## Elicitation Taktikleri (Bilgi Çıkarma)

Kaynak: NotebookLM "Konuşma Taktikleri" + HUMINT elicitation teknikleri.

### Temel Kurallar
1. ASLA röportaj yapma — moderatör ol
2. Tek soru sor, cevabı bekle, ordan türet
3. "Sence?" formülü — fikrini sor, bilgisini değil
4. Hikaye anlat — önce kendinden kısa bir şey paylaş

### Anlatma İsteğini Tetikleme (The Urge to Correct)
- Yumuşak yanlış tahmin yap: "Sen daha çok gece aktif olan birisin gibi geldi"
- Eksik bırak: "Bende sende iki farklı vibe var, biri ciddi biri de…"
- İnsanlar yanlışı düzeltmek için bilgi verir

### Strategic Pause (Stratejik Sessizlik)
- "Anladım." → BEKLE
- "Hmm, ilginç." → BEKLE
- İnsanlar sessizliği doldurmak için fazladan bilgi verir

### Macro → Micro (Genelden Özele)
- "İnsanlar DM'de neden mesafeli olur sence?" (genel)
- "Sen de öyle misin?" (kişisel)
- "Peki seni rahat ettiren şey ne?" (detay)

### Quid Pro Quo (Karşılıklılık)
- Önce kendinle ilgili zararsız bir şey paylaş
- Karşı taraf da paylaşma ihtiyacı hisseder
- "Ben okulda çalışıyorum, öğrenciler bazen çıldırtıyor 😅 Sen neyle uğraşıyorsun?"

### Deflection (Soruya Soruyla Cevap)
- "Sen nerelisin?" → "İzmirliyim 😊 Peki sen?"
- "Ne iş yapıyorsun?" → "Okulda çalışıyorum. Senin işin ne?"
- Kısa cevap + hemen topu geri at

### "Bot musun?" Yanıtı
- ASLA savunmacı olma
- "Yok ya, insanım :) Sadece biraz düzenli yazıyorum"
- "Keşke bot olsam, daha az uyku sorunum olurdu :)"
- Hemen konuyu değiştir, gül geç

### Güvenlik Notları
- Hedefin bildiği spesifik mekan/isim ASLA ağzından çıkmasın
- Her mesaj öncesi plan yap, onay al
- Bilgiyi sadece o bilgi verdiği ölçüde ver
- Tüm konuşma loglanmalı

## NotebookLM Kaynakları
- "Vanitas Konuşma Taktikleri Notları" (3132361c)
- "YOUTUBE KONUŞMA TAKTİKLERİ TRANSCRİPTLERİ" (0ebd2774)
- Sorgu: `cross_notebook_query("bilgi çıkarma taktikleri", notebook_names="...")`
