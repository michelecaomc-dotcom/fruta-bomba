# -*- coding: utf-8 -*-
"""Foglio di contatto degli allegati estratti, con hash per riconoscere i doppioni."""
import glob
import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "sorgenti")

visti = {}
file_unici = []
for p in sorted(glob.glob(os.path.join(SRC, "s*.*"))):
    dati = open(p, "rb").read()
    h = hashlib.md5(dati).hexdigest()[:8]
    if h in visti:
        print(f"DOPPIONE: {os.path.basename(p)} = {visti[h]}")
        continue
    visti[h] = os.path.basename(p)
    im = Image.open(p)
    file_unici.append((p, im.size, h))
    print(f"{os.path.basename(p):16} {im.size[0]}x{im.size[1]}  hash {h}")

print(f"\n{len(file_unici)} immagini uniche")

# foglio di contatto
cols = 4
tw, th, pad, lab = 470, 500, 18, 54
righe = (len(file_unici) + cols - 1) // cols
W = cols * tw + (cols + 1) * pad
H = righe * (th + lab) + (righe + 1) * pad
foglio = Image.new("RGB", (W, H), (27, 14, 31))
d = ImageDraw.Draw(foglio)
try:
    font = ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf", 24)
except OSError:
    font = ImageFont.load_default()

for i, (p, (w, h), hh) in enumerate(file_unici):
    c, r = i % cols, i // cols
    x = pad + c * (tw + pad)
    y = pad + r * (th + lab + pad)
    im = Image.open(p).convert("RGB")
    im.thumbnail((tw, th), Image.LANCZOS)
    foglio.paste(im, (x + (tw - im.width) // 2, y + (th - im.height) // 2))
    d.text((x, y + th + 4), f"{i + 1}. {os.path.basename(p)}", font=font, fill=(247, 239, 224))
    d.text((x, y + th + 30), f"{w}x{h}  {hh}", font=font, fill=(180, 160, 190))

dest = os.path.join(BASE, "anteprima-allegati.jpg")
foglio.save(dest, quality=88)
print("\n", dest, foglio.size)
