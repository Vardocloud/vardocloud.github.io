#!/usr/bin/env python3
"""
Paper Trading Sistemi — Vanitas Kaldıraçlı İşlem Simülatörü (Canlı)
v1.0 — 1 Temmuz 2026

Her saat başı çalışır:
1. Güncel fiyatları çeker
2. Açık pozisyonları kontrol eder (SL/TP/likitasyon)
3. Breakout sinyali üretir
4. Pozisyon açar/kapatır
5. Portföyü günceller
6. Önemli gelişmeleri raporlar

Kullanım:
  python3 paper-trading.py           # Normal çalışma
  python3 paper-trading.py --status  # Portföy durumunu göster
  python3 paper-trading.py --reset   # Portföyü sıfırla
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from urllib.request import Request, urlopen

# ============================================================
# KONFİGÜRASYON
# ============================================================
VERI_DIZINI = os.path.expanduser("~/.hermes/data/paper-trade")
os.makedirs(VERI_DIZINI, exist_ok=True)

PORTFOY_DOSYASI = os.path.join(VERI_DIZINI, "portfoy.json")
GECMIS_DOSYASI = os.path.join(VERI_DIZINI, "gecmis.json")
SINYAL_DOSYASI = os.path.join(VERI_DIZINI, "sinyaller.json")

# Paper trading başlangıç sermayesi
BASLANGIC_SERMAYE = 500.0
KALDIRAC = 5
KOMISYON = 0.001

# Takip edilecek coin'ler (Investing.com listesinden seçildi)
TAKIP_LISTESI = [
    "BTC", "ETH", "XRP", "SOL", "DOGE", "ADA", "LINK", 
    "DOT", "AVAX", "MATIC", "ATOM", "UNI", "LTC", "BCH",
    "NEAR", "APT", "ARB", "OP", "INJ", "TIA"
]

# Stablecoin'ler (atlanacak)
STABLECOINLER = {'USDT', 'USDC', 'DAI', 'USDS', 'USD1', 'USDE', 'USDG', 'USYC', 'FDUSD', 'TUSD', 'BUSD', 'FRAX', 'EURC', 'PYUSD', 'GUSD', 'PAXG', 'XAUT', 'WBT', 'LEO', 'RAIN', 'FIGR_HELOC', 'BNB', 'TRX', 'HYPE', 'ZEC', 'XLM', 'XMR', 'CC', 'GRAM', 'HBAR'}


def log(msg):
    print(f"[PAPER] {msg}", file=sys.stderr)


def fiye(deger):
    """Virgüllü sayıyı float'a çevir"""
    if isinstance(deger, (int, float)):
        return float(deger)
    return float(str(deger).replace(',', '').replace('$', '').replace('B', 'e9').replace('T', 'e12').replace('M', 'e6').replace('K', 'e3'))


# ============================================================
# 1. VERİ ÇEKME
# ============================================================
def anlik_fiyatlar():
    """CoinGecko'dan takip listesindeki coin'lerin anlık fiyatlarını çek"""
    coin_ids = {
        "BTC": "bitcoin", "ETH": "ethereum", "XRP": "ripple", "SOL": "solana",
        "DOGE": "dogecoin", "ADA": "cardano", "LINK": "chainlink", "DOT": "polkadot",
        "AVAX": "avalanche-2", "MATIC": "matic-network", "ATOM": "cosmos",
        "UNI": "uniswap", "LTC": "litecoin", "BCH": "bitcoin-cash",
        "NEAR": "near", "APT": "aptos", "ARB": "arbitrum", "OP": "optimism",
        "INJ": "injective-protocol", "TIA": "celestia",
        "SUI": "sui", "SEI": "sei-network", "PEPE": "pepe", "FLOKI": "floki",
    }
    
    ids = [v for k, v in coin_ids.items() if k in TAKIP_LISTESI]
    ids_str = ','.join(ids)
    
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_str}&vs_currencies=usd&include_24hr_change=true"
    
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urlopen(req, timeout=15)
        data = json.loads(response.read().decode())
        
        # Sembol mapping'ini ters çevir
        sembol_map = {v: k for k, v in coin_ids.items()}
        
        fiyatlar = {}
        for coin_id, info in data.items():
            sembol = sembol_map.get(coin_id, coin_id.upper())
            fiyatlar[sembol] = {
                'fiyat': info.get('usd', 0),
                'degisim_24h': info.get('usd_24h_change', 0),
            }
        
        return fiyatlar
    except Exception as e:
        log(f"Fiyat çekme hatası: {e}")
        return {}


# ============================================================
# 2. PORTFÖY YÖNETİMİ
# ============================================================
class PaperPortfoy:
    def __init__(self):
        self.data = self._yukle()
    
    def _yukle(self):
        if os.path.exists(PORTFOY_DOSYASI):
            try:
                with open(PORTFOY_DOSYASI) as f:
                    return json.load(f)
            except:
                pass
        return self._varsayilan()
    
    def _varsayilan(self):
        return {
            'baslangic': BASLANGIC_SERMAYE,
            'bakiye': BASLANGIC_SERMAYE,
            'ozsermaye': BASLANGIC_SERMAYE,
            'pozisyonlar': {},
            'bekleyen_sinyaller': [],
            'toplam_islem': 0,
            'kazanan': 0,
            'kaybeden': 0,
            'baslangic_tarihi': datetime.now().isoformat(),
            'son_guncelleme': datetime.now().isoformat(),
        }
    
    def kaydet(self):
        self.data['son_guncelleme'] = datetime.now().isoformat()
        self.data['ozsermaye'] = self.data['bakiye']
        with open(PORTFOY_DOSYASI, 'w') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def pozisyon_ac(self, sembol, fiyat, yon):
        """Yeni pozisyon aç"""
        bakiye = self.data['bakiye']
        if bakiye <= 0:
            log(f"Yetersiz bakiye: ${bakiye:.2f}")
            return False
        
        # Pozisyon büyüklüğü (bakiye * kaldıraç)
        poz_buyuklugu = bakiye * KALDIRAC
        komisyon = poz_buyuklugu * KOMISYON
        
        if komisyon > bakiye * 0.5:
            log(f"Komisyon çok yüksek: ${komisyon:.2f}")
            return False
        
        # Likitasyon fiyatı
        if yon == 'long':
            likitasyon = fiyat * (1 - 1/KALDIRAC * 0.9)
            stop_loss = fiyat * 0.97  # %3 stop
            take_profit = fiyat * 1.06  # %6 hedef
        else:
            likitasyon = fiyat * (1 + 1/KALDIRAC * 0.9)
            stop_loss = fiyat * 1.03
            take_profit = fiyat * 0.94
        
        poz_id = f"{sembol}_{int(time.time())}"
        
        self.data['pozisyonlar'][poz_id] = {
            'sembol': sembol,
            'yon': yon,
            'acilis_fiyati': fiyat,
            'guncel_fiyat': fiyat,
            'hacim': poz_buyuklugu,
            'kaldırac': KALDIRAC,
            'likitasyon': likitasyon,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'kar_zarar': 0,
            'kar_zarar_yuzde': 0,
            'acilis_zamani': datetime.now().isoformat(),
        }
        
        self.data['bakiye'] -= komisyon
        self.data['toplam_islem'] += 1
        self.kaydet()
        
        emoji = "🟢" if yon == 'long' else "🔴"
        log(f"{emoji} POZİSYON AÇILDI: {sembol} {yon.upper()} @ ${fiyat:.4f} | SL: ${stop_loss:.4f} | TP: ${take_profit:.4f}")
        return True
    
    def pozisyon_kapat(self, poz_id, fiyat, sebep="manuel"):
        """Pozisyonu kapat"""
        if poz_id not in self.data['pozisyonlar']:
            return None
        
        p = self.data['pozisyonlar'][poz_id]
        hacim = p['hacim']
        acilis = p['acilis_fiyati']
        
        if p['yon'] == 'long':
            kar_zarar = (fiyat - acilis) / acilis * hacim - (hacim * KOMISYON)
        else:
            kar_zarar = (acilis - fiyat) / acilis * hacim - (hacim * KOMISYON)
        
        self.data['bakiye'] += kar_zarar
        self.data['bakiye'] = max(self.data['bakiye'], 0)
        
        if kar_zarar > 0:
            self.data['kazanan'] += 1
        else:
            self.data['kaybeden'] += 1
        
        # Geçmişe kaydet
        islem = {
            'sembol': p['sembol'],
            'yon': p['yon'],
            'acilis': acilis,
            'kapanis': fiyat,
            'kaldırac': p['kaldırac'],
            'kar_zarar': round(kar_zarar, 2),
            'sebep': sebep,
            'acilis_zamani': p['acilis_zamani'],
            'kapanis_zamani': datetime.now().isoformat(),
        }
        self._gecmis_ekle(islem)
        
        emoji = "🟢" if kar_zarar > 0 else "🔴"
        kar_yuzde = (kar_zarar / BASLANGIC_SERMAYE) * 100
        log(f"{emoji} POZİSYON KAPANDI: {p['sembol']} - ${kar_zarar:.2f} ({kar_yuzde:+.2f}%) | {sebep}")
        
        del self.data['pozisyonlar'][poz_id]
        self.kaydet()
        return kar_zarar
    
    def pozisyonlari_kontrol_et(self, fiyatlar):
        """Açık pozisyonları kontrol et (SL/TP/likitasyon)"""
        kapatilan = []
        
        for poz_id in list(self.data['pozisyonlar'].keys()):
            p = self.data['pozisyonlar'][poz_id]
            sembol = p['sembol']
            fiyat = fiyatlar.get(sembol, {}).get('fiyat', 0)
            
            if fiyat == 0:
                continue
            
            p['guncel_fiyat'] = fiyat
            
            if p['yon'] == 'long':
                p['kar_zarar'] = (fiyat - p['acilis_fiyati']) / p['acilis_fiyati'] * p['hacim']
                p['kar_zarar_yuzde'] = (fiyat - p['acilis_fiyati']) / p['acilis_fiyati'] * 100
            
                if fiyat <= p['likitasyon']:
                    k = self.pozisyon_kapat(poz_id, fiyat, "💀 likitasyon")
                    if k: kapatilan.append(('likitasyon', sembol, k))
                elif p['stop_loss'] and fiyat <= p['stop_loss']:
                    k = self.pozisyon_kapat(poz_id, fiyat, "stop-loss")
                    if k: kapatilan.append(('stop-loss', sembol, k))
                elif p['take_profit'] and fiyat >= p['take_profit']:
                    k = self.pozisyon_kapat(poz_id, fiyat, "🎯 take-profit")
                    if k: kapatilan.append(('take-profit', sembol, k))
            else:  # short
                p['kar_zarar'] = (p['acilis_fiyati'] - fiyat) / p['acilis_fiyati'] * p['hacim']
                p['kar_zarar_yuzde'] = (p['acilis_fiyati'] - fiyat) / p['acilis_fiyati'] * 100
                
                if fiyat >= p['likitasyon']:
                    k = self.pozisyon_kapat(poz_id, fiyat, "💀 likitasyon")
                    if k: kapatilan.append(('likitasyon', sembol, k))
                elif p['stop_loss'] and fiyat >= p['stop_loss']:
                    k = self.pozisyon_kapat(poz_id, fiyat, "stop-loss")
                    if k: kapatilan.append(('stop-loss', sembol, k))
                elif p['take_profit'] and fiyat <= p['take_profit']:
                    k = self.pozisyon_kapat(poz_id, fiyat, "🎯 take-profit")
                    if k: kapatilan.append(('take-profit', sembol, k))
        
        self.kaydet()
        return kapatilan
    
    def _gecmis_ekle(self, islem):
        """İşlemi geçmişe ekle"""
        gecmis = []
        if os.path.exists(GECMIS_DOSYASI):
            try:
                with open(GECMIS_DOSYASI) as f:
                    gecmis = json.load(f)
            except:
                pass
        
        gecmis.append(islem)
        with open(GECMIS_DOSYASI, 'w') as f:
            json.dump(gecmis[-100:], f, ensure_ascii=False, indent=2)  # son 100 işlem
    
    def sinyal_ekle(self, sembol, yon, fiyat, sebep):
        """Sinyal kuyruğuna ekle"""
        self.data['bekleyen_sinyaller'].append({
            'sembol': sembol,
            'yon': yon,
            'fiyat': fiyat,
            'sebep': sebep,
            'zaman': datetime.now().isoformat(),
        })
        # Son 20 sinyali tut
        self.data['bekleyen_sinyaller'] = self.data['bekleyen_sinyaller'][-20:]
        self.kaydet()
    
    def portfoy_ozeti(self):
        """Portföy özeti"""
        toplam_kar_zarar = self.data['bakiye'] - BASLANGIC_SERMAYE
        kar_yuzde = (toplam_kar_zarar / BASLANGIC_SERMAYE) * 100
        
        win_rate = (self.data['kazanan'] / self.data['toplam_islem'] * 100) if self.data['toplam_islem'] > 0 else 0
        
        return {
            'bakiye': round(self.data['bakiye'], 2),
            'baslangic': BASLANGIC_SERMAYE,
            'net_kar_zarar': round(toplam_kar_zarar, 2),
            'getiri_yuzde': round(kar_yuzde, 2),
            'toplam_islem': self.data['toplam_islem'],
            'kazanan': self.data['kazanan'],
            'kaybeden': self.data['kaybeden'],
            'win_rate': round(win_rate, 1),
            'aktif_pozisyon': len(self.data['pozisyonlar']),
        }


# ============================================================
# 3. SİNYAL ÜRETİCİ
# ============================================================
class SinyalUretici:
    """Breakout stratejisi ile sinyal üret — Bitcoin Arısı tarzı (geçmiş veri + anlık)"""
    
    def __init__(self):
        pass
    
    def gecmis_analiz(self, sembol, gun=30):
        """Geçmiş veriden trend, EMA, RSI, direnç/destek hesapla"""
        try:
            import yfinance as yf
            import pandas as pd
            
            ticker_map = {
                "BTC": "BTC-USD", "ETH": "ETH-USD", "XRP": "XRP-USD", "SOL": "SOL-USD",
                "DOGE": "DOGE-USD", "ADA": "ADA-USD", "LINK": "LINK-USD", "DOT": "DOT-USD",
                "AVAX": "AVAX-USD", "LTC": "LTC-USD", "BCH": "BCH-USD", "NEAR": "NEAR-USD",
                "APT": "APT-USD", "ARB": "ARB-USD", "OP": "OP-USD", "INJ": "INJ-USD",
                "TIA": "TIA-USD", "ATOM": "ATOM-USD", "UNI": "UNI-USD", "MATIC": "MATIC-USD",
            }
            ticker = ticker_map.get(sembol)
            if not ticker:
                return None
            
            df = yf.Ticker(ticker).history(period=f"{gun}d")
            if df.empty or len(df) < 10:
                return None
            
            # Hareketli ortalamalar
            df['EMA5'] = df['Close'].ewm(span=5).mean()
            df['EMA10'] = df['Close'].ewm(span=10).mean()
            df['EMA20'] = df['Close'].ewm(span=20).mean()
            
            # RSI
            delta = df['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(window=7).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=7).mean()
            rs = gain / loss.replace(0, float('nan'))
            rsi = (100 - (100 / (1 + rs))).iloc[-1]
            
            son = df.iloc[-1]
            onceki = df.iloc[-2]
            
            # Trend
            ema5, ema10, ema20 = son['EMA5'], son['EMA10'], son['EMA20']
            fiyat = son['Close']
            
            if ema5 > ema10 > ema20:
                trend = "yukari"
                trend_guclu = True
            elif ema5 < ema10 < ema20:
                trend = "asagi"
                trend_guclu = True
            else:
                trend = "yatay"
                trend_guclu = False
            
            # Direnç / Destek (son 20 gün)
            son20 = df[-20:]
            direnc = son20['High'].max()
            destek = son20['Low'].min()
            
            # Hacim kontrolü
            hacim_ort = son20['Volume'].mean()
            hacim_son = son['Volume']
            hacim_anomali = hacim_son / hacim_ort if hacim_ort > 0 else 1
            
            # Günlük değişim
            gunluk_deg = ((fiyat - onceki['Close']) / onceki['Close']) * 100
            
            return {
                'trend': trend,
                'trend_guclu': trend_guclu,
                'rsi': rsi,
                'ema5': ema5,
                'ema10': ema10,
                'ema20': ema20,
                'direnc': direnc,
                'destek': destek,
                'hacim_anomali': hacim_anomali,
                'gunluk_degisim': gunluk_deg,
                'fiyat': fiyat,
            }
        except Exception as e:
            log(f"Geçmiş analiz hatası ({sembol}): {e}")
            return None
    
    def btc_trend_kontrol(self):
        """BTC'nin trend yönünü kontrol et — altcoin sinyalleri için filtre"""
        try:
            import yfinance as yf
            df = yf.Ticker("BTC-USD").history(period="30d")
            if df.empty or len(df) < 10:
                return "bilinmiyor"
            
            df['EMA5'] = df['Close'].ewm(span=5).mean()
            df['EMA10'] = df['Close'].ewm(span=10).mean()
            df['EMA20'] = df['Close'].ewm(span=20).mean()
            
            son = df.iloc[-1]
            if son['EMA5'] > son['EMA10'] > son['EMA20']:
                return "yukari"
            elif son['EMA5'] < son['EMA10'] < son['EMA20']:
                return "asagi"
            return "yatay"
        except:
            return "bilinmiyor"
    
    def atr_hesapla(self, df, period=14):
        """ATR (Average True Range) hesapla — volatilite bazlı stop-loss"""
        import pandas as pd
        yuksek = df['High']
        dusuk = df['Low']
        onceki_kapanis = df['Close'].shift(1)
        
        tr1 = yuksek - dusuk
        tr2 = (yuksek - onceki_kapanis).abs()
        tr3 = (dusuk - onceki_kapanis).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean().iloc[-1]
        return atr
    
    def sinyal_uret(self, sembol, fiyat, degisim_24h, btc_trend=None):
        """Breakout + geçmiş veri + BTC trend filtresi ile sinyal üret"""
        sinyaller = []
        
        # 0. BTC trendini kontrol et (altcoin'ler için)
        if btc_trend is None:
            btc_trend = self.btc_trend_kontrol()
        
        # 1. Geçmiş veriyi analiz et
        gecmis = self.gecmis_analiz(sembol)
        
        # 2. Anlık momentum sinyali (acil durum, sadece BTC trend izin veriyorsa)
        if degisim_24h and abs(degisim_24h) > 5:
            if degisim_24h > 5 and btc_trend != "asagi":
                sinyaller.append(('long', fiyat, f"%{degisim_24h:+.2f} 24s güçlü yükseliş • BTC: {btc_trend}"))
            elif degisim_24h < -5 and btc_trend != "yukari":
                sinyaller.append(('short', fiyat, f"%{degisim_24h:+.2f} 24s güçlü düşüş • BTC: {btc_trend}"))
        
        # 3. Geçmiş veri bazlı sinyal
        if gecmis:
            trend = gecmis['trend']
            rsi = gecmis['rsi']
            direnc = gecmis['direnc']
            destek = gecmis['destek']
            fiyat_anlik = gecmis['fiyat']
            
            # BTC trend filtresi uygula:
            # BTC yukarı trendde → LONG'a izin ver, SHORT'u kısıtla
            # BTC aşağı trendde → SHORT'a izin ver, LONG'u kısıtla
            long_izin = btc_trend in ("yukari", "yatay", "bilinmiyor")
            short_izin = btc_trend in ("asagi", "yatay", "bilinmiyor")
            
            # Trend yukarı + RSI uygun + BTC izni varsa → LONG
            if trend == "yukari" and rsi < 70 and long_izin:
                sinyaller.append(('long', fiyat_anlik,
                    f"📈 Trend: yukarı | RSI: {rsi:.0f} | Direnç: ${direnc:.2f} | BTC: {btc_trend}"))
            
            # Trend aşağı + RSI uygun + BTC izni varsa → SHORT
            elif trend == "asagi" and rsi > 30 and short_izin:
                sinyaller.append(('short', fiyat_anlik,
                    f"📉 Trend: aşağı | RSI: {rsi:.0f} | Destek: ${destek:.2f} | BTC: {btc_trend}"))
            
            # Bitcoin Arısı tarzı: Direnç kırılımı (sadece BTC uygun trenddeyse)
            if fiyat_anlik > direnc and trend == "yukari" and long_izin:
                sinyaller.append(('long', fiyat_anlik,
                    f"🚀 Direnç kırılımı ${direnc:.2f} → ${direnc*1.1:.2f} | BTC: {btc_trend}"))
            
            # Bitcoin Arısı tarzı: Destek kırılımı (sadece BTC uygun trenddeyse)
            if fiyat_anlik < destek and trend == "asagi" and short_izin:
                sinyaller.append(('short', fiyat_anlik,
                    f"💀 Destek kırılımı ${destek:.2f} → ${destek*0.9:.2f} | BTC: {btc_trend}"))
        
        # 4. Ucuz coin fırsatı (geçmiş veri yoksa saf fiyata bak)
        if not gecmis and fiyat < 0.10 and degisim_24h and degisim_24h > 0:
            sinyaller.append(('long', fiyat, f"Ucuz coin (${fiyat:.4f}) + pozitif momentum"))
        
        return sinyaller


# ============================================================
# 4. ANA FONKSİYONLAR
# ============================================================
def paper_trade_calistir():
    """Paper trading ana döngüsü — her saat başı çalışır"""
    portfoy = PaperPortfoy()
    sinyal_uretici = SinyalUretici()
    
    # 1. Güncel fiyatları çek
    log("Fiyatlar çekiliyor...")
    fiyatlar = anlik_fiyatlar()
    
    if not fiyatlar:
        log("Fiyat alınamadı, eski veriyle devam")
        return None
    
    log(f"{len(fiyatlar)} coin fiyatı alındı")
    
    # 2. Açık pozisyonları kontrol et
    kapatilan = portfoy.pozisyonlari_kontrol_et(fiyatlar)
    if kapatilan:
        for sebep, sembol, kz in kapatilan:
            print(f"{sebep}: {sembol} — ${kz:.2f}")
    
    # 3. Sinyal üret (max 3 coin'de pozisyon aç)
    aktif_sayi = len(portfoy.data['pozisyonlar'])
    
    if aktif_sayi < 3:  # max 3 eşzamanlı pozisyon
        for sembol in TAKIP_LISTESI:
            if sembol in STABLECOINLER:
                continue
            
            bilgi = fiyatlar.get(sembol, {})
            fiyat = bilgi.get('fiyat', 0)
            degisim = bilgi.get('degisim_24h', 0)
            
            if fiyat == 0:
                continue
            
            # Zaten pozisyon var mı?
            zaten_var = any(p['sembol'] == sembol for p in portfoy.data['pozisyonlar'].values())
            if zaten_var:
                continue
            
            sinyaller = sinyal_uretici.sinyal_uret(sembol, fiyat, degisim)
            
            for yon, sfiyat, sebep in sinyaller:
                if aktif_sayi >= 3:
                    break
                if portfoy.pozisyon_ac(sembol, sfiyat, yon):
                    portfoy.sinyal_ekle(sembol, yon, sfiyat, sebep)
                    print(f"📡 SİNYAL: {sembol} {yon.upper()} @ ${sfiyat:.4f} | {sebep}")
                    aktif_sayi += 1
    
    # 4. Özet üret
    ozet = portfoy.portfoy_ozeti()
    
    # Rapor metni
    emoji = "🟢" if ozet['net_kar_zarar'] >= 0 else "🔴"
    
    rapor = f"""
📊 PAPER TRADING — {datetime.now().strftime('%d %B %Y %H:%M')}
{emoji} Portföy: ${ozet['bakiye']:.2f} (%{ozet['getiri_yuzde']:+.1f})
━━━━━━━━━━━━━━━━━━━━
💰 Bakiye: ${ozet['bakiye']:.2f} | Başlangıç: ${ozet['baslangic']:.0f}
📈 İşlem: {ozet['toplam_islem']} | WR: %{ozet['win_rate']} ({ozet['kazanan']}W/{ozet['kaybeden']}L)
🎯 Aktif pozisyon: {ozet['aktif_pozisyon']}/3
"""
    
    # Aktif pozisyon detayı
    if portfoy.data['pozisyonlar']:
        rapor += f"\n📌 AÇIK POZİSYONLAR:\n"
        for poz_id, p in portfoy.data['pozisyonlar'].items():
            emoji_p = "🟢" if p['yon'] == 'long' else "🔴"
            kz_yuzde = (p['guncel_fiyat'] - p['acilis_fiyati']) / p['acilis_fiyati'] * 100
            if p['yon'] == 'short':
                kz_yuzde = (p['acilis_fiyati'] - p['guncel_fiyat']) / p['acilis_fiyati'] * 100
            rapor += f"{emoji_p} {p['sembol']} {p['yon'].upper()} | Giriş: ${p['acilis_fiyati']:.4f} | K/Z: %{kz_yuzde:+.2f}\n"
    
    # Kapatılan pozisyonlar
    if kapatilan:
        rapor += f"\n🔄 SON İŞLEMLER:\n"
        for sebep, sembol, kz in kapatilan[-3:]:
            emoji_k = "🟢" if kz > 0 else "🔴"
            rapor += f"{emoji_k} {sembol}: ${kz:.2f} ({sebep})\n"
    
    return rapor


def portfoy_durumu():
    """Portföy durumunu göster"""
    portfoy = PaperPortfoy()
    ozet = portfoy.portfoy_ozeti()
    fiyatlar = anlik_fiyatlar()
    
    # Aktif pozisyonları güncelle
    if fiyatlar:
        portfoy.pozisyonlari_kontrol_et(fiyatlar)
    
    emoji = "🟢" if ozet['net_kar_zarar'] >= 0 else "🔴"
    
    print(f"""
📊 PAPER TRADING PORTFÖY DURUMU
{emoji} Net K/Z: ${ozet['net_kar_zarar']:.2f} (%{ozet['getiri_yuzde']:+.1f})
━━━━━━━━━━━━━━━━━━━━
💰 Bakiye: ${ozet['bakiye']:.2f}
💼 Başlangıç: ${ozet['baslangic']:.0f}
📈 Toplam İşlem: {ozet['toplam_islem']}
🎯 Win Rate: %{ozet['win_rate']} ({ozet['kazanan']}W/{ozet['kaybeden']}L)
📌 Aktif: {ozet['aktif_pozisyon']}/3
""")
    
    if portfoy.data['pozisyonlar']:
        print(f"📌 AÇIK POZİSYONLAR:")
        for poz_id, p in portfoy.data['pozisyonlar'].items():
            emoji_p = "🟢" if p['yon'] == 'long' else "🔴"
            kz_yuzde = (p['guncel_fiyat'] - p['acilis_fiyati']) / p['acilis_fiyati'] * 100
            if p['yon'] == 'short':
                kz_yuzde = (p['acilis_fiyati'] - p['guncel_fiyat']) / p['acilis_fiyati'] * 100
            sl_tp = f"SL: ${p['stop_loss']:.4f} | TP: ${p['take_profit']:.4f}"
            print(f"  {emoji_p} {p['sembol']} {p['yon'].upper()} @ ${p['acilis_fiyati']:.4f} → ${p['guncel_fiyat']:.4f} (%{kz_yuzde:+.2f})")
            print(f"     {sl_tp}")
    
    # Coin fiyatları
    if fiyatlar:
        print(f"\n🪙 GÜNCEL FİYATLAR:")
        for sembol in TAKIP_LISTESI[:10]:
            bilgi = fiyatlar.get(sembol, {})
            fiyat = bilgi.get('fiyat', 0)
            degisim = bilgi.get('degisim_24h', 0)
            if fiyat:
                ok = "🟢" if degisim and degisim > 0 else "🔴" if degisim and degisim < 0 else "⚪"
                print(f"  {ok} {sembol}: ${fiyat:.4f} (%{degisim:+.2f})" if fiyat < 1 else f"  {ok} {sembol}: ${fiyat:.2f} (%{degisim:+.2f})")


def sifirla():
    """Portföyü sıfırla"""
    if os.path.exists(PORTFOY_DOSYASI):
        os.remove(PORTFOY_DOSYASI)
    if os.path.exists(GECMIS_DOSYASI):
        os.remove(GECMIS_DOSYASI)
    if os.path.exists(SINYAL_DOSYASI):
        os.remove(SINYAL_DOSYASI)
    print("✅ Paper trading portföyü sıfırlandı. Başlangıç sermayesi: $500")


def backtest_calistir(baslangic_tarihi, sembol="SOL", sermaye=500):
    """Geçmiş bir tarihten bugüne stratejiyi test et"""
    import yfinance as yf
    import pandas as pd
    from datetime import datetime
    
    print(f"\n{'='*50}")
    print(f"📜 BACKTEST — {sembol}")
    print(f"{'='*50}")
    print(f"Başlangıç: {baslangic_tarihi} | Sermaye: ${sermaye} | Kaldıraç: x{KALDIRAC}")
    
    # Veriyi çek
    ticker_map = {
        "BTC": "BTC-USD", "ETH": "ETH-USD", "XRP": "XRP-USD", "SOL": "SOL-USD",
        "DOGE": "DOGE-USD", "ADA": "ADA-USD", "LINK": "LINK-USD", "DOT": "DOT-USD",
        "AVAX": "AVAX-USD", "LTC": "LTC-USD", "BCH": "BCH-USD", "NEAR": "NEAR-USD",
    }
    ticker = ticker_map.get(sembol, f"{sembol}-USD")
    
    bugun = datetime.now().strftime('%Y-%m-%d')
    df = yf.Ticker(ticker).history(start=baslangic_tarihi, end=bugun)
    
    if df.empty or len(df) < 10:
        print(f"⚠️  Yetersiz veri ({len(df)} gün)")
        return
    
    print(f"📊 {len(df)} günlük veri ({df.index[0].date()} → {df.index[-1].date()})")
    
    # PaperPortfoy'u sıfırla ve backtest için kullan
    portfoy = PaperPortfoy()
    portfoy.data = portfoy._varsayilan()
    portfoy.data['baslangic'] = sermaye
    portfoy.data['bakiye'] = sermaye
    sinyal_uretici = SinyalUretici()
    
    gunluk_adim = 0
    toplam_gun = len(df)
    poz_aktif = False
    poz_yon = None
    
    for i in range(5, len(df)):
        if portfoy.data['bakiye'] <= 0:
            break
        
        gun = df.index[i]
        acilis = df['Open'].iloc[i]
        yuksek = df['High'].iloc[i]
        dusuk = df['Low'].iloc[i]
        kapanis = df['Close'].iloc[i]
        
        # Açık pozisyon var mı kontrol et
        if poz_aktif:
            poz_id = list(portfoy.data['pozisyonlar'].keys())[0] if portfoy.data['pozisyonlar'] else None
            if poz_id:
                p = portfoy.data['pozisyonlar'][poz_id]
                
                # Gün içi SL/TP/likitasyon kontrolü
                if poz_yon == 'long':
                    if dusuk <= p['stop_loss']:
                        portfoy.pozisyon_kapat(poz_id, p['stop_loss'] * 0.99, "stop-loss")
                        poz_aktif = False
                    elif yuksek >= p['take_profit']:
                        portfoy.pozisyon_kapat(poz_id, p['take_profit'] * 1.01, "🎯 take-profit")
                        poz_aktif = False
                else:
                    if yuksek >= p['stop_loss']:
                        portfoy.pozisyon_kapat(poz_id, p['stop_loss'] * 1.01, "stop-loss")
                        poz_aktif = False
                    elif dusuk <= p['take_profit']:
                        portfoy.pozisyon_kapat(poz_id, p['take_profit'] * 0.99, "🎯 take-profit")
                        poz_aktif = False
            
            # Gün sonu kapat (gecelik pozisyon taşıma)
            if poz_aktif and poz_id:
                portfoy.pozisyon_kapat(poz_id, kapanis, "gün sonu")
                poz_aktif = False
        
        if portfoy.data['bakiye'] <= 0:
            break
        
        # Sinyal üret (o günkü kapanış fiyatı ve geçmiş 30 günlük veri ile)
        sinyaller = sinyal_uretici.sinyal_uret(sembol, kapanis, 0)
        
        if sinyaller and not poz_aktif:
            yon, fiyat, sebep = sinyaller[0]
            if portfoy.pozisyon_ac(sembol, fiyat, yon):
                poz_aktif = True
                poz_yon = yon
        
        gunluk_adim += 1
        if gunluk_adim % 30 == 0:
            print(f"  ⏳ {gunluk_adim}/{toplam_gun} gün | Bakiye: ${portfoy.data['bakiye']:.2f}")
    
    # Kalan pozisyonu kapat
    if poz_aktif and portfoy.data['pozisyonlar']:
        poz_id = list(portfoy.data['pozisyonlar'].keys())[0]
        portfoy.pozisyon_kapat(poz_id, df['Close'].iloc[-1], "süre sonu")
    
    ozet = portfoy.portfoy_ozeti()
    emoji = "🟢" if ozet['net_kar_zarar'] >= 0 else "🔴"
    
    print(f"\n{'='*50}")
    print(f"📊 BACKTEST SONUCU — {sembol}")
    print(f"{'='*50}")
    print(f"{emoji} Başlangıç: ${sermaye:.0f} → ${ozet['bakiye']:.2f}")
    print(f"💰 K/Z: ${ozet['net_kar_zarar']:.2f} (%{ozet['getiri_yuzde']:+.1f})")
    print(f"📈 İşlem: {ozet['toplam_islem']} | WR: %{ozet['win_rate']} ({ozet['kazanan']}W/{ozet['kaybeden']}L)")
    
    return ozet


def main():
    if '--status' in sys.argv:
        portfoy_durumu()
        return
    
    if '--reset' in sys.argv:
        sifirla()
        return
    
    if '--backtest' in sys.argv:
        idx = sys.argv.index('--backtest')
        tarih = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "2026-01-01"
        sembol = "SOL"
        sermaye = 500
        for i, arg in enumerate(sys.argv):
            if arg == '--coin' and i+1 < len(sys.argv):
                sembol = sys.argv[i+1].upper()
            if arg == '--sermaye' and i+1 < len(sys.argv):
                sermaye = int(sys.argv[i+1])
        backtest_calistir(tarih, sembol, sermaye)
        return
    
    # Normal çalışma (canlı paper trading)
    rapor = paper_trade_calistir()
    if rapor:
        print(rapor)
    else:
        print("[SILENT]")


if __name__ == '__main__':
    main()
