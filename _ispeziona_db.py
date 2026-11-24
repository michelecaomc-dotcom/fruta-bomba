import json
import sqlite3

p = r"C:\Users\miche\.local\share\opencode\opencode.db"
c = sqlite3.connect("file:" + p.replace("\\", "/") + "?mode=ro", uri=True)
c.row_factory = sqlite3.Row

righe = c.execute(
    "select id, session_id, type, seq, time_created, data from session_message "
    "order by time_created desc limit 12"
).fetchall()
for r in righe:
    data = r["data"]
    print("=" * 70)
    print(r["type"], r["seq"], r["time_created"])
    try:
        d = json.loads(data)
    except Exception:
        print(data[:400])
        continue
    testo = json.dumps(d, ensure_ascii=False)
    # mostra solo le chiavi e gli eventuali percorsi immagine
    print("chiavi:", list(d.keys())[:12])
    for chiave in ("parts", "content", "attachments", "files"):
        if chiave in d:
            print(f"  {chiave}:", json.dumps(d[chiave], ensure_ascii=False)[:800])
    if ".png" in testo or ".jpg" in testo or "attachment" in testo.lower():
        for tok in set(testo.split('"')):
            if tok.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                print("   PATH?:", tok)
