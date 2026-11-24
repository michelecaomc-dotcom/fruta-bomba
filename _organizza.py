# -*- coding: utf-8 -*-
"""Rinomina gli allegati estratti con nomi parlanti e archivia gli originali."""
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "sorgenti")
ARCHIVIO = os.path.join(SRC, "_originali_chat")
os.makedirs(ARCHIVIO, exist_ok=True)

MAPPA = {
    "s228_00.webp": "sovereign-vision.webp",
    "s228_01.jpg": "giardino-delle-mele.jpg",
    "s228_03.webp": "medicinal-sovereign.webp",
    "s228_04.jpg": "pioggia-rossa.jpg",
    "s228_05.jpg": "beyond-watchful-skies.jpg",
    "s260_00.webp": "luxe-sovereign-grido.webp",
    "s260_01.jpg": "regina-di-fiori.jpg",
    "s300_00.webp": "psychedelic-sovereign.webp",
    "s300_01.jpg": "toeletta-cosmica.jpg",
    "s300_02.jpg": "citta-che-brucia.jpg",
    "s300_03.jpg": "natura-morta-piramidi.jpg",
    "s300_04.jpg": "paradiso-alla-frutta.jpg",
    "s340_00.webp": "luxe-sovereign-mandala.webp",
}

for vecchio, nuovo in MAPPA.items():
    p = os.path.join(SRC, vecchio)
    if not os.path.exists(p):
        print(f"  manca: {vecchio}")
        continue
    shutil.copy2(p, os.path.join(SRC, nuovo))
    print(f"  {vecchio} -> {nuovo}")

# archivia i file grezzi sNNN_* per non reimportarli
for nome in os.listdir(SRC):
    if nome.startswith("s") and nome[1:4].isdigit():
        shutil.move(os.path.join(SRC, nome), os.path.join(ARCHIVIO, nome))
print("\nOriginali archiviati in sorgenti/_originali_chat")
