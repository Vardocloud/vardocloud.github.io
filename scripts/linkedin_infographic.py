#!/usr/bin/env python3
"""LinkedIn infographic/tablo üretimi — APA verilerini görselleştirir."""
import sys, json, os, textwrap
from PIL import Image, ImageDraw, ImageFont

def wrap_text(draw, text, font, max_width):
    """Metni max_width piksele sığacak şekilde satırlara böl."""
    words = text.split()
    lines = []
    current = ""
    for w in words:
        test = current + " " + w if current else w
        bb = draw.textbbox((0, 0), test, font=font)
        if bb[2] - bb[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines

def create_infographic(data_points, output_path="/tmp/gorsel.jpg"):
    """Bir infographic görsel oluşturur.
    
    data_points: [{"number": "100+", "label": "Randomize kontrollü çalışma", 
                    "sub": "CBT-I'yi destekliyor (Blom ve ark., 2017)"}, ...]
    """
    W, H = 1200, 628
    img = Image.new("RGB", (W, H), (245, 240, 235))  # Warm krem arka plan
    
    draw = ImageDraw.Draw(img)
    
    # Fontları yükle
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_number = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
        font_source = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except:
        font_title = ImageFont.load_default()
        font_number = ImageFont.load_default()
        font_label = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_source = ImageFont.load_default()
    
    # Üst başlık
    title = "UYKU & RUH SAĞLIĞI"
    subtitle = "APA Monitor on Psychology · Haziran 2026"
    
    tt_bb = draw.textbbox((0, 0), title, font=font_title)
    draw.text(((W - (tt_bb[2]-tt_bb[0]))//2, 25), title, fill=(40, 35, 30), font=font_title)
    
    ts_bb = draw.textbbox((0, 0), subtitle, font=font_label)
    draw.text(((W - (ts_bb[2]-ts_bb[0]))//2, 62), subtitle, fill=(120, 110, 100), font=font_label)
    
    # Çizgi
    draw.line([(80, 92), (W-80, 92)], fill=(200, 190, 180), width=1)
    
    # Kart düzeni — 3 üst, 2 alt (veya hepsi esnek)
    cards = len(data_points)
    if cards <= 3:
        cols = cards
        rows = 1
    elif cards <= 5:
        cols = 3
        rows = 2
    else:
        cols = 3
        rows = (cards + 2) // 3
    
    card_w = 340
    card_h = 190
    start_y = 115
    gap_x = 30
    gap_y = 20
    
    total_w = cols * card_w + (cols - 1) * gap_x
    start_x = (W - total_w) // 2
    
    colors = [
        (70, 130, 180),   # Steel blue
        (180, 100, 70),   # Rust
        (60, 150, 120),   # Teal
        (160, 120, 60),   # Gold
        (140, 80, 140),   # Purple
        (70, 150, 150),   # Cyan
    ]
    
    for i, dp in enumerate(data_points[:6]):
        col = i % cols
        row = i // cols
        
        x = start_x + col * (card_w + gap_x)
        y = start_y + row * (card_h + gap_y)
        
        bg_color = colors[i % len(colors)]
        light_bg = tuple(min(c + 60, 255) for c in bg_color)
        
        # Kart arka planı
        draw.rounded_rectangle([x, y, x+card_w, y+card_h], radius=12, fill=(255, 255, 255), outline=bg_color, width=2)
        
        # Sol renk şeridi
        draw.rounded_rectangle([x+2, y+2, x+8, y+card_h-2], radius=3, fill=bg_color)
        
        # Numara
        num = dp.get("number", "")
        nb = draw.textbbox((0, 0), num, font=font_number)
        draw.text((x + 22, y + 12), num, fill=bg_color, font=font_number)
        
        # Label (ana metin)
        label = dp.get("label", "")
        label_lines = wrap_text(draw, label, font_label, card_w - 40)
        ly = y + 75
        for line in label_lines[:2]:
            draw.text((x + 22, ly), line, fill=(60, 55, 50), font=font_label)
            ly += 22
        
        # Sub (açıklama)
        sub = dp.get("sub", "")
        sub_lines = wrap_text(draw, sub, font_sub, card_w - 40)
        sy = y + card_h - 52
        for line in sub_lines[:2]:
            draw.text((x + 22, sy), line, fill=(120, 115, 110), font=font_sub)
            sy += 18
        
        # Kaynak
        src = dp.get("source", "")
        if src:
            draw.text((x + 22, y + card_h - 22), src, fill=(160, 155, 150), font=font_source)
    
    # Alt bilgi
    footer = "bardopsikoloji.com.tr"
    fb = draw.textbbox((0, 0), footer, font=font_source)
    draw.text(((W - (fb[2]-fb[0]))//2, H - 18), footer, fill=(180, 175, 170), font=font_source)
    
    img.save(output_path, "JPEG", quality=92)
    return output_path

def main():
    # JSON verisini argv[1]'den veya stdin'den al
    if len(sys.argv) > 1:
        data = json.loads(sys.argv[1])
    else:
        data = json.load(sys.stdin)
    
    path = create_infographic(data)
    print(f"MEDIA:{path}")

if __name__ == "__main__":
    main()
