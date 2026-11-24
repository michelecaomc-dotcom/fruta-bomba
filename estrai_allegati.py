# -*- coding: utf-8 -*-
"""Estrae le immagini allegate ai messaggi dell'utente e le salva in sorgenti/."""
import base64
import json
import os
import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8")

DB = r"C:\Users\miche\.local\share\opencode\opencode.db"
BASE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(BASE, "sorgenti")
os.makedirs(DEST, exist_ok=True)

c = sqlite3.connect("file:" + DB.replace("\\", "/") + "?mode=ro", uri=True)

# sessione corrente = quella del messaggio utente più recente
sid = c.execute(
    "select session_id from session_message where type='user' "
    "order by time_created desc limit 1").fetchone()[0]
print("sessione:", sid)

righe = c.execute(
    "select id, seq, time_created, data from session_message "
    "where session_id=? and type='user' order by seq", (sid,)).fetchall()

for mid, seq, t, data in righe:
    d = json.loads(data)
    files = d.get("files") or []
    if not files:
        continue
    print(f"\nmessaggio seq={seq}: {len(files)} allegati")
    for i, f in enumerate(files):
        chiavi = {k: (type(v).__name__, len(v) if hasattr(v, "__len__") else v)
                  for k, v in f.items()}
        print("   campi:", chiavi)
        b64 = f.get("data") or ""
        if not b64:
            continue
        try:
            grezzo = base64.b64decode(b64)
        except Exception as e:
            print("   decodifica fallita:", e)
            continue
        # riconosce il formato dai magic bytes
        if grezzo.startswith(b"\xff\xd8\xff"):
            ext = ".jpg"
        elif grezzo.startswith(b"\x89PNG"):
            ext = ".png"
        elif grezzo[:4] == b"RIFF" and grezzo[8:12] == b"WEBP":
            ext = ".webp"
        elif grezzo[:2] == b"BM":
            ext = ".bmp"
        else:
            ext = ".bin"
        nome_orig = f.get("filename") or f.get("name") or ""
        nome = f"s{seq:03d}_{i:02d}{ext}"
        percorso = os.path.join(DEST, nome)
        with open(percorso, "wb") as out:
            out.write(grezzo)
        print(f"   -> {nome} ({len(grezzo)/1024:.0f} KB) da {nome_orig}")
