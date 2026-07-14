#!/usr/bin/env python3
"""
Pollinations Image Generation Helper Script
Usage: python3 generate_image.py "prompt" [--model kontext] [--width 1024] [--height 1024] [--reference URL] [--output /path/to/image.jpg]
"""

import argparse
import os
import sys
import urllib.parse
import httpx

def get_api_key():
    """Read API key from .env file"""
    env_path = '/home/ubuntu/.hermes/.env'
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('POLLINATIONS_API_KEY='):
                return line.split('=', 1)[1].strip()
    raise RuntimeError("POLLINATIONS_API_KEY not found in .env")

def generate_image(prompt, model='kontext', width=1024, height=1024, reference_url=None, output_path=None, nologo=True, private=True, enhance=False, negative_prompt=None, seed=None, guidance_scale=None, quality='medium', transparent=False):
    """Generate image using Pollinations direct API"""
    api_key = get_api_key()
    
    encoded_prompt = urllib.parse.quote(prompt)
    url = f'https://gen.pollinations.ai/image/{encoded_prompt}?model={model}&width={width}&height={height}&nologo={str(nologo).lower()}&private={str(private).lower()}&key={api_key}'
    
    if enhance:
        url += '&enhance=true'
    if negative_prompt:
        url += f'&negative_prompt={urllib.parse.quote(negative_prompt)}'
    if seed is not None:
        url += f'&seed={seed}'
    if guidance_scale:
        url += f'&guidance_scale={guidance_scale}'
    if quality != 'medium':
        url += f'&quality={quality}'
    if transparent:
        url += '&transparent=true'
    if reference_url:
        url += f'&image={urllib.parse.quote(reference_url)}'
    
    response = httpx.get(url, timeout=60.0)
    response.raise_for_status()
    
    # Determine output path
    if output_path is None:
        import tempfile
        output_path = tempfile.mktemp(suffix='.jpg')
    
    with open(output_path, 'wb') as f:
        f.write(response.content)
    
    return output_path

def main():
    parser = argparse.ArgumentParser(description='Generate images using Pollinations API')
    parser.add_argument('prompt', help='Image generation prompt')
    parser.add_argument('--model', default='kontext', choices=['kontext', 'flux', 'turbo', 'gptimage', 'seedream', 'seedream-pro', 'nanobanana', 'nanobanana-pro'], help='Model to use')
    parser.add_argument('--width', type=int, default=1024, help='Image width')
    parser.add_argument('--height', type=int, default=1024, help='Image height')
    parser.add_argument('--reference', help='Reference image URL for image-to-image (kontext supports single image)')
    parser.add_argument('--output', help='Output file path (default: temp file)')
    parser.add_argument('--nologo', action='store_true', default=True, help='Remove watermark')
    parser.add_argument('--no-nologo', dest='nologo', action='store_false', help='Keep watermark')
    parser.add_argument('--private', action='store_true', default=True, help='Hide from public feed')
    parser.add_argument('--no-private', dest='private', action='store_false', help='Add to public feed')
    parser.add_argument('--enhance', action='store_true', help='Let AI enhance prompt')
    parser.add_argument('--negative', help='Negative prompt')
    parser.add_argument('--seed', type=int, help='Random seed for reproducibility')
    parser.add_argument('--guidance', type=float, help='Guidance scale (1-20)')
    parser.add_argument('--quality', default='medium', choices=['low', 'medium', 'high', 'hd'], help='Quality level')
    parser.add_argument('--transparent', action='store_true', help='Transparent background')
    
    args = parser.parse_args()
    
    try:
        output = generate_image(
            prompt=args.prompt,
            model=args.model,
            width=args.width,
            height=args.height,
            reference_url=args.reference,
            output_path=args.output,
            nologo=args.nologo,
            private=args.private,
            enhance=args.enhance,
            negative_prompt=args.negative,
            seed=args.seed,
            guidance_scale=args.guidance,
            quality=args.quality,
            transparent=args.transparent
        )
        print(output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()