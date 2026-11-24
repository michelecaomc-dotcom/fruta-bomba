# -*- coding: utf-8 -*-
"""
COSTRUISCI IL SITO — Fruta Bomba (arte psichedelica classica)
=============================================================
Legge opere.json, ottimizza le immagini (JPG + WebP, miniature e full),
prepara i file da scaricare (JPG + PDF A4) e scrive:

  index.html            sito completo, autonomo, pronto da pubblicare
  blogger.html          stesso contenuto, da incollare in una pagina Blogger
  robots.txt            per un hosting statico (Blogger ha il suo)
  sitemap.xml           idem
  img/  download/       immagini e file da scaricare

Per cambiare le opere basta modificare opere.json e rilanciare:
  python costruisci_sito.py

Per usare immagini nuove: metti i file in arte_psichedelica/opere/
(oppure in sito_frutabomba/sorgenti/) e aggiorna "file" in opere.json.
"""

import html
import json
import os
import re
import shutil

from PIL import Image, ImageFilter, ImageOps

BASE = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(BASE)
SORGENTI = [
    os.path.join(RADICE, "arte_psichedelica", "opere"),
    os.path.join(BASE, "sorgenti"),
]
IMG = os.path.join(BASE, "img")
DOWNLOAD = os.path.join(BASE, "download")
for d in (IMG, DOWNLOAD):
    os.makedirs(d, exist_ok=True)

# --------------------------------------------------------------- parametri sito
SITO = {
    "nome": "Fruta Bomba",
    "titolo": "Fruta Bomba — campagne immaginarie e arte psichedelica",
    "descrizione": (
        "Galleria di campagne pubblicitarie immaginarie: classicismo, frutta e "
        "colori psichedelici anni Settanta in manifesti e nature morte digitali. "
        "Quattro opere in download gratuito."
    ),
    "url": "https://frutabombafrutabomba.blogspot.com/",
    # indirizzo definitivo del sito (canonical + og:url)
    "url_canonico": "https://michelecaomc-dotcom.github.io/SHOCKNOMICS/fruta-bomba/",
    "autore": "Sanmicheli",
    "email": "mila.michele@yahoo.com",
    "logo_url": "https://michelecaomc-dotcom.github.io/SHOCKNOMICS/",
    "collezione_url": "https://frutabombafrutabomba.blogspot.com/",
    "licenza": "CC BY-NC-ND 4.0",
    "licenza_url": "https://creativecommons.org/licenses/by-nc-nd/4.0/deed.it",
    "img_base": "img",                # in blogger.html puoi mettere un URL assoluto
    # base pubblica dove stanno img/ e download/ (letta da blogger.html)
    "asset_base_blogger": "https://michelecaomc-dotcom.github.io/SHOCKNOMICS/fruta-bomba",
}

LARGHEZZA_FULL = 1800
LARGHEZZA_THUMB = 900
QUALITA_FULL = 88
QUALITA_THUMB = 82

LOGO_FONTE = os.path.join(BASE, "logo-fonte.png")


def prepara_logo():
    """Genera il logo in varie misure dentro img/ (logo, apple touch, favicon)."""
    if not os.path.exists(LOGO_FONTE):
        print("   logo-fonte.png assente: salto il logo")
        return
    im = Image.open(LOGO_FONTE).convert("RGB")
    im = im.resize((320, 320), Image.LANCZOS)
    im.save(os.path.join(IMG, "logo.png"), optimize=True)
    im.resize((192, 192), Image.LANCZOS).save(
        os.path.join(IMG, "logo-192.png"), optimize=True)
    im.resize((48, 48), Image.LANCZOS).save(
        os.path.join(IMG, "favicon.png"), optimize=True)
    print("   logo: img/logo.png (320), logo-192, favicon")


def slug(testo):
    testo = testo.lower()
    testo = re.sub(r"[àáâ]", "a", testo)
    testo = re.sub(r"[èéê]", "e", testo)
    testo = re.sub(r"[ìíî]", "i", testo)
    testo = re.sub(r"[òóô]", "o", testo)
    testo = re.sub(r"[ùúû]", "u", testo)
    testo = re.sub(r"[^a-z0-9]+", "-", testo).strip("-")
    return testo or "opera"


def trova_sorgente(nome_file):
    for cartella in SORGENTI:
        p = os.path.join(cartella, nome_file)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(
        f"Immagine non trovata: {nome_file} — cercata in {SORGENTI}")


def prepara_immagini(opera):
    """Genera miniature, versioni full e WebP. Ritorna (w, h) della thumb."""
    src = Image.open(trova_sorgente(opera["file"]))
    src = ImageOps.exif_transpose(src).convert("RGB")

    def salva(img, nome_base, lato, qualita):
        copia = img.copy()
        copia.thumbnail((lato, lato), Image.LANCZOS)
        jpg = os.path.join(IMG, nome_base + ".jpg")
        webp = os.path.join(IMG, nome_base + ".webp")
        copia.save(jpg, "JPEG", quality=qualita, optimize=True, progressive=True)
        copia.save(webp, "WEBP", quality=qualita, method=6)
        return copia.size

    w, h = salva(src, f"{opera['id']}-thumb", LARGHEZZA_THUMB, QUALITA_THUMB)
    salva(src, f"{opera['id']}-full", LARGHEZZA_FULL, QUALITA_FULL)
    opera["_w"], opera["_h"] = w, h
    opera["_sorgente"] = src
    return opera


def prepara_download(opera):
    src = opera["_sorgente"]
    nome = slug(opera["titolo"])
    jpg = os.path.join(DOWNLOAD, f"frutabomba-{nome}.jpg")
    src.save(jpg, "JPEG", quality=95, optimize=True, progressive=True)
    pdf = os.path.join(DOWNLOAD, f"frutabomba-{nome}-a4.pdf")
    # PDF A4 verticale con margine bianco e didascalia stampata
    A4 = (2480, 3508)  # 210x297 mm a 300 dpi
    foglio = Image.new("RGB", A4, (247, 239, 225))
    margine = 170
    area_w = A4[0] - 2 * margine
    area_h = A4[1] - 2 * margine - 320
    copia = src.copy()
    # i file di partenza sono piccoli: per la stampa A4 li porto almeno a 1600 px
    if max(copia.size) < 1600:
        fattore = 1600 / max(copia.size)
        copia = copia.resize(
            (round(copia.width * fattore), round(copia.height * fattore)),
            Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.6, 90, 3))
    copia.thumbnail((area_w, area_h), Image.LANCZOS)
    foglio.paste(copia, ((A4[0] - copia.width) // 2, margine + (area_h - copia.height) // 2))
    foglio.save(pdf, "PDF", resolution=300.0)
    opera["_download_jpg"] = os.path.relpath(jpg, BASE).replace("\\", "/")
    opera["_download_pdf"] = os.path.relpath(pdf, BASE).replace("\\", "/")
    opera["_peso_mb"] = round(os.path.getsize(jpg) / 1024 / 1024, 1)
    return opera


# ------------------------------------------------------------------- CSS
CSS = r"""
:root{
  --ink:#1b0e1f;
  --paper:#f7efe0;
  --paper2:#fdf8ee;
  --arancia:#e4572e;
  --giallo:#f2b705;
  --magenta:#d81e5b;
  --teal:#0f7b6c;
  --viola:#4b1e6b;
  --ombra:6px 6px 0 var(--ink);
  --radius:18px;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0;background:var(--paper);color:var(--ink);
  font-family:"Archivo","Helvetica Neue",Arial,sans-serif;
  font-size:17px;line-height:1.62;
  -webkit-font-smoothing:antialiased;
  overflow-x:hidden;
}
body::after{
  content:"";position:fixed;inset:0;pointer-events:none;z-index:9999;
  opacity:.055;mix-blend-mode:multiply;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3'/%3E%3C/filter%3E%3Crect width='160' height='160' filter='url(%23n)'/%3E%3C/svg%3E");
}
h1,h2,h3,h4{font-family:"Fraunces",Georgia,serif;font-weight:700;line-height:1.02;margin:0;letter-spacing:-.02em}
a{color:var(--ink)}
img{max-width:100%;display:block}
.wrap{width:min(1180px,92vw);margin-inline:auto}
.eyebrow{
  font-size:.72rem;letter-spacing:.22em;text-transform:uppercase;
  font-weight:700;margin:0 0 .9rem;display:inline-flex;align-items:center;gap:.55rem;
}
.eyebrow::before{content:"";width:26px;height:3px;background:var(--arancia);display:inline-block}

/* ---------- header ---------- */
header.top{
  position:sticky;top:0;z-index:100;
  background:rgba(247,239,224,.86);backdrop-filter:blur(10px);
  border-bottom:2px solid var(--ink);
}
.top-in{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:.65rem 0}
.logo{display:flex;align-items:center;gap:.6rem;text-decoration:none;font-family:"Fraunces",serif;
  font-weight:700;font-size:1.22rem;letter-spacing:-.02em}
.brand{display:flex;align-items:center;gap:.6rem}
.logo-mark{display:block;line-height:0;border-radius:50%;transition:transform .18s ease}
.logo-mark img{width:44px;height:44px;border-radius:50%;display:block;
  box-shadow:0 0 0 2px var(--ink)}
.logo-mark:hover{transform:rotate(-7deg) scale(1.06)}
.foot-brand{font-family:"Fraunces",serif;font-weight:700;font-size:1.3rem;margin-top:.55rem}
.foot .logo-mark img{box-shadow:0 0 0 2px var(--paper)}
.logo svg{flex:0 0 auto}
nav.menu{display:flex;gap:.35rem;flex-wrap:wrap}
nav.menu a{
  text-decoration:none;font-size:.78rem;font-weight:700;text-transform:uppercase;
  letter-spacing:.1em;padding:.45rem .8rem;border-radius:999px;border:2px solid transparent;
  transition:.18s;
}
nav.menu a:hover{border-color:var(--ink);background:var(--giallo)}

/* ---------- hero ---------- */
.hero{position:relative;overflow:hidden;border-bottom:2px solid var(--ink);
  background:var(--paper2)}
.hero::before{
  content:"";position:absolute;inset:0;z-index:1;pointer-events:none;
  background:linear-gradient(96deg,var(--paper2) 0%,var(--paper2) 34%,
    rgba(253,248,238,.72) 52%,rgba(253,248,238,0) 74%);
}
.hero-sun{
  position:absolute;width:min(170vw,1700px);aspect-ratio:1;right:-58vw;top:-66vw;
  border-radius:50%;z-index:0;
  background:repeating-conic-gradient(from 0deg,
    var(--arancia) 0deg 5deg, var(--giallo) 5deg 10deg,
    var(--magenta) 10deg 15deg, var(--viola) 15deg 20deg);
  animation:gira 90s linear infinite;
}
@keyframes gira{to{transform:rotate(360deg)}}
.hero-in{position:relative;z-index:2;padding:clamp(3rem,7vw,6rem) 0 clamp(2.4rem,5vw,4rem)}
.hero h1{
  font-size:clamp(3.1rem,11vw,8.6rem);line-height:.86;letter-spacing:-.045em;
  text-transform:uppercase;
}
.hero h1 em{font-style:italic;color:var(--arancia);text-transform:none}
.hero-p{max-width:39ch;margin:1.6rem 0 0;font-size:1.05rem}
.cta-row{display:flex;flex-wrap:wrap;gap:.9rem;margin-top:2rem}
.btn{
  display:inline-flex;align-items:center;gap:.6rem;text-decoration:none;
  font-weight:800;font-size:.82rem;letter-spacing:.12em;text-transform:uppercase;
  padding:.95rem 1.5rem;border:2px solid var(--ink);border-radius:999px;
  background:var(--paper2);box-shadow:var(--ombra);transition:.16s;
}
.btn:hover{transform:translate(-2px,-2px);box-shadow:8px 8px 0 var(--ink)}
.btn:active{transform:translate(3px,3px);box-shadow:2px 2px 0 var(--ink)}
.btn.solid{background:var(--ink);color:var(--paper2)}
.btn.solid:hover{background:var(--arancia);color:var(--ink)}

/* ---------- marquee ---------- */
.marquee{background:var(--ink);color:var(--paper);overflow:hidden;border-bottom:2px solid var(--ink)}
.marquee div{display:flex;gap:2.2rem;white-space:nowrap;padding:.7rem 0;
  animation:scorri 28s linear infinite;will-change:transform}
.marquee span{font-size:.78rem;letter-spacing:.26em;text-transform:uppercase;font-weight:700}
.marquee b{color:var(--giallo)}
@keyframes scorri{to{transform:translateX(-50%)}}

/* ---------- sezioni ---------- */
section{padding:clamp(3.2rem,7vw,6rem) 0;position:relative}
.sez-head{display:flex;align-items:flex-end;justify-content:space-between;gap:2rem;flex-wrap:wrap;margin-bottom:2.6rem}
.sez-head h2{font-size:clamp(2.1rem,5vw,3.6rem);text-transform:uppercase;letter-spacing:-.03em}
.sez-head p{max-width:46ch;margin:0}

/* ---------- galleria ---------- */
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:1.6rem}
.serie + .serie{margin-top:clamp(2.6rem,5vw,4rem)}
.serie-head{
  display:grid;grid-template-columns:auto 1fr;gap:.2rem 1.4rem;align-items:baseline;
  border-top:2px solid var(--ink);padding-top:1.1rem;margin-bottom:1.6rem;
}
.serie-head .eyebrow{grid-column:1/-1;margin-bottom:.4rem}
.serie-head h3{font-size:clamp(1.7rem,3.4vw,2.5rem);text-transform:uppercase;letter-spacing:-.02em}
.serie-head p:last-child{max-width:52ch;font-size:.92rem;margin:0;color:#3a2b3d}
@media (max-width:700px){.serie-head{grid-template-columns:1fr}}
.card{
  background:var(--paper2);border:2px solid var(--ink);border-radius:var(--radius);
  overflow:hidden;box-shadow:var(--ombra);display:flex;flex-direction:column;
  transition:.2s;
}
.card:hover{transform:translate(-3px,-3px) rotate(-.35deg);box-shadow:9px 9px 0 var(--ink)}
.card-media{display:block;position:relative;overflow:hidden;background:var(--ink);border-bottom:2px solid var(--ink)}
.card-media img{width:100%;height:auto;transition:transform .5s ease}
.card:hover .card-media img{transform:scale(1.035)}
.card-body{padding:1.15rem 1.2rem 1.35rem;display:flex;flex-direction:column;gap:.4rem;flex:1}
.card-num{
  font-family:"Fraunces",serif;font-size:.78rem;font-weight:700;letter-spacing:.18em;
  color:var(--arancia);
}
.card h3{font-size:1.42rem;line-height:1.05}
.card .sub{font-size:.82rem;font-style:italic;color:var(--viola);margin:0;line-height:1.35}
.card .txt{font-size:.9rem;margin:.35rem 0 0;line-height:1.55;color:#3a2b3d}
.card .meta{list-style:none;padding:0;margin:.7rem 0 0;display:flex;flex-wrap:wrap;gap:.35rem}
.card .meta li{
  font-size:.63rem;letter-spacing:.09em;text-transform:uppercase;font-weight:700;
  border:1.5px solid var(--ink);border-radius:999px;padding:.2rem .55rem;
}
.badge{
  align-self:flex-start;margin-top:.9rem;font-size:.66rem;font-weight:800;
  letter-spacing:.14em;text-transform:uppercase;background:var(--giallo);
  border:2px solid var(--ink);border-radius:999px;padding:.28rem .7rem;
  transform:rotate(-2deg);
}

/* ---------- download ---------- */
.download{background:var(--viola);color:var(--paper);border-top:2px solid var(--ink);border-bottom:2px solid var(--ink)}
.download .eyebrow{color:var(--giallo)}
.download .eyebrow::before{background:var(--giallo)}
.download h2{color:var(--paper)}
.download .sez-head p{color:#e8dcee}
.dl-griglia{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1.6rem}
.dl{
  background:var(--paper2);color:var(--ink);border:2px solid var(--ink);border-radius:var(--radius);
  overflow:hidden;display:flex;flex-direction:column;box-shadow:6px 6px 0 var(--giallo);
}
.dl img{width:100%;height:230px;object-fit:cover;border-bottom:2px solid var(--ink)}
.dl-body{padding:1.1rem 1.15rem 1.3rem;display:flex;flex-direction:column;gap:.35rem;flex:1}
.dl h3{font-size:1.3rem}
.dl .sub{font-size:.79rem;font-style:italic;color:var(--magenta);margin:0}
.dl .txt{font-size:.86rem;margin:.3rem 0 0;line-height:1.5;color:#3a2b3d}
.dl-links{display:flex;gap:.5rem;flex-wrap:wrap;margin-top:auto;padding-top:1rem}
.dl-links a{
  text-decoration:none;font-size:.68rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;
  border:2px solid var(--ink);border-radius:999px;padding:.5rem .85rem;background:var(--giallo);
  transition:.15s;
}
.dl-links a.ghost{background:transparent}
.dl-links a:hover{background:var(--ink);color:var(--paper2)}
.nota-licenza{font-size:.78rem;margin-top:1.8rem;color:#e2d5ea;max-width:70ch}

/* ---------- studio ---------- */
.studio-grid{display:grid;grid-template-columns:1.15fr .85fr;gap:clamp(1.6rem,4vw,3.4rem);align-items:start}
.studio-grid p{max-width:58ch}
.studio-box{
  border:2px solid var(--ink);border-radius:var(--radius);background:var(--paper2);
  padding:1.6rem;box-shadow:var(--ombra);
}
.studio-box h3{font-size:1.2rem;margin-bottom:.5rem}
.studio-box ul{margin:0;padding-left:1.1rem;font-size:.9rem}
.studio-box li{margin-bottom:.35rem}
.firma{font-family:"Fraunces",serif;font-style:italic;font-size:1.5rem;margin-top:1.4rem}

/* ---------- footer ---------- */
footer{background:var(--ink);color:var(--paper);padding:2.6rem 0 2rem;border-top:2px solid var(--ink)}
.foot{display:flex;justify-content:space-between;gap:1.6rem;flex-wrap:wrap;align-items:flex-start}
.foot a{color:var(--giallo)}
.foot small{display:block;opacity:.7;font-size:.75rem;line-height:1.7;max-width:52ch}

/* ---------- responsive ---------- */
@media (max-width:820px){
  .studio-grid{grid-template-columns:1fr}
  nav.menu{display:none}
  .dl img{height:200px}
}
@media (prefers-reduced-motion:reduce){
  *{animation:none!important;transition:none!important;scroll-behavior:auto!important}
}
"""


def card_html(op, img_base):
    e = html.escape
    badge = ('<span class="badge">Scaricabile gratis</span>'
             if op["download"] else "")
    return f'''
      <article class="card" id="op{op["id"]}">
        <a class="card-media" href="{img_base}/{op["id"]}-full.jpg" target="_blank" rel="noopener">
          <picture>
            <source type="image/webp" srcset="{img_base}/{op["id"]}-full.webp">
            <img src="{img_base}/{op["id"]}-full.jpg" alt="{e(op["alt"])}"
                 width="{op["_w"]}" height="{op["_h"]}" loading="lazy" decoding="async">
          </picture>
        </a>
        <div class="card-body">
          <span class="card-num">{e(op.get("serie", ""))} · {op["id"]}</span>
          <h3>{e(op["titolo"])}</h3>
          <p class="sub">{e(op["sottotitolo"])}</p>
          <p class="txt">{e(op["testo"])}</p>
          <ul class="meta"><li>{e(op["anno"])}</li><li>{e(op["tecnica"].split(" — ")[0])}</li></ul>
          {badge}
        </div>
      </article>'''


def download_html(op, img_base):
    e = html.escape
    # img_base è "img" (percorso relativo) oppure "https://sito/img"
    if img_base.endswith("/img"):
        dl = img_base[:-4] + "/download/"
    else:
        dl = "download/"
    jpg = op["_download_jpg"].split("/")[-1]
    pdf = op["_download_pdf"].split("/")[-1]
    return f'''
      <article class="dl" id="dl{op["id"]}">
        <img src="{img_base}/{op["id"]}-thumb.jpg" alt="{e(op["alt"])}" loading="lazy" decoding="async">
        <div class="dl-body">
          <span class="card-num">{e(op["campagna"])}</span>
          <h3>{e(op["titolo"])}</h3>
          <p class="sub">{e(op["sottotitolo"])}</p>
          <p class="txt">{e(op["testo"])}</p>
          <div class="dl-links">
            <a href="{dl}{jpg}" download>Scarica JPG · {op["_peso_mb"]} MB</a>
            <a class="ghost" href="{dl}{pdf}" download>PDF A4</a>
          </div>
        </div>
      </article>'''


def json_ld(opere):
    base = (SITO["url_canonico"] or SITO["url"]).rstrip("/") + "/"
    opere_json = []
    for op in opere:
        if not op["download"]:
            continue
        opere_json.append({
            "@type": "VisualArtwork",
            "name": op["titolo"],
            "alternativeName": op["sottotitolo"],
            "description": op["testo"],
            "artMedium": "Stampa digitale fine art",
            "artform": "Digital artwork",
            "dateCreated": op["anno"],
            "creator": {"@type": "Person", "name": SITO["autore"]},
            "image": base + f"img/{op['id']}-full.jpg",
            "thumbnailUrl": base + f"img/{op['id']}-thumb.jpg",
            "license": SITO["licenza_url"],
        })
    dati = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": SITO["titolo"],
        "description": SITO["descrizione"],
        "url": base,
        "inLanguage": "it-IT",
        "author": {"@type": "Person", "name": SITO["autore"]},
        "hasPart": opere_json,
    }
    return json.dumps(dati, ensure_ascii=False, indent=2)


def pagina(opere, img_base, per_blogger=False):
    e = html.escape
    scaricabili = [o for o in opere if o["download"]]
    n_download = len(scaricabili)
    totale = len(opere)
    n_serie = len({o.get("serie", "") for o in opere})
    logo = f"{img_base}/logo.png"

    descrizioni_serie = {
        "Sovereign": (
            "Sei manifesti per un conglomerato che non esiste: farmaci, armi, "
            "cosmetici e satelliti venduti con lo stesso sorriso. Il classicismo "
            "fa da quinta, la psichedelia da imballaggio."),
        "Giardino": (
            "Sette tavole senza slogan: frutta, vasi, specchi e cieli che si "
            "arrotolano. Qui la pubblicità si ritira e resta il quadro, con la "
            "luce di un pomeriggio che non finisce."),
        "Barocco": (
            "Il barocco incontra la pubblicità: stampe secentesche, frutta "
            "iperreale e architetture brutaliste. La decorazione diventa "
            "messaggio — e in una di queste due, il messaggio è serio."),
    }
    serie_viste = []
    for op in opere:
        s = op.get("serie", "")
        if s not in serie_viste:
            serie_viste.append(s)
    blocchi = []
    for s in serie_viste:
        gruppo = [o for o in opere if o.get("serie", "") == s]
        carte = "".join(card_html(o, img_base) for o in gruppo)
        descr = descrizioni_serie.get(s, "")
        blocchi.append(f'''
      <div class="serie">
        <div class="serie-head">
          <p class="eyebrow">Serie · {len(gruppo)} opere</p>
          <h3>{e(s)}</h3>
          <p>{e(descr)}</p>
        </div>
        <div class="griglia">{carte}
        </div>
      </div>''')
    galleria = "".join(blocchi)
    downloads = "".join(download_html(o, img_base) for o in scaricabili)
    anno = "2026"
    jsonld = json_ld(opere)
    canonico = (SITO["url_canonico"] or SITO["url"]).rstrip("/") + "/"
    # og:image deve essere un indirizzo assoluto
    og_base = img_base if img_base.startswith("http") else canonico + img_base.lstrip("/")
    primo = (scaricabili[0]["id"] if scaricabili else opere[0]["id"])
    og_img = f'{og_base}/{primo}-full.jpg'

    corpo = f'''
<header class="top">
  <div class="wrap top-in">
    <div class="brand">
      <a class="logo-mark" href="{SITO["logo_url"]}" target="_blank" rel="noopener"
         title="SHOCKNOMICS — il sito dell'autore">
        <img src="{logo}" alt="Logo SHOCKNOMICS" width="44" height="44">
      </a>
      <a class="logo" href="#top">Fruta Bomba</a>
    </div>
    <nav class="menu" aria-label="Menu principale">
      <a href="#opere">Opere</a>
      <a href="#download">Download gratis</a>
      <a href="#studio">Studio</a>
      <a href="#contatti">Contatti</a>
    </nav>
  </div>
</header>

<main id="top">
  <section class="hero">
    <div class="hero-sun" aria-hidden="true"></div>
    <div class="wrap hero-in">
      <p class="eyebrow">Campagne immaginarie · dal 2013</p>
      <h1>Fruta<br><em>Bomba</em></h1>
      <p class="hero-p">Manifesti e nature morte per un impero pubblicitario che non
      esiste. Classici, frutta, marmi e orbite: la grafica psichedelica degli anni
      Settanta applicata al lusso, con la serietà di un museo e la faccia tosta di
      un annuncio a doppia pagina.</p>
      <div class="cta-row">
        <a class="btn solid" href="#opere">Guarda le opere</a>
        <a class="btn" href="#download">Scarica {n_download} opere gratis</a>
      </div>
    </div>
  </section>

  <div class="marquee" aria-hidden="true"><div>
    <span>Campagne immaginarie</span><span><b>·</b></span><span>Classicismo</span><span><b>·</b></span>
    <span>Psichedelia anni '70</span><span><b>·</b></span><span>Download gratuito</span><span><b>·</b></span>
    <span>Nature morte</span><span><b>·</b></span><span>Campagne immaginarie</span><span><b>·</b></span>
    <span>Classicismo</span><span><b>·</b></span><span>Psichedelia anni '70</span><span><b>·</b></span>
    <span>Download gratuito</span><span><b>·</b></span><span>Nature morte</span><span><b>·</b></span>
  </div></div>

  <section id="opere">
    <div class="wrap">
      <div class="sez-head">
        <div>
          <p class="eyebrow">La collezione</p>
          <h2>Opere</h2>
        </div>
        <p>{n_serie} serie, {totale} pezzi: i manifesti della Sovereign, conglomerato
        immaginario di farmaci, armi e cosmetici; le tavole del Giardino, dove la
        réclame sparisce e resta la frutta sotto un cielo che gira; e il Barocco,
        dove la decorazione diventa messaggio.</p>
      </div>
      <div class="serie-lista">{galleria}
      </div>
    </div>
  </section>

  <section id="download" class="download">
    <div class="wrap">
      <div class="sez-head">
        <div>
          <p class="eyebrow">Regalo</p>
          <h2>Scarica gratis</h2>
        </div>
        <p>{n_download} opere in alta risoluzione, libere per uso personale e didattico.
        JPG pronto per lo schermo, PDF impaginato per la stampa in A4.</p>
      </div>
      <div class="dl-griglia">{downloads}
      </div>
      <p class="nota-licenza">Licenza {SITO["licenza"]}: puoi scaricare, stampare e
      condividere le opere citando l'autore e il sito, senza modificarle e senza uso
      commerciale. Per esposizioni, pubblicazioni o stampe in grande formato scrivi
      allo studio.</p>
    </div>
  </section>

  <section id="studio">
    <div class="wrap">
      <div class="sez-head">
        <div>
          <p class="eyebrow">Lo studio</p>
          <h2>Classico, ma con il filtro sbagliato</h2>
        </div>
      </div>
      <div class="studio-grid">
        <div>
          <p>Fruta Bomba nasce come quaderno di incisioni e stampe; oggi è il
          laboratorio di una campagna pubblicitaria che non è mai stata lanciata.
          Al centro c'è la Sovereign, un conglomerato immaginario che vende cure,
          armamenti, cosmetici e visioni orbitali usando lo stesso alfabeto visivo:
          il manifesto di lusso, la frutta come promessa, il cielo come sfondo
          infinito.</p>
          <p>Il metodo è sempre lo stesso: impaginazione da réclame, tipografia
          gonfiata, colore saturo anni Settanta — Moscoso, Wilson, Peter Max,
          Klarwein — e poi un innesto classico: una colonna, un vaso istoriato, una
          statua che affiora. Il risultato è un classicismo che non chiede permesso,
          dove la bellezza ideale finisce in vetrina e la vetrina si crede un museo.</p>
          <p>{SITO["autore"]} è un appassionato e collezionista di arte: la sua
          <a href="{SITO["collezione_url"]}" target="_blank" rel="noopener">collezione
          di stampe e incisioni</a> si può vedere sul blog.</p>
          <p class="firma">— {SITO["autore"]}</p>
        </div>
        <aside class="studio-box">
          <h3>In breve</h3>
          <ul>
            <li><strong>Autore:</strong> {SITO["autore"]}, appassionato e collezionista d'arte</li>
            <li><strong>Tecnica:</strong> composizione digitale, stampa fine art</li>
            <li><strong>Temi:</strong> classicismo, frutta, lusso, sorveglianza</li>
            <li><strong>Formati:</strong> JPG alta risoluzione e PDF A4</li>
            <li><strong>Licenza download:</strong> {SITO["licenza"]}</li>
            <li><strong>Anno:</strong> {anno}</li>
          </ul>
        </aside>
      </div>
    </div>
  </section>
</main>

<footer id="contatti">
  <div class="wrap foot">
    <div>
      <a class="logo-mark" href="{SITO["logo_url"]}" target="_blank" rel="noopener"
         title="SHOCKNOMICS — il sito dell'autore">
        <img src="{logo}" alt="Logo SHOCKNOMICS" width="48" height="48">
      </a>
      <div class="foot-brand">Fruta Bomba</div>
      <small style="margin-top:.6rem">Campagne immaginarie, manifesti e nature
      morte digitali. Nessun prodotto reale è stato venduto.</small>
    </div>
    <div>
      <small>Scrivimi: <a href="mailto:{SITO["email"]}">{SITO["email"]}</a><br>
      Blog: <a href="{SITO["url"]}">frutabombafrutabomba.blogspot.com</a><br>
      Licenza opere: <a href="{SITO["licenza_url"]}">{SITO["licenza"]}</a></small>
      <small style="margin-top:.8rem">© {anno} {SITO["autore"]} — Tutti i diritti
      riservati sulle opere. Sovereign è un marchio di fantasia.</small>
    </div>
  </div>
</footer>

<script type="application/ld+json">
{jsonld}
</script>
'''

    if per_blogger:
        # frammento per una pagina Blogger: niente <html>, <head>, <body>
        font_url = ("https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;800"
                    "&family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,700;"
                    "1,9..144,400&display=swap")
        return f'''<style>
@import url("{font_url}");
{CSS}
</style>
<div class="frutabomba">
{corpo}
</div>
'''

    return f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{SITO["titolo"]}</title>
<meta name="description" content="{SITO["descrizione"]}">
<meta name="author" content="{SITO["autore"]}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{canonico}">
<meta property="og:type" content="website">
<meta property="og:locale" content="it_IT">
<meta property="og:site_name" content="{SITO["nome"]}">
<meta property="og:title" content="{SITO["titolo"]}">
<meta property="og:description" content="{SITO["descrizione"]}">
<meta property="og:url" content="{canonico}">
<meta property="og:image" content="{og_img}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{SITO["titolo"]}">
<meta name="twitter:description" content="{SITO["descrizione"]}">
<meta name="twitter:image" content="{og_img}">
<meta name="theme-color" content="#f7efe0">
<link rel="icon" href="{img_base}/favicon.png" sizes="48x48">
<link rel="apple-touch-icon" href="{img_base}/logo-192.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;800&family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,700;1,9..144,400&display=swap" rel="stylesheet">
<style>
{CSS}
</style>
</head>
<body>
{corpo}
</body>
</html>
'''


def scrivi(nome, contenuto):
    percorso = os.path.join(BASE, nome)
    with open(percorso, "w", encoding="utf-8", newline="\n") as f:
        f.write(contenuto)
    print(f"  scritto: {nome} ({len(contenuto) / 1024:.0f} KB)")


def main():
    with open(os.path.join(BASE, "opere.json"), encoding="utf-8") as f:
        opere = json.load(f)

    # pulisce le cartelle generate, per non lasciare file vecchi
    for cartella in (IMG, DOWNLOAD):
        for nome in os.listdir(cartella):
            os.remove(os.path.join(cartella, nome))

    prepara_logo()

    print("1) Ottimizzo le immagini...")
    for op in opere:
        prepara_immagini(op)
        print(f"   {op['id']} {op['titolo']} — thumb {op['_w']}x{op['_h']}")

    print("2) Preparo i download gratuiti...")
    for op in opere:
        if op["download"]:
            prepara_download(op)
            print(f"   {op['titolo']}: {op['_peso_mb']} MB + PDF A4")

    print("3) Scrivo le pagine...")
    scrivi("index.html", pagina(opere, SITO["img_base"]))
    base_blogger = SITO["asset_base_blogger"].rstrip("/")
    img_blogger = (base_blogger + "/img") if base_blogger else SITO["img_base"]
    scrivi("blogger.html", pagina(opere, img_blogger, per_blogger=True))
    scrivi("robots.txt",
           "User-agent: *\nAllow: /\nSitemap: "
           + SITO["url"].rstrip("/") + "/sitemap.xml\n")
    scrivi("sitemap.xml",
           '<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           f'  <url><loc>{SITO["url"]}</loc><changefreq>monthly</changefreq>'
           '<priority>1.0</priority></url>\n'
           '</urlset>\n')
    print("\nFatto. Apri index.html nel browser per vedere il sito.")


if __name__ == "__main__":
    main()
