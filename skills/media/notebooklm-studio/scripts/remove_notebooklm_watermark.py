#!/usr/bin/env python3
"""
NotebookLM Watermark Remover — Column-by-Column Background Sampling
Kullanım: python3 remove_notebooklm_watermark.py <input.pdf> [output.pdf]

Varsayılan output: <input>_clean.pdf
"""
import sys, os, fitz

def remove_watermark(input_path, output_path=None):
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_clean.pdf"
    
    doc = fitz.open(input_path)
    out_doc = fitz.open()
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        rect = page.rect
        w, h = rect.width, rect.height
        
        # Watermark konumu (PDF biriminde)
        wm_x0 = w - 180
        wm_y0 = h - 45
        wm_x1 = w - 5
        wm_y1 = h - 5
        sample_y0 = wm_y0 - 15
        sample_y1 = wm_y0
        
        for col in range(int(wm_x0), int(wm_x1)):
            sample_rect = fitz.Rect(col, sample_y0, col + 1, sample_y1)
            cover_rect = fitz.Rect(col, wm_y0, col + 1, wm_y1)
            
            samples = page.get_pixmap(dpi=72, clip=sample_rect)
            if samples.n > 0:
                r, g, b = samples.samples[0], samples.samples[1], samples.samples[2]
                annot = page.add_rect_annot(cover_rect)
                annot.set_colors(stroke=None, fill=(r/255, g/255, b/255))
                annot.set_border(width=0)
                annot.update()
        
        out_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
    
    out_doc.save(output_path, garbage=4, deflate=True, clean=True)
    out_doc.close()
    doc.close()
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: python3 remove_notebooklm_watermark.py <input.pdf> [output.pdf]", file=sys.stderr)
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_path):
        print(f"Hata: {input_path} bulunamadı", file=sys.stderr)
        sys.exit(1)
    
    result = remove_watermark(input_path, output_path)
    print(f"✅ Watermark temizlendi: {result}")
