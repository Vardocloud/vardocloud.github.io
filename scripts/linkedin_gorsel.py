#!/usr/bin/env python3
"""LinkedIn görsel üretimi — Pollinations API ile."""
import sys, requests, json, os

def gorsel_uret(prompt):
    api_key = os.environ.get("POLLINATIONS_API_KEY", "").strip()
    
    full_prompt = f"{prompt}, minimalist professional illustration, clean geometric shapes, warm pastel tones, soft gradients, no text no letters no words no watermarks"
    
    # Pollinations image generation API (POST)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "kontext",
        "width": 1200,
        "height": 628,
        "prompt": full_prompt,
        "nologo": True,
        "safe": False
    }
    
    resp = requests.post(
        "https://gen.pollinations.ai/v1/images/generate",
        headers=headers, json=payload, timeout=45
    )
    
    if resp.status_code == 200:
        data = resp.json()
        # Response structure varies — find the image URL
        img_url = None
        if isinstance(data, dict):
            img_url = data.get("url") or data.get("image_url") or data.get("data", {}).get("url")
        if not img_url:
            # Download the response content directly if it's binary
            path = "/tmp/gorsel.jpg"
            with open(path, "wb") as f:
                f.write(resp.content)
            size = os.path.getsize(path)
            if size > 5000:
                print(f"MEDIA:{path}")
                sys.exit(0)
    
    # Fallback: GET request with URL parameters
    from urllib.parse import quote
    url = f"https://gen.pollinations.ai/image/{quote(full_prompt)}?width=1200&height=628&model=kontext&nologo=true"
    resp2 = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=45)
    
    if resp2.status_code == 200 and len(resp2.content) > 5000:
        path = "/tmp/gorsel.jpg"
        with open(path, "wb") as f:
            f.write(resp2.content)
        print(f"MEDIA:{path}")
        sys.exit(0)
    
    print(f"HATA: tüm yöntemler başarısız. Son yanıt: {resp2.status_code} - {resp2.text[:200]}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: linkedin_gorsel.py 'prompt metni'", file=sys.stderr)
        sys.exit(1)
    gorsel_uret(sys.argv[1])
