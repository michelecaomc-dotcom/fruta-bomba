# -*- coding: utf-8 -*-
"""Foglio di contatto delle opere (per anteprima veloce)."""
import json
import os

from PIL import Image, ImageDraw, ImageFont

base = os.path.dirname(os.path.abspath(__file__))
opere = json.load(open(os.path.join(base, "opere.json"), encoding="utf-8"))

cols = 4
righe = (len(opere) + cols - 1) // cols
tw, th, pad, lab = 460, 460, 16, 48
W = cols * tw + (cols + 1) * pad
H = righe * (th + lab) + (righe + 1) * pad
foglio = Image.new("RGB", (W, H), (27, 14, 31))
d = ImageDraw.Draw(foglio)
try:
    font = ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf", 25)
except OSError:
    font = ImageFont.load_default()

for i, op in enumerate(opere):
    c, r = i % cols, i // righe
    x = pad + c * (tw + pad)
    y = pad + r * (th + lab + pad)
    im = Image.open(os.path.join(base, "img", op["id"] + "-thumb.jpg"))
    im.thumbnail((tw, th), Image.LANCZOS)
    cx = x + (tw - im.width) // 2
    cy = y + (th - im.height) // 2
    foglio.paste(im, (cx, cy))
    d.text((x, y + th + 6), f'{op["id"]}  {op["titolo"]}', font=font, fill=(247, 239, 224))

dest = os.path.join(base, "anteprima-opere.jpg")
foglio.save(dest, quality=90)
print(dest, foglio.size)
