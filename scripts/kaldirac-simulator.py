#!/usr/bin/env python3
"""
Kaldıraçlı İşlem Simülatörü — Vanitas Kripto Trading Sistemi
v1.0 — 1 Temmuz 2026

Kullanım:
  python3 kaldirac-simulator.py --coin BTC-USD --baslangic 1000 --kaldırac 10
  python3 kaldirac-simulator.py --coin XRP-USD --baslangic 500 --kaldırac 5 --short
  python3 kaldirac-simulator.py --coin ETH-USD --strateji breakout --rapor
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
import random

# ============================================================
# KONFİGÜRASYON
# ============================================================
RAPOR_DIZINI = os.path.expanduser("~/.hermes/data/kaldirac-simulasyonu")
os.makedirs(RAPOR_DIZINI, exist_ok=True)

# ============================================================
# 1. VERİ ÇEKME
# ============================================================
def veri_cek(coin, gun=90):
    """yfinance ile geçmiş veri çek"""
    import yfinance as yf
    
    # Coin mapping
    ticker_map = {
        "BTC-USD": "BTC-USD", "XRP-USD": "XRP-USD", "ETH-USD": "ETH-USD",
        "SOL-USD": "SOL-USD", "SUI-USD": "SUI-USD", "CHZ-USD": "CHZ-USD",
        "BNB-USD": "BNB-USD", "DOGE-USD": "DOGE-USD", "ADA-USD": "ADA-USD",
    }
    ticker = ticker_map.get(coin, coin)
    
    print(f"[VERİ] {coin} çekiliyor...")
    hisse = yf.Ticker(ticker)
    df = hisse.history(period=f"{gun}d")
    
    if df.empty:
        print(f"[HATA] {coin} için veri bulunamadı!")
        return None
    
    print(f"[VERİ] {len(df)} günlük veri alındı ({df.index[0].date()} → {df.index[-1].date()})")
    return df

# ============================================================
# 2. KALDIRAÇLI İŞLEM MOTORU
# ============================================================
class KaldiracMotoru:
    """
    Kaldıraçlı işlem simülasyonu.
    - Long/Short desteği
    - Kaldıraç çarpanı
    - Likitasyon hesaplama
    - Stop-loss / Take-profit
    """
    
    def __init__(self, baslangic_sermaye=1000, kaldırac=10, 
                 komisyon=0.001, funding_rate=0.0001):
        self.sermaye = float(baslangic_sermaye)
        self.baslangic_sermaye = float(baslangic_sermaye)
        self.kaldırac = kaldırac
        self.komisyon = komisyon
        self.funding_rate = funding_rate
        
        self.pozisyon = None  # aktif pozisyon
        self.islem_gecmisi = []
        self.sermaye_grafigi = [(0, self.sermaye)]
        self.toplam_islem = 0
        self.kazanan = 0
        self.kaybeden = 0
        
    def pozisyon_ac(self, fiyat, yon="long", hacim=None):
        """Pozisyon aç"""
        if self.pozisyon:
            print("[POZİSYON] Zaten açık pozisyon var!")
            return False
        
        # Kaldıraçlı pozisyon büyüklüğü
        if hacim is None:
            hacim = self.sermaye * self.kaldırac
        
        # Komisyon
        komisyon_ucret = hacim * self.komisyon
        if komisyon_ucret > self.sermaye * 0.5:
            print(f"[HATA] Komisyon ({komisyon_ucret:.2f}$) sermayenin %50'sinden fazla!")
            return False
        
        # Likitasyon fiyatı
        if yon == "long":
            likitasyon = fiyat * (1 - 1/self.kaldırac * 0.9)
        else:
            likitasyon = fiyat * (1 + 1/self.kaldırac * 0.9)
        
        self.pozisyon = {
            'yon': yon,
            'acilis_fiyati': fiyat,
            'hacim': hacim,
            'kaldırac': self.kaldırac,
            'likitasyon': likitasyon,
            'stop_loss': None,
            'take_profit': None,
            'kar_zarar': 0,
            'kar_zarar_yuzde': 0,
        }
        
        self.sermaye -= komisyon_ucret
        self.toplam_islem += 1
        
        print(f"[AÇILDI] {yon.upper()} | Fiyat: {fiyat:.4f}$ | Hacim: ${hacim:.2f} | Kaldıraç: x{self.kaldırac}")
        print(f"[LİKİT] Likitasyon: {likitasyon:.4f}$ | Risk: ${komisyon_ucret:.2f} (komisyon)")
        return True
    
    def stop_loss_ayarla(self, seviye):
        """Stop-loss seviyesi belirle"""
        if not self.pozisyon:
            return
        self.pozisyon['stop_loss'] = seviye
        print(f"[SL] Stop-loss: {seviye:.4f}$")
    
    def take_profit_ayarla(self, seviye):
        """Take-profit seviyesi belirle"""
        if not self.pozisyon:
            return
        self.pozisyon['take_profit'] = seviye
        print(f"[TP] Take-profit: {seviye:.4f}$")
    
    def pozisyon_kapat(self, fiyat, sebep="manuel"):
        """Pozisyonu kapat"""
        if not self.pozisyon:
            return 0
        
        p = self.pozisyon
        acilis = p['acilis_fiyati']
        hacim = p['hacim']
        
        # Kar/Zarar hesapla
        if p['yon'] == 'long':
            fiyat_farki = (fiyat - acilis) / acilis
        else:
            fiyat_farki = (acilis - fiyat) / acilis
        
        kar_zarar = hacim * fiyat_farki - (hacim * self.komisyon)
        kar_yuzde = (kar_zarar / self.baslangic_sermaye) * 100
        
        self.sermaye += kar_zarar
        self.sermaye = max(self.sermaye, 0)  # negatif sermaye olmasın
        
        # İstatistik
        if kar_zarar > 0:
            self.kazanan += 1
        else:
            self.kaybeden += 1
        
        # Kaydet
        islem = {
            'zaman': datetime.now().isoformat(),
            'yon': p['yon'],
            'acilis': acilis,
            'kapanis': fiyat,
            'kaldırac': p['kaldırac'],
            'kar_zarar': round(kar_zarar, 2),
            'kar_yuzde': round(kar_yuzde, 2),
            'sebep': sebep,
            'sermaye_sonrasi': round(self.sermaye, 2),
        }
        self.islem_gecmisi.append(islem)
        
        emoji = "🟢" if kar_zarar > 0 else "🔴"
        print(f"[KAPATILDI] {emoji} {sebep} | K/Z: ${kar_zarar:.2f} ({kar_yuzde:+.2f}%) | Sermaye: ${self.sermaye:.2f}")
        
        self.pozisyon = None
        self.sermaye_grafigi.append((len(self.islem_gecmisi), self.sermaye))
        return kar_zarar
    
    def check_likitasyon(self, fiyat):
        """Likitasyon kontrolü"""
        if not self.pozisyon:
            return False
        
        p = self.pozisyon
        if p['yon'] == 'long' and fiyat <= p['likitasyon']:
            self.pozisyon_kapat(fiyat, "likitasyon")
            print("[💀] LİKİDE OLUNDU! Pozisyon sıfırlandı.")
            return True
        elif p['yon'] == 'short' and fiyat >= p['likitasyon']:
            self.pozisyon_kapat(fiyat, "likitasyon")
            print("[💀] LİKİDE OLUNDU! Pozisyon sıfırlandı.")
            return True
        
        # Stop-loss kontrol
        if p['stop_loss']:
            if p['yon'] == 'long' and fiyat <= p['stop_loss']:
                self.pozisyon_kapat(fiyat, "stop-loss")
                return True
            elif p['yon'] == 'short' and fiyat >= p['stop_loss']:
                self.pozisyon_kapat(fiyat, "stop-loss")
                return True
        
        # Take-profit kontrol
        if p['take_profit']:
            if p['yon'] == 'long' and fiyat >= p['take_profit']:
                self.pozisyon_kapat(fiyat, "take-profit")
                return True
            elif p['yon'] == 'short' and fiyat <= p['take_profit']:
                self.pozisyon_kapat(fiyat, "take-profit")
                return True
        
        return False
    
    def anlik_kar_zarar(self, fiyat):
        """Açık pozisyonun anlık K/Z'sı"""
        if not self.pozisyon:
            return 0
        p = self.pozisyon
        if p['yon'] == 'long':
            return (fiyat - p['acilis_fiyati']) / p['acilis_fiyati'] * p['hacim']
        else:
            return (p['acilis_fiyati'] - fiyat) / p['acilis_fiyati'] * p['hacim']
    
    def rapor(self):
        """Performans raporu"""
        kazanc = self.sermaye - self.baslangic_sermaye
        kazanc_yuzde = (kazanc / self.baslangic_sermaye) * 100
        
        win_rate = (self.kazanan / self.toplam_islem * 100) if self.toplam_islem > 0 else 0
        
        karlar = [i['kar_zarar'] for i in self.islem_gecmisi if i['kar_zarar'] > 0]
        zararlar = [i['kar_zarar'] for i in self.islem_gecmisi if i['kar_zarar'] < 0]
        ortalama_kar = sum(karlar)/len(karlar) if karlar else 0
        ortalama_zarar = sum(zararlar)/len(zararlar) if zararlar else 0
        
        max_drawdown = 0
        zirve = self.baslangic_sermaye
        for _, s in self.sermaye_grafigi:
            zirve = max(zirve, s)
            dd = (zirve - s) / zirve * 100
            max_drawdown = max(max_drawdown, dd)
        
        return {
            'baslangic_sermaye': self.baslangic_sermaye,
            'son_sermaye': round(self.sermaye, 2),
            'net_kar_zarar': round(kazanc, 2),
            'getiri_yuzde': round(kazanc_yuzde, 2),
            'toplam_islem': self.toplam_islem,
            'kazanan': self.kazanan,
            'kaybeden': self.kaybeden,
            'win_rate': round(win_rate, 1),
            'ortalama_kar': round(ortalama_kar, 2),
            'ortalama_zarar': round(ortalama_zarar, 2),
            'max_drawdown': round(max_drawdown, 1),
            'kar_zarar_orani': round(abs(ortalama_kar/ortalama_zarar), 2) if ortalama_zarar != 0 else 0,
        }

# ============================================================
# 3. STRATEJİLER
# ============================================================
class Stratejiler:
    """Test edilecek trading stratejileri"""
    
    @staticmethod
    def breakout_emacross(df, motor, kaldırac=10):
        """
        Bitcoin Arısı esintili: EMA crossover + breakout
        - EMA 20/50 kesişiminde pozisyon aç
        - Direnç/destek kırılımında yön değiştir
        """
        import pandas as pd
        
        df = df.copy()
        df['EMA20'] = df['Close'].ewm(span=20).mean()
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        df['RSI'] = Stratejiler._rsi(df['Close'])
        
        # Pivot noktaları (basit direnç/destek)
        df['Yuksek'] = df['High'].rolling(10).max()
        df['Dusuk'] = df['Low'].rolling(10).min()
        
        poz_aktif = False
        poz_yon = None
        
        for i in range(50, len(df)):
            fiyat = df['Close'].iloc[i]
            tarih = df.index[i]
            
            # Likitasyon kontrolü
            if poz_aktif:
                if motor.check_likitasyon(fiyat):
                    poz_aktif = False
                    poz_yon = None
                    continue
            
            # Sinyal üret
            ema20_once = df['EMA20'].iloc[i-1]
            ema50_once = df['EMA50'].iloc[i-1]
            ema20_simdi = df['EMA20'].iloc[i]
            ema50_simdi = df['EMA50'].iloc[i]
            
            rsi = df['RSI'].iloc[i]
            yuksek = df['Yuksek'].iloc[i]
            dusuk = df['Dusuk'].iloc[i]
            
            # LONG sinyali: EMA20 > EMA50 kesişimi + RSI < 70
            if not poz_aktif and ema20_once <= ema50_once and ema20_simdi > ema50_simdi and rsi < 70:
                motor.pozisyon_ac(fiyat, "long")
                motor.stop_loss_ayarla(fiyat * 0.97)  # %3 stop
                motor.take_profit_ayarla(fiyat * 1.06)  # %6 hedef
                poz_aktif = True
                poz_yon = "long"
            
            # SHORT sinyali: EMA20 < EMA50 kesişimi + RSI > 30
            elif not poz_aktif and ema20_once >= ema50_once and ema20_simdi < ema50_simdi and rsi > 30:
                motor.pozisyon_ac(fiyat, "short")
                motor.stop_loss_ayarla(fiyat * 1.03)  # %3 stop
                motor.take_profit_ayarla(fiyat * 0.94)  # %6 hedef
                poz_aktif = True
                poz_yon = "short"
            
            # Direnç/destek kırılımı — pozisyon yön değiştirme
            elif poz_aktif and poz_yon == "long" and fiyat < dusuk:
                motor.pozisyon_kapat(fiyat, "destek kırılımı")
                poz_aktif = False
                poz_yon = None
            elif poz_aktif and poz_yon == "short" and fiyat > yuksek:
                motor.pozisyon_kapat(fiyat, "direnç kırılımı")
                poz_aktif = False
                poz_yon = None
        
        # Açık pozisyonu kapat
        if poz_aktif:
            motor.pozisyon_kapat(df['Close'].iloc[-1], "zaman doldu")
        
        return motor.rapor()
    
    @staticmethod
    def rsi_mean_reversion(df, motor, kaldırac=5):
        """
        RSI ortalama dönüş stratejisi
        - RSI < 30 → LONG (aşırı satım)
        - RSI > 70 → SHORT (aşırı alım)
        """
        df = df.copy()
        df['RSI'] = Stratejiler._rsi(df['Close'])
        
        poz_aktif = False
        poz_yon = None
        
        for i in range(20, len(df)):
            fiyat = df['Close'].iloc[i]
            rsi = df['RSI'].iloc[i]
            
            if poz_aktif:
                if motor.check_likitasyon(fiyat):
                    poz_aktif = False
                    poz_yon = None
                    continue
            
            # Aşırı satım → LONG
            if not poz_aktif and rsi < 30:
                motor.pozisyon_ac(fiyat, "long")
                motor.stop_loss_ayarla(fiyat * 0.95)
                motor.take_profit_ayarla(fiyat * 1.08)
                poz_aktif = True
                poz_yon = "long"
            
            # Aşırı alım → SHORT
            elif not poz_aktif and rsi > 70:
                motor.pozisyon_ac(fiyat, "short")
                motor.stop_loss_ayarla(fiyat * 1.05)
                motor.take_profit_ayarla(fiyat * 0.92)
                poz_aktif = True
                poz_yon = "short"
            
            # RSI neutral zone'a dönünce kapat
            elif poz_aktif and 40 <= rsi <= 60:
                motor.pozisyon_kapat(fiyat, "RSI nötr")
                poz_aktif = False
                poz_yon = None
        
        if poz_aktif:
            motor.pozisyon_kapat(df['Close'].iloc[-1], "zaman doldu")
        
        return motor.rapor()
    
    @staticmethod
    def _rsi(fiyatlar, period=14):
        """RSI hesapla"""
        import pandas as pd
        delta = pd.Series(fiyatlar).diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss.replace(0, float('nan'))
        rsi = 100 - (100 / (1 + rs))
        return rsi

# ============================================================
# 4. ANA FONKSİYONLAR
# ============================================================
def backtest(coin="BTC-USD", baslangic=1000, kaldırac=10, 
             strateji="breakout", gun=180):
    """Geçmiş veride strateji test et"""
    print(f"\n{'='*50}")
    print(f"📊 BACKTEST: {coin}")
    print(f"{'='*50}")
    print(f"Sermaye: ${baslangic} | Kaldıraç: x{kaldırac} | Strateji: {strateji}")
    
    df = veri_cek(coin, gun)
    if df is None:
        return None
    
    motor = KaldiracMotoru(baslangic, kaldırac)
    
    if strateji == "breakout":
        sonuc = Stratejiler.breakout_emacross(df, motor, kaldırac)
    elif strateji == "rsi":
        sonuc = Stratejiler.rsi_mean_reversion(df, motor, kaldırac)
    else:
        print(f"[HATA] Bilinmeyen strateji: {strateji}")
        return None
    
    return sonuc


def paper_trade(coin="BTC-USD", baslangic=1000, kaldırac=10, 
                strateji="breakout"):
    """Canlı veri ile paper trading"""
    print(f"\n{'='*50}")
    print(f"📊 PAPER TRADING: {coin}")
    print(f"{'='*50}")
    
    # İlk veriyi çek
    df = veri_cek(coin, 30)
    if df is None:
        return None
    
    motor = KaldiracMotoru(baslangic, kaldırac)
    print(f"📡 Paper trading başladı — ${baslangic} | x{kaldırac}")
    print(f"ℹ️  Her 5 dakikada bir güncellenecek. Ctrl+C ile durdur.")
    
    return motor


def format_raporu(sonuc, coin, kaldırac):
    """Raporu formatla"""
    if sonuc is None:
        return None
    
    emoji = "🟢" if sonuc['net_kar_zarar'] > 0 else "🔴"
    
    return f"""
📊 BACKTEST RAPORU — {coin} | x{kaldırac}
{emoji} Net K/Z: ${sonuc['net_kar_zarar']:.2f} (%{sonuc['getiri_yuzde']:+.1f})
━━━━━━━━━━━━━━━━━━━━
💼 Sermaye: ${sonuc['baslangic_sermaye']:.0f} → ${sonuc['son_sermaye']:.2f}
📈 Toplam İşlem: {sonuc['toplam_islem']}
🎯 Win Rate: %{sonuc['win_rate']} ({sonuc['kazanan']}W/{sonuc['kaybeden']}L)
💰 Ort. Kar: ${sonuc['ortalama_kar']:.2f} | Zarar: ${sonuc['ortalama_zarar']:.2f}
📉 Max Drawdown: %{sonuc['max_drawdown']}
⚖️  K/Z Oranı: {sonuc['kar_zarar_orani']}
"""


def coin_listesi_yukle():
    """Kayıtlı coin listesini yükle"""
    import glob
    coin_dosya = os.path.expanduser("~/.hermes/data/coins/coin-listesi.json")
    if os.path.exists(coin_dosya):
        with open(coin_dosya) as f:
            data = json.load(f)
        return data.get('coins', [])
    return []


def coin_bul(sembol):
    """Sembole göre coin ara"""
    coins = coin_listesi_yukle()
    sembol = sembol.upper().replace('-USD', '').replace('-USDT', '')
    for c in coins:
        if c['symbol'] == sembol:
            return c
    return None


def coin_listele():
    """Coin listesini formatlı göster"""
    coins = coin_listesi_yukle()
    if not coins:
        print("❌ Coin listesi bulunamadı. Önce 'python3 coin-listesi.py' çalıştır.")
        return
    
    print(f"\n{'='*50}")
    print(f"🪙 COIN LİSTESİ — {len(coins)} coin (Investing.com + CoinGecko)")
    print(f"{'='*50}")
    print(f"{'Sembol':<8} {'İsim':<20} {'Fiyat':<10} {'24s':<8} {'Hacim':<10}")
    print(f"{'-'*60}")
    
    for c in coins[:40]:
        sembol = c['symbol']
        isim = c['name'][:18]
        fiyat = f"${c['price']:.1f}" if c['price'] > 100 else (f"${c['price']:.4f}" if c['price'] < 0.01 else f"${c['price']:.4f}")
        chg = f"%{c.get('chg_24h', 0):+.2f}" if c.get('chg_24h') else "N/A"
        vol = f"${c.get('vol_24h', 0)/1e6:.0f}M" if c.get('vol_24h') else "N/A"
        print(f"  {sembol:<8} {isim:<20} {fiyat:<10} {chg:<8} {vol:<10}")
    
    print(f"\n  ... ve {len(coins)-40} coin daha")
    print(f"  Kullanım: --coin BTC, --coin XRP, --coin SOL")


def toplu_test(coin_list, baslangic=500, kaldırac=5, strateji="breakout", gun=90):
    """Birden çok coin'de backtest yap"""
    print(f"\n{'='*50}")
    print(f"🔄 TOPLU BACKTEST — {len(coin_list)} coin")
    print(f"{'='*50}")
    print(f"Sermaye: ${baslangic} | Kaldıraç: x{kaldırac} | Strateji: {strateji}")
    print(f"{'='*50}")
    
    sonuclar = []
    for sembol in coin_list:
        try:
            sonuc = backtest(f"{sembol}-USD", baslangic, kaldırac, strateji, gun)
            if sonuc:
                sonuclar.append((sembol, sonuc))
                emoji = "🟢" if sonuc['net_kar_zarar'] > 0 else "🔴"
                print(f"  {emoji} {sembol}: ${sonuc['net_kar_zarar']:.2f} (%{sonuc['getiri_yuzde']:+.1f}) | WR: %{sonuc['win_rate']} | DD: %{sonuc['max_drawdown']}")
        except Exception as e:
            print(f"  ⚠️  {sembol}: HATA — {e}")
    
    # Sıralama
    sonuclar.sort(key=lambda x: x[1]['net_kar_zarar'], reverse=True)
    
    print(f"\n{'='*50}")
    print(f"📊 TOPLU SONUÇ — En iyiden en kötüye")
    print(f"{'='*50}")
    print(f"{'Sembol':<8} {'Net K/Z':<12} {'%':<8} {'WR':<8} {'DD':<8} {'İşlem':<8}")
    print(f"{'-'*50}")
    for sembol, s in sonuclar:
        emoji = "🟢" if s['net_kar_zarar'] > 0 else "🔴"
        print(f"{emoji} {sembol:<6} ${s['net_kar_zarar']:<8.2f} %{s['getiri_yuzde']:<+5.1f} %{s['win_rate']:<5.1f} %{s['max_drawdown']:<5.1f} {s['toplam_islem']:<5}")
    
    # Kazanan/kaybeden
    kazanan = sum(1 for _, s in sonuclar if s['net_kar_zarar'] > 0)
    print(f"\n📈 Kazanan: {kazanan}/{len(sonuclar)} (%{kazanan/len(sonuclar)*100:.0f})")
    
    return sonuclar


def main():
    parser = argparse.ArgumentParser(description='Kaldıraçlı İşlem Simülatörü')
    parser.add_argument('--coin', default='BTC-USD', help='Coin (BTC, XRP, ETH, SOL, SUI veya "list" tüm coinleri göster)')
    parser.add_argument('--baslangic', type=float, default=1000, help='Başlangıç sermayesi ($)')
    parser.add_argument('--kaldırac', type=int, default=10, help='Kaldıraç (2-100)')
    parser.add_argument('--short', action='store_true', help='Short strateji test et')
    parser.add_argument('--strateji', default='breakout', choices=['breakout', 'rsi'], help='Strateji')
    parser.add_argument('--gun', type=int, default=180, help='Test edilecek gün sayısı')
    parser.add_argument('--rapor', action='store_true', help='Önceki raporları listele')
    parser.add_argument('--karsilastir', action='store_true', help='Tüm stratejileri karşılaştır')
    parser.add_argument('--top-test', type=int, default=0, help='İlk N coin\'de toplu backtest yap')
    parser.add_argument('--hedef-coinler', type=str, default='', help='Virgülle ayrılmış coin listesi (XRP,SOL,ETH,SUI)')
    
    args = parser.parse_args()
    
    if args.rapor:
        import glob
        raporlar = glob.glob(os.path.join(RAPOR_DIZINI, "*.json"))
        print(f"\n📁 {len(raporlar)} kayıtlı test raporu:")
        for r in sorted(raporlar)[-10:]:
            with open(r) as f:
                data = json.load(f)
            emoji = "🟢" if data.get('net_kar_zarar', 0) > 0 else "🔴"
            print(f"{emoji} {os.path.basename(r)} — ${data.get('net_kar_zarar', 0):.2f}")
        return
    
    # Coin listesini göster
    if args.coin.lower() == 'list':
        coin_listele()
        return
    
    # Toplu test
    if args.top_test > 0:
        coins = coin_listesi_yukle()
        semboller = [c['symbol'] for c in coins[:args.top_test] 
                     if c['symbol'] not in ['USDT', 'USDC', 'DAI', 'USDS', 'USD1', 'USDE', 'USDG', 'USYC', 'FDUSD', 'TUSD', 'BUSD', 'FRAX', 'LUSD', 'EURS', 'CEUR', 'EURC', 'PYUSD', 'GUSD', 'PAXG', 'XAUT', 'WBT']]
        # Stablecoin'leri filtrele
        stablecoinler = {'USDT', 'USDC', 'DAI', 'USDS', 'USD1', 'USDE', 'USDG', 'USYC', 'FDUSD', 'TUSD', 'BUSD', 'FRAX', 'LUSD', 'EURS', 'CEUR', 'EURC', 'PYUSD', 'GUSD', 'PAXG', 'XAUT', 'WBT', 'LEO', 'RAIN', 'FIGR_HELOC'}
        semboller = [s for s in semboller if s not in stablecoinler][:args.top_test]
        toplu_test(semboller, args.baslangic, args.kaldırac, args.strateji, args.gun)
        return
    
    # Virgülle ayrılmış coin listesi
    if args.hedef_coinler:
        semboller = [s.strip().upper() for s in args.hedef_coinler.split(',')]
        toplu_test(semboller, args.baslangic, args.kaldırac, args.strateji, args.gun)
        return
    
    if args.karsilastir:
        # Tüm stratejileri karşılaştır
        print(f"\n{'='*50}")
        print(f"🔄 STRATEJİ KARŞILAŞTIRMASI — {args.coin}")
        print(f"{'='*50}")
        
        for strat in ['breakout', 'rsi']:
            sonuc = backtest(args.coin, args.baslangic, args.kaldırac, strat, args.gun)
            if sonuc:
                print(format_raporu(sonuc, args.coin, args.kaldırac))
        
        # Farklı kaldıraçları da test et
        print(f"\n🔄 KALDIRAÇ KARŞILAŞTIRMASI — {args.coin}")
        for k in [1, 3, 5, 10, 20]:
            sonuc = backtest(args.coin, args.baslangic, k, "breakout", args.gun)
            if sonuc:
                emoji = "🟢" if sonuc['net_kar_zarar'] > 0 else "🔴"
                print(f"  x{k}: {emoji} ${sonuc['net_kar_zarar']:.2f} | WR: %{sonuc['win_rate']} | DD: %{sonuc['max_drawdown']}")
        return
    
    # Tek test
    sonuc = backtest(args.coin, args.baslangic, args.kaldırac, args.strateji, args.gun)
    if sonuc:
        # Raporu kaydet
        rapor_dosya = os.path.join(RAPOR_DIZINI, f"{args.coin}_{args.strateji}_x{args.kaldırac}_{datetime.now().strftime('%Y%m%d_%H%M')}.json")
        with open(rapor_dosya, 'w') as f:
            json.dump(sonuc, f, indent=2)
        
        print(format_raporu(sonuc, args.coin, args.kaldırac))
        print(f"📁 Rapor kaydedildi: {rapor_dosya}")


if __name__ == '__main__':
    main()
