#!/usr/bin/env python3
"""LinkedIn infographic/tablo üretimi — APA verilerini görselleştirir.
Kullanım: linkedin_infographic.py 'JSON_DATA'
  JSON_DATA: [{"number": "...", "label": "...", "sub": "...", "source": "..."}]
Çıktı: MEDIA:/tmp/gorsel.jpg
"""
import sys, json, os
from PIL import Image, ImageDraw, ImageFont

def wrap_text(draw, text, font, max_width):
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
    W, H = 1200, 628
    img = Image.new("RGB", (W, H), (245, 240, 235))
    draw = ImageDraw.Draw(img)

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

    draw.text(((W - draw.textbbox((0, 0), "UYKU & RUH SAĞLIĞI", font=font_title)[2])//2, 25),
              "UYKU & RUH SAĞLIĞI", fill=(40, 35, 30), font=font_title)
    draw.text(((W - draw.textbbox((0, 0), "APA Monitor on Psychology", font=font_label)[2])//2, 62),
              "APA Monitor on Psychology", fill=(120, 110, 100), font=font_label)
    draw.line([(80, 92), (W-80, 92)], fill=(200, 190, 180), width=1)

    cards = len(data_points)
    cols = min(cards, 3)
    rows = (cards + cols - 1) // cols
    card_w, card_h = 340, 190
    start_y = 115
    gap_x, gap_y = 30, 20
    start_x = (W - (cols * card_w + (cols - 1) * gap_x)) // 2
    colors = [(70, 130, 180), (180, 100, 70), (60, 150, 120), (160, 120, 60), (140, 80, 140), (70, 150, 150)]

    for i, dp in enumerate(data_points[:6]):
        col = i % cols
        row = i // cols
        x = start_x + col * (card_w + gap_x)
        y = start_y + row * (card_h + gap_y)
        c = colors[i % 6]
        draw.rounded_rectangle([x, y, x+card_w, y+card_h], radius=12, fill=(255, 255, 255), outline=c, width=2)
        draw.rounded_rectangle([x+2, y+2, x+8, y+card_h-2], radius=3, fill=c)
        draw.text((x+22, y+12), dp.get("number",""), fill=c, font=font_number)
        for j, line in enumerate(wrap_text(draw, dp.get("label",""), font_label, card_w-40)[:2]):
            draw.text((x+22, y+75+j*22), line, fill=(60,55,50), font=font_label)
        for j, line in enumerate(wrap_text(draw, dp.get("sub",""), font_sub, card_w-40)[:2]):
            draw.text((x+22, y+card_h-52+j*18), line, fill=(120,115,110), font=font_sub)
        src = dp.get("source","")
        if src:
            draw.text((x+22, y+card_h-22), src, fill=(160,155,150), font=font_source)

    fb = draw.textbbox((0, 0), "bardopsikoloji.com.tr", font=font_source)
    draw.text(((W - (fb[2]-fb[0]))//2, H-18), "bardopsikoloji.com.tr", fill=(180,175,170), font=font_source)
    img.save(output_path, "JPEG", quality=92)
    return output_path

if __name__ == "__main__":
    data = json.loads(sys.argv[1]) if len(sys.argv) > 1 else json.load(sys.stdin)
    path = create_infographic(data)
    print(f"MEDIA:{path}")
