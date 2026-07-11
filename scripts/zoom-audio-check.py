#!/usr/bin/env python3
"""
zoom-audio-check.py — Kayıt sırasında periyodik ses kontrolü

Kullanım:
  python3 zoom-audio-check.py <kayit_dosyasi.mp3> [esik_db]

30 Haz 2026'da Miuul kaydının sessiz çıkmasına sebep olan hatayı
erken tespit etmek için tasarlandı.

ffprobe ile volumedetect yapar:
  - mean_volume < -60 dB  → ❌ SESSİZ (acil müdahale gerek)
  - -60dB < mean < -30dB  → ⚠️ DÜŞÜK (Chrome sesini kontrol et)
  - mean > -30dB          → ✅ NORMAL

Exit code:
  0 = ses var (normal)
  1 = çok düşük (uyarı)
  2 = sessiz (acil müdahale)
  3 = ffprobe hatası / dosya yok
"""

import sys
import subprocess
import json
import re
import os

def get_mean_volume(filepath):
    """ffprobe ile mean_volume değerini al."""
    if not os.path.exists(filepath):
        return None, f"Dosya bulunamadı: {filepath}"
    
    try:
        result = subprocess.run(
            ["ffprobe", "-i", filepath, "-af", "volumedetect", 
             "-f", "null", "-"],
            capture_output=True, text=True, timeout=30
        )
        output = result.stderr + result.stdout
        
        # mean_volume değerini bul
        match = re.search(r'mean_volume:\s*([-\d.]+)\s*dB', output)
        if match:
            return float(match.group(1)), output
        else:
            # Dosya çok kısaysa volumedetect çalışmayabilir
            return None, output
    except subprocess.TimeoutExpired:
        return None, "ffprobe timeout"
    except FileNotFoundError:
        return None, "ffprobe bulunamadı"

def check_recording_active(filepath):
    """Kayıt hâlâ devam ediyor mu? ffmpeg process'ini kontrol et."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "ffmpeg.*zoom_rec"],
            capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except:
        return False

def main():
    if len(sys.argv) < 2:
        print("Kullanım: zoom-audio-check.py <kayit_dosyasi.mp3> [esik_db]")
        sys.exit(3)
    
    filepath = sys.argv[1]
    threshold = float(sys.argv[2]) if len(sys.argv) > 2 else -60.0
    
    mean_db, output = get_mean_volume(filepath)
    
    recording_active = check_recording_active(filepath)
    
    if mean_db is None:
        if recording_active:
            print(f"⏳ Kayıt devam ediyor — ses seviyesi henüz ölçülemiyor (dosya çok kısa)")
            sys.exit(0)  # Henüz erken, hata sayma
        else:
            print(f"❌ Ses seviyesi ölçülemedi, ffmpeg çalışmıyor")
            print(f"--- ffprobe çıktısı ---\n{output}\n---")
            sys.exit(3)
    
    if mean_db < threshold:
        if recording_active:
            print(f"🔴 SESSİZ KAYIT TESPİTİ ({mean_db:.1f} dB) — ffmpeg çalışıyor ama ses gelmiyor!")
            print(f"   Olası neden: PULSE_SINK yanlış, Chrome çökmüş, toplantı bitmiş")
            print(f"   Öneri: Chrome tab'larını kontrol et, gerekirse yeniden başlat")
        else:
            print(f"🔴 SESSİZ KAYIT ({mean_db:.1f} dB) — ffmpeg çalışmıyor")
        sys.exit(2)
    elif mean_db < -30:
        print(f"⚠️  DÜŞÜK SES ({mean_db:.1f} dB) — kayıt devam ediyor, takip et")
        sys.exit(1)
    else:
        print(f"✅ SES NORMAL ({mean_db:.1f} dB)")
        sys.exit(0)

if __name__ == "__main__":
    main()
