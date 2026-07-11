#!/usr/bin/env python3
"""
YouTube Ekonomi Kanalları — Son Videoları Çek + Transkript
Günde 1 kere çalışır. RSS + Transcript ile çalışır, API key gerekmez.
v2.0 — 1 Temmuz 2026: Transkript çekme + Yatırım 101 öncelikli
"""

import json
import urllib.request
import xml.etree.ElementTree as ET
import sys
import os
from datetime import datetime, timezone

KANALLAR = {
    "Kayıt Dışı İktisat (Ceyhun Elgin)": "UCFrDHMXMBvxkPryv1qRxhtw",
    "Yatırım 101": "UCWsudnBrEOJLQ1JpkdloxKg",
    "Kendine Milyoner": "UCjdUCRPvoqvTVBJZfEZrd1A",
    "Borsadan Hisse": "UC2n7FaAFNuIpR9Ul3R_MGuw",
    "Mark Tilbury": "UCxgAuX3XZROujMmGphN_scA",
}

ONCELIKLI_KANALLAR = ["Yatırım 101"]  # Bu kanalların transkripti de çekilir

DATA_DIR = os.path.expanduser("~/.hermes/data/youtube")
TRANSCRIPT_DIR = os.path.join(DATA_DIR, "transcripts")
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

# Daha önce işlenmiş video ID'lerini takip et
STATE_FILE = os.path.join(DATA_DIR, "islenen_videolar.json")


def yukle_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"islenen": []}


def kaydet_state(islenen):
    with open(STATE_FILE, "w") as f:
        json.dump({"islenen": islenen}, f, ensure_ascii=False, indent=2)


def rss_fetch(channel_id):
    """Bir kanalın RSS feed'inden son 15 videoyu çek"""
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            tree = ET.parse(resp)
            root = tree.getroot()

        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)

        videos = []
        for entry in entries:
            title = entry.find("atom:title", ns)
            vid_elem = entry.find("atom:videoId", ns)
            published = entry.find("atom:published", ns)
            link = entry.find("atom:link", ns)

            video_id = vid_elem.text if vid_elem is not None else ""
            video_url = f"https://youtu.be/{video_id}" if video_id else ""

            videos.append({
                "title": title.text if title is not None else "",
                "video_id": video_id,
                "url": video_url,
                "published": published.text if published is not None else "",
            })

        return videos

    except Exception as e:
        return {"error": str(e)}


def transcript_cek(video_id):
    """YouTubeTranscriptApi ile video transkriptini çek"""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        # Önce Türkçe dene, olmazsa İngilizce
        transcript = api.fetch(video_id, languages=['tr', 'en'])
        if transcript:
            metin = " ".join([seg.text for seg in transcript])
            return {"durum": "basarili", "metin": metin[:8000], "segment_sayisi": len(transcript)}
        return {"durum": "altyazi_yok"}
    except Exception as e:
        hata = str(e)
        if "Subtitles are disabled" in hata:
            return {"durum": "altyazi_yok"}
        return {"durum": "hata", "hata": hata[:100]}


def main():
    bugun = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    state = yukle_state()
    islenen = state["islenen"]

    output = {
        "timestamp": datetime.now().isoformat(),
        "kanallar": {},
        "ozet": {"toplam_kanal": 0, "toplam_video": 0, "hata": 0, "yeni_transkript": 0}
    }

    for kanal_adi, channel_id in KANALLAR.items():
        print(f"  📡 {kanal_adi}...", end=" ")
        sys.stdout.flush()

        videos = rss_fetch(channel_id)

        if isinstance(videos, dict) and "error" in videos:
            print(f"❌ {videos['error'][:40]}")
            output["kanallar"][kanal_adi] = {"durum": "hata", "hata": videos["error"]}
            output["ozet"]["hata"] += 1
            continue

        # Bugünkü videoları bul
        bugunku_videolar = [v for v in videos if v.get("published", "")[:10] == bugun]
        bugun_yeni_sayisi = len(bugunku_videolar)

        # Öncelikli kanallar için transkript çek
        yeni_transkript = 0
        if kanal_adi in ONCELIKLI_KANALLAR:
            for v in videos:
                vid = v["video_id"]
                if vid and vid not in islenen:
                    # Transkript çek
                    sonuc = transcript_cek(vid)
                    v["transkript"] = sonuc
                    if sonuc.get("durum") == "basarili":
                        yeni_transkript += 1
                        islenen.append(vid)
                        # Transkripti dosyaya kaydet
                        tarih = v.get("published", bugun)[:10]
                        dosya_adi = f"{tarih}_{kanal_adi.replace(' ','_')}_{vid}.json"
                        dosya_yolu = os.path.join(TRANSCRIPT_DIR, dosya_adi)
                        with open(dosya_yolu, "w") as f:
                            json.dump({
                                "kanal": kanal_adi,
                                "title": v["title"],
                                "url": v["url"],
                                "published": v["published"],
                                "transkript": sonuc["metin"],
                                "cekilme_tarihi": bugun,
                            }, f, ensure_ascii=False, indent=2)
                    elif sonuc.get("durum") == "altyazi_yok":
                        # Altyazı yoksa da işlenmiş say (tekrar denemesin)
                        islenen.append(vid)

        toplam_video = len(videos)
        output["kanallar"][kanal_adi] = {
            "durum": "basarili",
            "channel_id": channel_id,
            "bugun_yeni": bugun_yeni_sayisi,
            "yeni_transkript": yeni_transkript,
            "videolar": videos[:10],
        }
        output["ozet"]["toplam_kanal"] += 1
        output["ozet"]["toplam_video"] += toplam_video
        output["ozet"]["yeni_transkript"] += yeni_transkript

        print(f"✅ {toplam_video} video (bugün: {bugun_yeni_sayisi}, transkript: {yeni_transkript})")

    # State kaydet
    kaydet_state(islenen)

    # Özet
    print(f"\n{'='*50}")
    print(f"  📺 YouTube Ekonomi Taraması — {datetime.now().strftime('%d %B %Y %H:%M')}")
    print(f"{'='*50}")
    print(f"  Başarılı kanal: {output['ozet']['toplam_kanal']}/{len(KANALLAR)}")
    print(f"  Toplam video:   {output['ozet']['toplam_video']}")
    print(f"  Yeni transkript: {output['ozet']['yeni_transkript']}")
    print(f"  Hata:           {output['ozet']['hata']}")

    # Bugün yeni video varsa göster
    yeni_videolar = []
    for kanal, data in output["kanallar"].items():
        if data.get("durum") == "basarili" and data.get("bugun_yeni", 0) > 0:
            for v in data.get("videolar", []):
                if v.get("published", "")[:10] == bugun:
                    yeni_videolar.append((kanal, v))

    if yeni_videolar:
        print(f"\n  🆕 BUGÜN YENİ VİDEOLAR:")
        for kanal, v in yeni_videolar[:5]:
            print(f"  • [{kanal}] {v['title'][:80]}")
            print(f"    {v['url']}")

    # JSON çıktı
    with open("/tmp/youtube_tarama_son.json", "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Transkript dosyalarının listesini de ayrı bir JSON'a yaz
    transkript_listesi = []
    for fname in os.listdir(TRANSCRIPT_DIR):
        if fname.endswith(".json"):
            fpath = os.path.join(TRANSCRIPT_DIR, fname)
            with open(fpath) as f:
                data = json.load(f)
            transkript_listesi.append({
                "dosya": fname,
                "kanal": data["kanal"],
                "title": data["title"],
                "url": data["url"],
                "published": data["published"],
                "cekilme_tarihi": data["cekilme_tarihi"],
            })

    transkript_listesi.sort(key=lambda x: x.get("published", ""), reverse=True)
    with open(os.path.join(DATA_DIR, "transkript_listesi.json"), "w") as f:
        json.dump(transkript_listesi, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
