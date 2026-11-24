# -*- coding: utf-8 -*-
"""
IMPORTA LE NUOVE IMMAGINI
=========================
Metti le tue opere (JPG, PNG, WebP, TIFF) in:  sito_frutabomba/sorgenti/
poi lancia:  python importa_immagini.py

Cosa fa:
  - trova le immagini non ancora presenti in opere.json
  - crea per ognuna una scheda provvisoria (titolo = nome file ripulito,
    download = false) così il sito si costruisce subito
  - non tocca le schede già esistenti: titoli e testi si possono riscrivere

Dopo l'import basta rilanciare  python costruisci_sito.py
"""

import json
import os
import re

from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
SORGENTI = os.path.join(BASE, "sorgenti")
ESTENSIONI = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp"}
JSON = os.path.join(BASE, "opere.json")


def titolo_da_file(nome):
    testo = os.path.splitext(nome)[0]
    testo = re.sub(r"^[0-9]+[\s_.-]*", "", testo)
    testo = testo.replace("_", " ").replace("-", " ").strip()
    return testo.capitalize() if testo else "Senza titolo"


def main():
    os.makedirs(SORGENTI, exist_ok=True)
    with open(JSON, encoding="utf-8") as f:
        opere = json.load(f)

    gia = {o["file"] for o in opere}
    nuovi = []
    for nome in sorted(os.listdir(SORGENTI)):
        if os.path.splitext(nome)[1].lower() not in ESTENSIONI:
            continue
        if nome in gia:
            continue
        percorso = os.path.join(SORGENTI, nome)
        try:
            im = Image.open(percorso)
            im.verify()
            im = Image.open(percorso)
            w, h = im.size
        except Exception as e:
            print(f"  salto {nome}: non è un'immagine valida ({e})")
            continue
        nuovi.append({
            "id": "",
            "file": nome,
            "titolo": titolo_da_file(nome),
            "sottotitolo": "Scheda da completare",
            "anno": "2026",
            "tecnica": "",
            "testo": "",
            "alt": titolo_da_file(nome),
            "download": False,
            "campagna": "",
            "_nota": f"file originale {w}x{h}px",
        })
        print(f"  nuova: {nome} ({w}x{h})")

    if not nuovi:
        print("Nessuna immagine nuova in", SORGENTI)
        return

    # assegna gli id liberi in coda
    usati = {int(o["id"]) for o in opere if o["id"].isdigit()}
    prossimo = 1
    for nuovo in nuovi:
        while prossimo in usati:
            prossimo += 1
        nuovo["id"] = f"{prossimo:02d}"
        usati.add(prossimo)

    opere.extend(nuovi)
    with open(JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(opere, f, ensure_ascii=False, indent=2)
    print(f"\nAggiunte {len(nuovi)} schede provvisorie a opere.json")
    print("Ora: python costruisci_sito.py")


if __name__ == "__main__":
    main()
