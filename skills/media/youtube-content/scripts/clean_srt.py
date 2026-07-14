#!/usr/bin/env python3
"""Clean YouTube auto-caption SRT from overlapping segments + dedup.

YouTube auto-captions produce 3 overlapping blocks per segment.
Step 1: Extract text from each SRT block, strip timestamps.
Step 2: Remove consecutive duplicate lines (3x overlap).
Step 3: Merge into clean continuous text.

Usage: python3 clean_srt.py <input.srt> [output.txt]
"""
import re
import sys

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <input.srt> [output.txt]")
    sys.exit(1)

with open(sys.argv[1], encoding='utf-8') as f:
    text = f.read()

# Step 1: Extract text from SRT blocks
blocks = re.split(r'\n\n+', text.strip())
clean_lines = []

for block in blocks:
    if not block.strip():
        continue
    lines = block.strip().split('\n')
    text_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line[0].isdigit() or '-->' in line:
            continue
        text_lines.append(line)
    if text_lines:
        clean_lines.extend(text_lines)

# Step 2: Remove consecutive duplicates (3x overlap fix)
deduped = []
for line in clean_lines:
    if not deduped or line != deduped[-1]:
        deduped.append(line)

# Step 3: Merge into clean text
output = ' '.join(deduped)

if len(sys.argv) > 2:
    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        f.write(output)
    print(f"Written {len(output)} chars to {sys.argv[2]}")
else:
    print(output[:500] + f"... ({len(output)} chars total)")
