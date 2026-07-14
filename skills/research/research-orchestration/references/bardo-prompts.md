# Bardo Research Project — Prompt Templates (2026-05-24)

Exact prompts used for the 4-phase Bardo marketing research. Use as templates for similar research projects.

---

## Faz 1: Pazar & Strateji Araştırması

```
# Bardo Psychology - Faz 1: Dijital Pazarlama & Strateji Araştırması

Türkiye'de bir psikolog/psikolojik danışmanlık ofisi için dijital pazarlama stratejileri araştırması yap.

## Araştırma Başlıkları:

1. **Türkiye'de psikologlar için dijital pazarlama:** Hangi kanallar gerçekten işe yarıyor?
2. **Platformların gerçek değeri:** Danışan yönlendirme platformları mantıklı mı?
3. **Niş odaklı pazarlama stratejileri:** Spesifik nişlerde Google Ads ve SEO
4. **Bütçe dostu pazarlama taktikleri:** Sıfır/düşük bütçeyle görünürlük
5. **Rakip analizi yaklaşımları:** Yerel rekabet analizi

## Talimatlar:
- Her konu başlığı için 3-5 somut bulgu topla
- Türkçe kaynaklara öncelik ver
- delegate_task kullanarak paralel araştırma yap
- Bulguları ~/research_bardo/faz1_pazar_strateji.md dosyasına kaydet
- En altta "Öne Çıkan İçgörüler" bölümü ekle
```

## Faz 2: Teknik Derin Dalış

```
# Bardo Psychology - Faz 2: Google Ads & AI Otomasyon Araştırması

## Araştırma Başlıkları:
1. **GitHub'da Google Ads otomasyon repoları** (en az 5 repo)
2. **Google Ads API ile neler mümkün**
3. **Psikologlar için Google Ads best practice'leri**
4. **AI + Google Ads entegrasyon örnekleri**
5. **Google Ads panelini öğrenme kısayolları**

## Talimatlar:
- GitHub repoları için yıldız sayısı, son güncelleme, ana özellikleri belirt
- Bulguları ~/research_bardo/faz2_googleads_ai.md dosyasına kaydet
- "En Umut Verici GitHub Repoları (Top 3)" bölümü ekle
```

## Faz 3: Alternatif Kanallar

```
# Bardo Psychology - Faz 3: Alternatif Kanallar & SEO Araştırması

## Araştırma Başlıkları:
1. **SEO stratejileri (yerel & içerik)**
2. **Google Business Profile optimizasyonu**
3. **İçerik pazarlaması** (blog, podcast, video)
4. **Ücretsiz/düşük bütçeli görünürlük taktikleri**
5. **Sosyal medya algoritma stratejileri** + n8n teşhisi

## Talimatlar:
- Bulguları ~/research_bardo/faz3_alternatif_kanallar.md dosyasına kaydet
- "n8n Neden Çalışmadı? Teşhis" bölümü ekle
```

## Faz 4: Sentez & Teslimat

```
# Bardo Psychology - Faz 4: Nihai Strateji Raporu

### ADIM 1: Tüm faz dosyalarını oku
### ADIM 2: Nihai raporu oluştur
Rapor başlıkları:
1. Yönetici Özeti
2. Mevcut Durum Analizi
3. Önerilen Strateji (Kademeli: kısa/orta/uzun vadeli)
4. Google Ads AI Otomasyonu Yol Haritası
5. Beklenen Maliyet & ROI Tablosu
6. Aksiyon Planı (İlk 7 Gün)
7. Riskler & Kaçınılması Gerekenler

### ADIM 3: Raporu Telegram'a gönder
- Türkçe, sıcak ve net dil
- "Edel için Bardo Strateji Raporu hazır ☕" ile başla
```

## Cron Job Yapılandırması

| Faz | schedule | deliver | enabled_toolsets |
|-----|----------|---------|------------------|
| 1   | 1m       | local   | web,terminal,file,delegation |
| 2   | 40m      | local   | web,terminal,file,delegation |
| 3   | 80m      | local   | web,terminal,file,delegation |
| 4   | 180m     | origin  | terminal,file,delegation |

Not: Faz 4'te `web` toolset'i kaldırıldı çünkü sadece dosya okuma + sentez yapıyor.
