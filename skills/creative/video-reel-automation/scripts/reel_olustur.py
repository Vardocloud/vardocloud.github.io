#!/usr/bin/env python3
"""
Instagram Reel Oluşturucu — MoviePy + FFmpeg
Ücretsiz araçlar: MoviePy, FFmpeg, Pixabay

Kullanım:
  python3 reel_olustur.py --images /path/to/photos/ --output reel.mp4 --music fon.mp3

Not: font parametresi için ~/.fonts/CormorantGaramond-Bold.ttf (slogan için)
ve ~/.fonts/Montserrat-SemiBold.ttf (alt başlık için) önerilir.
"""
import os, sys, glob, argparse
from pathlib import Path
import numpy as np

def create_reel(image_folder=".", output_path="reel_cikti.mp4",
                slogan="Siz isteyin, biz yapalım.",
                alt_baslik="İç Mimarlık & Dekorasyon Tasarım",
                iletisim="", music_path=None, duration=90,
                font_serif=None, font_sans=None):
    """
    Fotoğraflardan Instagram Reel (9:16) oluşturur.
    
    Parameters:
        font_serif: Serif font yolu (slogan/başlık için, örn. Cormorant Garamond Bold)
        font_sans: Sans-serif font yolu (alt başlık için, örn. Montserrat SemiBold)
    """
    try:
        from moviepy import (ImageClip, TextClip, CompositeVideoClip,
                             AudioFileClip, concatenate_videoclips, vfx, afx, VideoClip)
    except ImportError:
        from moviepy.editor import (ImageClip, TextClip, CompositeVideoClip,
                                    AudioFileClip, concatenate_videoclips, vfx, afx)
        from moviepy.video.VideoClip import VideoClip

    # Font seçimi
    home = os.path.expanduser("~")
    FONT_SERIF = font_serif or os.path.join(home, ".fonts", "CormorantGaramond-Bold.ttf")
    FONT_SANS = font_sans or os.path.join(home, ".fonts", "Montserrat-SemiBold.ttf")
    
    # Font kontrol
    for label, path in [("Serif", FONT_SERIF), ("Sans", FONT_SANS)]:
        if not os.path.exists(path):
            # Fallback to Montserrat Bold if SemiBold missing
            alt = path.replace("SemiBold", "Bold")
            if os.path.exists(alt):
                if "SemiBold" in path:
                    FONT_SANS = alt
                continue
            print(f"⚠️  {label} font bulunamadı: {path}")

    # Görselleri bul
    exts = ('*.jpg', '*.jpeg', '*.png', '*.webp')
    images = []
    for e in exts:
        images.extend(sorted(glob.glob(os.path.join(image_folder, e))))
    if not images:
        print(f"HATA: {image_folder} içinde görsel bulunamadı.", file=sys.stderr)
        sys.exit(1)
    print(f"✓ {len(images)} görsel")

    W, H = 1080, 1920  # 9:16
    per_clip = min(duration / len(images), 8)
    total_t = per_clip * len(images)

    # Renkler
    GOLD = "#D4AF37"
    WHITE = "#FFFFFF"

    # Her görsel için clip
    clips = []
    for i, p in enumerate(images):
        print(f"  {os.path.basename(p)}")
        c = ImageClip(p, duration=per_clip)
        iw, ih = c.size
        target_ratio = W / H
        if iw / ih > target_ratio:
            c = c.resized(height=H).cropped(x_center=c.w / 2, width=W)
        else:
            c = c.resized(width=W).cropped(y_center=c.h / 2, height=H)
        if i > 0:
            c = c.with_effects([vfx.CrossFadeIn(min(0.5, per_clip * 0.15))])
        clips.append(c)
    final = concatenate_videoclips(clips, method="compose")

    # --- METIN OVERLAY'LERI ---
    text_clips = []

    # Gradient (alt kısım - hafif, mekan görünsün)
    gradient_height = int(H * 0.30)
    gradient_start = H * 0.70

    def make_gradient(t):
        frame = np.zeros((gradient_height, W, 3), dtype=np.uint8)
        for y in range(gradient_height):
            alpha = y / gradient_height
            val = int(alpha * 80)
            frame[y, :, :] = val
        return frame

    grad = VideoClip(make_gradient, duration=total_t)
    grad = grad.with_position((0, gradient_start)).with_opacity(0.45)
    text_clips.append(grad)

    # Açılış metni (ilk 3sn)
    acilis = TextClip(
        text="İç Mimarlık & Dekorasyon",
        font=FONT_SERIF, font_size=56, color=GOLD,
        stroke_color="black", stroke_width=1,
        text_align="center", size=(int(W * 0.9), None),
    )
    acilis = acilis.with_duration(min(3, per_clip * 1.5)) \
        .with_position(("center", int(H * 0.25))) \
        .with_effects([vfx.FadeIn(0.5), vfx.FadeOut(0.5)])
    text_clips.append(acilis)

    # Dekoratif altın çizgi
    if alt_baslik or slogan:
        try:
            line = VideoClip(
                lambda t: np.full((2, int(W * 0.3), 3), [212, 175, 55], dtype=np.uint8),
                duration=total_t
            )
            line = line.with_position((W // 2 - int(W * 0.15), int(H * 0.74))) \
                .with_opacity(0.6)
            text_clips.append(line)
        except:
            pass

    # Alt başlık
    if alt_baslik:
        alt = TextClip(
            text=alt_baslik, font=FONT_SANS, font_size=34,
            color=WHITE, stroke_color="black", stroke_width=1,
            text_align="center", size=(int(W * 0.85), None),
        )
        alt = alt.with_position(("center", int(H * 0.77))) \
            .with_duration(min(90, total_t)) \
            .with_effects([vfx.FadeIn(1.5)])
        text_clips.append(alt)

    # Slogan
    if slogan:
        sl = TextClip(
            text=slogan, font=FONT_SERIF, font_size=56, color=GOLD,
            stroke_color="black", stroke_width=1,
            text_align="center", size=(int(W * 0.85), None),
        )
        sl = sl.with_position(("center", int(H * 0.85))) \
            .with_duration(min(60, total_t)) \
            .with_effects([vfx.FadeIn(1.0)])
        text_clips.append(sl)

    # İletişim (son 5sn)
    if iletisim:
        son = min(5, total_t)
        ic = TextClip(
            text=iletisim, font=FONT_SANS, font_size=34, color=WHITE,
            stroke_color="black", stroke_width=1,
            text_align="center", size=(int(W * 0.85), None),
        )
        ic = ic.with_duration(son) \
            .with_position(("center", int(H * 0.90))) \
            .with_start(max(0, total_t - son)) \
            .with_effects([vfx.FadeIn(0.5)])
        text_clips.append(ic)

    print("✓ Metin overlay'leri hazır.")

    # Müzik
    audio = None
    if music_path and os.path.exists(music_path):
        ac = AudioFileClip(music_path)
        if ac.duration < total_t:
            loops = int(total_t / ac.duration) + 1
            ac = ac.with_effects([afx.AudioLoop(loops=loops)])
        ac = ac.with_duration(total_t)
        ac = ac.with_effects([afx.AudioFadeIn(2.0), afx.MultiplyVolume(0.7)])
        audio = ac
        print("✓ Müzik ayarlandı.")

    # Render
    all_clips = [final] + text_clips
    final = CompositeVideoClip(all_clips, size=(W, H))
    if audio:
        final = final.with_audio(audio)

    print(f"🎬 Render: {output_path} ({total_t:.1f}s)...")
    final.write_videofile(output_path, codec="libx264", audio_codec="aac",
                          fps=24, preset="medium", bitrate="4000k", threads=4)
    final.close()
    size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"✅ {output_path} ({size_mb:.1f}MB, {total_t:.0f}s)")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Instagram Reel Oluşturucu")
    p.add_argument("--images", default=".", help="Görsel klasörü")
    p.add_argument("--output", default="reel_cikti.mp4", help="Çıktı MP4 yolu")
    p.add_argument("--slogan", default="Siz isteyin, biz yapalım.", help="Ana slogan")
    p.add_argument("--alt-baslik", default="İç Mimarlık & Dekorasyon Tasarım", help="Alt başlık")
    p.add_argument("--iletisim", default="", help="İletişim bilgisi (son 5sn)")
    p.add_argument("--music", default=None, help="Müzik dosyası yolu")
    p.add_argument("--sure", type=int, default=90, help="Toplam süre (saniye)")
    p.add_argument("--font-serif", default=None, help="Serif font yolu (slogan/başlık)")
    p.add_argument("--font-sans", default=None, help="Sans-serif font yolu (alt başlık)")
    args = p.parse_args()
    create_reel(args.images, args.output, args.slogan,
                args.alt_baslik, args.iletisim, args.music, args.sure,
                args.font_serif, args.font_sans)
