#!/usr/bin/env python3
"""
Bitcoin Arısı (@BitcoinArisi) Telegram Kanalı Tarayıcı
Vanitas — Ekonomi Zekası Kaynak Entegrasyonu

t.me/s/BitcoinArisi sayfasını tarar, mesajları çeker,
reklamları filtreler, birikim fikirlerini kategorize eder.

Kullanım:
  python3 bitcoin-arisi-tarayici.py              # normal tarama (sadece yeni mesajlar)
  python3 bitcoin-arisi-tarayici.py --full       # tüm geçmişi tarar (sayfalama ile)
  python3 bitcoin-arisi-tarayici.py --report     # sadece bugünün özetini göster
  python3 bitcoin-arisi-tarayici.py --filtreli   # filtrelenmiş birikim fikirlerini göster
"""

import requests
import json
import os
import re
import sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

# === KONFİGÜRASYON ===
KANAL = "BitcoinArisi"
BASE_URL = f"https://t.me/s/{KANAL}"
VERI_DIZINI = os.path.expanduser("~/.hermes/data/bitcoin-arisi")
VERI_DOSYASI = os.path.join(VERI_DIZINI, "mesajlar.json")
RAPOR_DOSYASI = os.path.join(VERI_DIZINI, "birikim-fikirleri.json")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

# Reklam/bot tanıtımı için filtre anahtar kelimeleri
REKLAM_KELIMELER = [
    r'@\w+_bot', r'bot', r'reklam', r'ücretsiz', r'ücredsiz',
    r'sinyal', r'signal', r'giriş yap', r'kaydol',
    r'premium', r'vip', r'özel üyelik', r'telegram kanalı',
    r'davet et', r'çevrenizi davet', r'toplama', r'ense karartma',
]

# Filtrelenecek coin'ler (bildirimlerde gösterilmez, min. yatırım eşiği vs.)
FILTRENECEK_COINLER = [
    r'\bvoid\b', r'\bvoid\b',  # min $150 yatırım — Edel için uygun değil
]

# Birikim fikri / drop fırsatı / ucuz yatırım için anahtar kelimeler
BIRIKIM_KELIMELERI = [
    r'direnç', r'destek', r'hedef', r'alım', r'düşüş',
    r'fırsat', r'drop', r'ucuz', r'ön satış', r'ico',
    r'presale', r'sto', r'token satış', r'erken',
    r'proje', r'yeni liste', r'birikim', r'uzun vade',
    r'orta vade', r'portföy', r'dca', r'krılım',
    r'0,\d+\$',  # çok düşük fiyatlı coin'ler (0.00x$)
]


def log(msg):
    print(f"[Bitcoin Arısı] {msg}", file=sys.stderr)


def sayfa_indir(url):
    """HTML sayfasını indir"""
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
    }
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        return r.text
    except Exception as e:
        log(f"Sayfa indirme hatası: {e}")
        return None


def mesajlari_parse(html):
    """HTML'den mesajları çıkar"""
    soup = BeautifulSoup(html, 'html.parser')
    mesajlar = []
    
    # Her bir mesaj wrap'ini bul
    for wrap in soup.select('.tgme_widget_message_wrap'):
        msg_div = wrap.select_one('.tgme_widget_message')
        if not msg_div:
            continue
        
        data_post = msg_div.get('data-post', '')
        post_id = data_post.replace(f"{KANAL}/", "") if data_post else ""
        
        # Zaman
        time_tag = msg_div.select_one('time')
        z依稀n = time_tag.get('datetime') if time_tag else ""
        
        # Görüntülenme
        views_span = msg_div.select_one('.tgme_widget_message_views')
        views = views_span.get_text(strip=True) if views_span else "0"
        
        # Mesaj metni
        text_div = msg_div.select_one('.tgme_widget_message_text')
        mesaj_metni = ""
        if text_div:
            mesaj_metni = text_div.get_text('\n', strip=True)
        
        # Eğer metin yoksa, medya mesajı olabilir
        if not mesaj_metni:
            not_supported = msg_div.select_one('.message_media_not_supported_label')
            if not_supported:
                mesaj_metni = f"[MEDYA: {not_supported.get_text(strip=True)}]"
            else:
                mesaj_metni = "[MEDYA]"
        
        # Link preview varsa
        link_title = ""
        link_desc = ""
        link_preview = msg_div.select_one('.link_preview_title')
        link_preview_desc = msg_div.select_one('.link_preview_description')
        if link_preview:
            link_title = link_preview.get_text(strip=True)
        if link_preview_desc:
            link_desc = link_preview_desc.get_text(strip=True)
        
        if not post_id:
            continue
        
        mesajlar.append({
            'id': post_id,
            'tarih': z依稀n,
            'views': views,
            'metin': mesaj_metni,
            'link_baslik': link_title,
            'link_aciklama': link_desc,
        })
    
    return mesajlar


def sonraki_sayfa_before(html):
    """Sayfadaki en eski mesajın ID'sini bul (before parametresi için)"""
    soup = BeautifulSoup(html, 'html.parser')
    # En alttaki "previous messages" linkini ara
    prev_link = soup.select_one('.js-messages_more_wrap a[href*="before="]')
    if prev_link:
        href = prev_link.get('href', '')
        match = re.search(r'before=(\d+)', href)
        if match:
            return match.group(1)
    return None


def reklam_mi(mesaj):
    """Mesajın reklam/bot tanıtımı olup olmadığını kontrol et"""
    metin = mesaj.get('metin', '').lower()
    for kelime in REKLAM_KELIMELER:
        if re.search(kelime, metin, re.IGNORECASE):
            return True
    # Eğer sadece @mention varsa ve analiz yoksa reklam olabilir
    if re.search(r'@\w+', mesaj.get('metin', '')) and len(metin) < 150:
        return True
    return False


def filtrelenmis_coin_mi(mesaj):
    """Filtrelenen coin'lerden biri mesajda geçiyor mu?"""
    metin = mesaj.get('metin', '').lower()
    for kelime in FILTRENECEK_COINLER:
        if re.search(kelime, metin, re.IGNORECASE):
            return True
    return False


def birikim_fikri_mi(mesaj):
    """Mesajın birikim fikri / drop fırsatı / ucuz yatırım olup olmadığını kontrol et"""
    metin = mesaj.get('metin', '').lower()
    for kelime in BIRIKIM_KELIMELERI:
        if re.search(kelime, metin, re.IGNORECASE):
            return True
    return False


def kategorize_et(mesaj):
    """Mesajı kategorize et"""
    metin = mesaj.get('metin', '').lower()
    
    # Kripto kategorileri
    if any(coin in metin for coin in ['bitcoin', 'btc', 'btc ']):
        kripto = 'Bitcoin'
    elif any(coin in metin for coin in ['solana', 'sol ']):
        kripto = 'Solana'
    elif any(coin in metin for coin in ['sui']):
        kripto = 'Sui'
    elif any(coin in metin for coin in ['chz', 'chiliz']):
        kripto = 'Chiliz'
    else:
        kripto = 'Altcoin'
    
    # Fiyat seviyesine göre ucuz yatırım mı?
    ucuz_mu = False
    fiyatlar = re.findall(r'0,\d+\$', metin)
    if fiyatlar:
        rakamlar = [float(f.replace(',', '.').replace('$', '')) for f in fiyatlar]
        if any(r < 1.0 for r in rakamlar):
            ucuz_mu = True
    
    # Drop fırsatı mı?
    drop_mu = bool(re.search(r'düşüş|destek|fırsat|alım', metin, re.IGNORECASE))
    
    return {
        'kripto': kripto,
        'ucuz_mu': ucuz_mu,
        'drop_mu': drop_mu,
        'hedef_fiyat': fiyatlar if fiyatlar else [],
    }


def mevcut_veriyi_yukle():
    """Daha önce kaydedilmiş veriyi yükle"""
    if os.path.exists(VERI_DOSYASI):
        try:
            with open(VERI_DOSYASI, 'r') as f:
                return json.load(f)
        except:
            pass
    return {'son_guncelleme': None, 'mesajlar': {}, 'istatistik': {}}


def veriyi_kaydet(veri):
    """Veriyi kaydet"""
    os.makedirs(VERI_DIZINI, exist_ok=True)
    veri['son_guncelleme'] = datetime.now(timezone.utc).isoformat()
    with open(VERI_DOSYASI, 'w') as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)
    log(f"{len(veri['mesajlar'])} mesaj kaydedildi → {VERI_DOSYASI}")


def birikim_fikirlerini_kaydet(fikirler):
    """Birikim fikirlerini ayrı dosyaya kaydet"""
    os.makedirs(VERI_DIZINI, exist_ok=True)
    cikti = {
        'son_guncelleme': datetime.now(timezone.utc).isoformat(),
        'kaynak': f"@{KANAL}",
        'toplam_filtrelenmis': len(fikirler),
        'birikim_fikirleri': fikirler,
    }
    with open(RAPOR_DOSYASI, 'w') as f:
        json.dump(cikti, f, ensure_ascii=False, indent=2)
    log(f"{len(fikirler)} birikim fikri kaydedildi → {RAPOR_DOSYASI}")
    return cikti


def tarama(hepsi=False):
    """Ana tarama fonksiyonu"""
    log(f"Tarama başlıyor{' (TÜM GEÇMİŞ)' if hepsi else ' (sadece son mesajlar)'}")
    
    # Mevcut veriyi yükle
    veri = mevcut_veriyi_yukle()
    mevcut_idler = set(veri.get('mesajlar', {}).keys())
    
    url = BASE_URL
    yeni_sayfa = True
    toplam_yeni = 0
    
    while url:
        html = sayfa_indir(url)
        if not html:
            break
        
        mesajlar = mesajlari_parse(html)
        if not mesajlar:
            log("Mesaj bulunamadı, durduruluyor")
            break
        
        for msg in mesajlar:
            mid = msg['id']
            if mid not in mevcut_idler:
                veri['mesajlar'][mid] = msg
                toplam_yeni += 1
        
        log(f"Bu sayfada {len(mesajlar)} mesaj, toplam {len(veri['mesajlar'])} benzersiz")
        
        if hepsi:
            before = sonraki_sayfa_before(html)
            if before and before not in mevcut_idler:
                url = f"{BASE_URL}?before={before}"
                log(f"Önceki sayfaya geç: before={before}")
            else:
                url = None
                if before and before in mevcut_idler:
                    log("Zaten tarandı, durduruluyor")
        else:
            url = None  # Sadece son sayfa
    
    # İstatistik
    veri['istatistik'] = {
        'toplam_mesaj': len(veri['mesajlar']),
        'yeni_mesaj': toplam_yeni,
        'son_tarih': datetime.now(timezone.utc).isoformat(),
    }
    
    veriyi_kaydet(veri)
    log(f"Tarama tamam: {toplam_yeni} yeni mesaj eklendi")
    
    return veri


def filtrele_ve_raporla(veri):
    """Mesajları filtrele ve birikim fikirlerini çıkar"""
    mesajlar = list(veri.get('mesajlar', {}).values())
    
    # Tarihe göre sırala (yeniden eskiye)
    mesajlar.sort(key=lambda m: m.get('tarih', ''), reverse=True)
    
    reklam_sayisi = 0
    birikim_fikirleri = []
    diger_analizler = []
    
    for msg in mesajlar:
        if reklam_mi(msg):
            reklam_sayisi += 1
            continue
        
        if filtrelenmis_coin_mi(msg):
            continue
        
        kategori = kategorize_et(msg)
        
        if birikim_fikri_mi(msg) or kategori['drop_mu'] or kategori['ucuz_mu']:
            birikim_fikirleri.append({
                'id': msg['id'],
                'tarih': msg['tarih'],
                'metin': msg['metin'][:300],
                'kripto': kategori['kripto'],
                'drop_mu': kategori['drop_mu'],
                'ucuz_mu': kategori['ucuz_mu'],
                'hedef_fiyat': kategori['hedef_fiyat'],
                'views': msg['views'],
            })
        else:
            diger_analizler.append(msg)
    
    # Birikim fikirlerini kaydet
    rapor = birikim_fikirlerini_kaydet(birikim_fikirleri)
    rapor['istatistik'] = {
        'toplam_mesaj': len(mesajlar),
        'reklam_filtrelenen': reklam_sayisi,
        'birikim_fikri': len(birikim_fikirleri),
        'diger_analiz': len(diger_analizler),
    }
    
    return rapor


def bugunun_ozeti(veri):
    """Bugün eklenen mesajların özeti"""
    bugun = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    mesajlar = list(veri.get('mesajlar', {}).values())
    mesajlar.sort(key=lambda m: m.get('tarih', ''), reverse=True)
    
    bugun_mesaj = [m for m in mesajlar if m.get('tarih', '').startswith(bugun)]
    
    print(f"\n{'='*50}")
    print(f"🐝 @BitcoinArisi — Bugün ({bugun})")
    print(f"{'='*50}")
    
    if not bugun_mesaj:
        print("Bugün yeni mesaj yok.")
        return
    
    for msg in bugun_mesaj:
        reklam = " [REKLAM]" if reklam_mi(msg) else ""
        filtrelenmis = " [FİLTRELENMİŞ]" if (not reklam and filtrelenmis_coin_mi(msg)) else ""
        birikim = " [BİRİKİM FİKRİ]" if (not reklam and not filtrelenmis and birikim_fikri_mi(msg)) else ""
        print(f"\n[{msg['tarih'][:16]}][{msg['views']} görüntü]{reklam}{filtrelenmis}{birikim}")
        print(f"  {msg['metin'][:200]}")
        if len(msg['metin']) > 200:
            print(f"  ...({len(msg['metin'])} karakter)")


def cron_cikisi(veri, onceki_durum):
    """Cron modu için çıktı üret — sadece yeni mesaj varsa rapor ver"""
    rapor = filtrele_ve_raporla(veri)
    yeni = veri.get('istatistik', {}).get('yeni_mesaj', 0)
    
    if yeni == 0:
        # Yeni mesaj yok — sessiz kal
        return
    
    # Yeni mesaj var — özet gönder
    print(f"🐝 @BitcoinArisi — {yeni} YENİ MESAJ")
    print(f"━━━━━━━━━━━━━━━━━━━━")
    print(f"📊 Toplam: {rapor['istatistik']['toplam_mesaj']} mesaj")
    print(f"🚫 Reklam filtrelenen: {rapor['istatistik']['reklam_filtrelenen']}")
    print(f"💰 Birikim fikri: {rapor['istatistik']['birikim_fikri']}")
    
    # En yeni 3 birikim fikri
    yeniler = [f for f in rapor['birikim_fikirleri'] 
               if any(m.get('id') == f['id'] for m in 
                      list(veri['mesajlar'].values())[-yeni:])]
    
    if yeniler:
        print(f"\n💰 YENİ BİRİKİM FİKİRLERİ:")
        for fikir in yeniler[:3]:
            etiket = []
            if fikir['drop_mu']: etiket.append('📉 DROP')
            if fikir['ucuz_mu']: etiket.append('💎 UCUZ')
            etiket_str = ' | '.join(etiket) if etiket else ''
            print(f"  [{fikir['tarih'][:16]}][{fikir['kripto']}] {etiket_str}")
            print(f"  {fikir['metin'][:150]}")
            if fikir['hedef_fiyat']:
                print(f"  🎯 {', '.join(fikir['hedef_fiyat'][:3])}")


def main():
    hepsi = '--full' in sys.argv
    sadece_rapor = '--report' in sys.argv
    cron_modu = '--cron' in sys.argv
    
    if sadece_rapor:
        veri = mevcut_veriyi_yukle()
        bugunun_ozeti(veri)
        return
    
    # Tarama yap
    veri = tarama(hepsi=hepsi)
    
    if cron_modu:
        cron_cikisi(veri, None)
        return
    
    # Filtrele ve raporla
    rapor = filtrele_ve_raporla(veri)
    
    print(f"\n{'='*50}")
    print(f"🐝 @BitcoinArisi — Tarama Raporu")
    print(f"{'='*50}")
    print(f"📊 Toplam mesaj: {rapor['istatistik']['toplam_mesaj']}")
    print(f"🚫 Filtrelenen reklam: {rapor['istatistik']['reklam_filtrelenen']}")
    print(f"💰 Birikim fikri: {rapor['istatistik']['birikim_fikri']}")
    print(f"📝 Diğer analiz: {rapor['istatistik']['diger_analiz']}")
    
    print(f"\n{'='*50}")
    print(f"💰 BİRİKİM FİKİRLERİ — Düşüşte Alım Fırsatları & Ucuz Yatırımlar")
    print(f"{'='*50}")
    for fikir in rapor['birikim_fikirleri'][:10]:
        etiket = []
        if fikir['drop_mu']: etiket.append('📉 DROP')
        if fikir['ucuz_mu']: etiket.append('💎 UCUZ')
        etiket_str = ' | '.join(etiket) if etiket else ''
        print(f"\n[{fikir['tarih'][:16]}][{fikir['kripto']}] {etiket_str}")
        print(f"  {fikir['metin'][:200]}")
        if fikir['hedef_fiyat']:
            print(f"  🎯 Hedef: {', '.join(fikir['hedef_fiyat'][:5])}")


if __name__ == '__main__':
    main()
