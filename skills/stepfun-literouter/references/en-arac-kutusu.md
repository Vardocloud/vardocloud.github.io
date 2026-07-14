# LiteRouter Free Models — EN Araç Kutusu (Vanitas için)

> İngilizce görevlerde kullanılacak ücretsiz modeller.
> Tarih: 20 Haziran 2026

---

## 📦 KAPSAM

Bu modeller **Türkçe bilgisi kanıtlanmamış** veya **İngilizce odaklıdır**. 
Vanitas'ın İngilizce gerektiren işlerinde (kod, araştırma, data, yaratıcı yazarlık) kullanılır.

---

## ⚡ KOD & TEKNİK İŞLER

### devstral-small-2507:free (Mistral, 24B)
| Özellik | Değer |
|---|---|
| **Uzmanlık** | Agentic coding |
| **SWE-Bench** | %53.6 (açık modellerde #1) |
| **Uncensored** | ✅ |
| **Kullanım** | Karmaşık GitHub issue çözümü, PR açma, kod refactor |
| **Kaynak** | [Mistral Devstral](https://mistral.ai/news/devstral-2507/) |

### gpt-oss-120b:free (OpenAI, 117B MoE)
| Özellik | Değer |
|---|---|
| **Uzmanlık** | Reasoning + structured output |
| **Seviye** | o4-mini eşdeğeri |
| **JSON hata** | En düşük structured output error rate |
| **Kullanım** | Code review, algoritma analizi, teknik dokümantasyon |
| **Kaynak** | [OpenAI gpt-oss](https://openai.com/index/introducing-gpt-oss/) |

### gpt-oss-20b:free (OpenAI, 21B MoE)
| Özellik | Değer |
|---|---|
| **Uzmanlık** | Edge cihaz, düşük kaynak |
| **RAM** | 16GB ile çalışır |
| **Seviye** | o3-mini eşdeğeri |
| **Kullanım** | Raspberry Pi servisleri, mobil/edge deployment |
| **Kaynak** | [OpenRouter gpt-oss-20b](https://openrouter.ai/openai/gpt-oss-20b/pricing) |

### trinity-mini:free (Arcee AI, 26B MoE — 3B aktif)
| Özellik | Değer |
|---|---|
| **Uzmanlık** | Function calling, multi-step agent |
| **Context** | 131K |
| **ABD yapımı** | ✅ GDPR uyumlu senaryolar |
| **Kullanım** | API zincirleri, otomasyon, veri pipeline |
| **Kaynak** | [Arcee Trinity](https://www.arcee.ai/trinity) |

---

## 🧠 ARAŞTIRMA & ANALİZ

### grok-4.1-fast-reasoning:free (xAI)
| Özellik | Değer |
|---|---|
| **Uzmanlık** | Uzun doküman, çok adımlı ajan |
| **Context** | **2M token** (en geniş) |
| **Tool calling** | Agentic #1 |
| **Reasoning** | Açılıp kapanabilir |
| **Kullanım** | Kitap analizi, repo-wide refactor, büyük log analizi |
| **Kaynak** | [xAI Structured Outputs](https://docs.x.ai/developers/model-capabilities/text/structured-outputs) |

### owl-alpha:free:full-context (OpenRouter)
| Özellik | Değer |
|---|---|
| **Uzmanlık** | Full-context agentic |
| **Context** | **1M token** (full-context free) |
| **JSON hata** | %0.34 structured output error |
| **Claude Code uyumu** | ✅ |
| **Kullanım** | Uzun süreli ajan oturumları, Claude Code entegrasyonu, büyük projeler |
| **Kaynak** | [OpenRouter Owl Alpha](https://openrouter.ai/openrouter/owl-alpha) |

### openrouter:free:full-context
| Özellik | Değer |
|---|---|
| **Uzmanlık** | 25 free model arasında oto-routing |
| **Akıllı filtre** | Tool calling, structured output, vision ihtiyacına göre seçim |
| **Kullanım** | "Hangi model iyi bilmiyorum, sen karar ver" durumları |

---

## 🎭 YARATICI YAZARLIK & STORYTELLING

### mythomax-l2-13b:free (Gryphe, 13B)
| Özellik | Değer |
|---|---|
| **Uzmanlık** | Roleplay, storytelling |
| **Context** | 4K |
| **Öne çıkan** | "En iyi roleplay modellerinden biri" |
| **Kullanım** | NPC diyalogları, interaktif hikaye, karakter yazımı |
| **Kaynak** | [OpenRouter MythoMax](https://openrouter.ai/gryphe/mythomax-l2-13b) |

### l3-8b-lunaris:free (Sao10K, 8B)
| Özellik | Değer |
|---|---|
| **Uzmanlık** | Generalist + RP dengesi |
| **Context** | 8K |
| **Öne çıkan** | "Birden çok modelin stratejik merge'i" |
| **Kullanım** | Yaratıcı yazarlık, sosyal medya içeriği, beyin fırtınası |
| **Kaynak** | [OpenRouter L3 Lunaris](https://openrouter.ai/sao10k/l3-lunaris-8b/api) |

---

## ⚡ HIZLI API & GERÇEK ZAMAN

### mistral-small-24b-instruct-2501:free (Mistral, 24B)
| Özellik | Değer |
|---|---|
| **Uzmanlık** | Hızlı yanıt, instruction following |
| **Hız** | **150 t/s** |
| **Çok dilli** | 12+ dil (EN/FR/DE/ES/IT) |
| **Kullanım** | Gerçek zamanlı EN sohbet, API entegrasyon, günlük asistan |
| **Kaynak** | [Mistral Small 3](https://mistral.ai/news/mistral-small-3/) |

### llama-3.1-8b-instruct-turbo:free (Meta, 8B)
| Özellik | Değer |
|---|---|
| **Uzmanlık** | Hızlı, geniş context |
| **Context** | 131K |
| **Uncensored** | ✅ |
| **Kullanım** | Sansürsüz EN içerik, uzun context gerektiren hızlı işler |

### llama-3.3-70b-instruct-turbo:free (Meta, 70B)
| Özellik | Değer |
|---|---|
| **Uzmanlık** | En büyük model, structured output %0 hata |
| **Context** | 131K |
| **Çok dilli** | 8 dil (EN/DE/FR/IT/PT/HI/ES/TH) |
| **Kullanım** | Hataya tahammülü olmayan JSON çıktısı, kritik doğruluk gereken görevler |
| **Kaynak** | [OpenRouter Llama 3.3](https://openrouter.ai/meta-llama/llama-3.3-70b-instruct) |

---

## 🧩 KÜÇÜK & ÖZEL GÖREVLER

### ministral-3b-2512:free (Mistral, 3B)
| Özellik | Değer |
|---|---|
| **Uzmanlık** | En küçük, vision |
| **Context** | 128K |
| **Kullanım** | Mobil görsel+metin, düşük kaynaklı sınıflandırma |

### llama-3.2-3b-instruct:free (Meta, 3B)
| Özellik | Değer |
|---|---|
| **Uzmanlık** | En küçük Llama |
| **Context** | 131K |
| **Hız** | 143 t/s |
| **Kullanım** | Basit sınıflandırma, hızlı etiketleme, regex alternatifi |

### mistral-nemo-instruct-2407:free (Mistral+Nvidia, 12B)
| Özellik | Değer |
|---|---|
| **Uzmanlık** | Nvidia GPU optimizasyonu |
| **Context** | 128K |
| **Kullanım** | Nvidia altyapısında çalışan EN servisler |

---

## 🎯 KARAR AĞACI (EN İŞLERİ İÇİN)

```
Görev ne?
├─ Kod yazma/onarım
│  ├─ Karmaşık → devstral-small-2507
│  └─ Basit → gpt-oss-20b veya llama-3.1-8b
│
├─ Araştırma/analiz
│  ├─ Uzun doküman (>500K token) → grok-4.1-fast veya owl-alpha
│  ├─ JSON çıktısı kritik → gpt-oss-120b
│  └─ Hızlı özet → mistral-small-24b
│
├─ Yaratıcı yazarlık
│  ├─ Roleplay → mythomax-l2-13b
│  └─ Genel yaratıcı → l3-8b-lunaris
│
├─ API/tool çağrısı
│  ├─ Çok adımlı → trinity-mini
│  └─ Tek çağrı, hızlı → mistral-small-24b
│
└─ Sınıflandırma/etiketleme
   └─ llama-3.2-3b veya ministral-3b
```
