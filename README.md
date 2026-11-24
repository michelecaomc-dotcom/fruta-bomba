# Fruta Bomba — sito

Sito della galleria: 15 opere in tre serie (Sovereign, Giardino, Barocco),
4 download gratuiti.

**Indirizzo pubblico:** https://michelecaomc-dotcom.github.io/SHOCKNOMICS/fruta-bomba/

Il sito vive dentro il repository SHOCKNOMICS, in una cartella sua
(`fruta-bomba/`): è una pagina a parte e non tocca la home, i PDF né
gli altri documenti.

Tutto si genera dai file di questa cartella.

```
sito_frutabomba/
├─ index.html            ← il sito completo (anteprima locale)
├─ blogger.html          ← lo stesso sito come pagina Blogger
├─ opere.json            ← catalogo: titoli, testi, alt, download sì/no
├─ logo-fonte.png        ← il logo (320×320)
├─ sorgenti/             ← immagini originali (qui metti le nuove)
├─ img/                  ← immagini ottimizzate JPG + WebP (generate)
├─ download/             ← JPG + PDF A4 dei pezzi gratuiti (generati)
├─ costruisci_sito.py    ← rigenera tutto
├─ pubblica_shocknomics.py ← rigenera, copia in SHOCKNOMICS e pubblica
├─ importa_immagini.py   ← aggiunge le immagini nuove al catalogo
└─ anteprima.py          ← foglio di contatto di tutte le opere
```

## Pubblicare (un comando)

```powershell
python pubblica_shocknomics.py
```

Rigenera il sito, copia `index.html`, `img/` e `download/` nella cartella
`fruta-bomba/` del repository SHOCKNOMICS, fa commit e push. Dopo un minuto
GitHub Pages è aggiornato.

Il repository locale di SHOCKNOMICS sta in `..\Repo SHOCKNOMICS`. Se non
c'è:

```powershell
cd ..
git clone https://github.com/michelecaomc-dotcom/SHOCKNOMICS.git "Repo SHOCKNOMICS"
```

## Rigenerare solo il sito

```powershell
python costruisci_sito.py
```

Indirizzi e contatti sono in cima a `costruisci_sito.py`:

- `SITO["email"]` → `mila.michele@yahoo.com`
- `SITO["url_canonico"]` → indirizzo pubblico del sito (canonical e og:url)
- `SITO["url"]` → il blog, usato nei link "collezione di stampe"

## Aggiungere opere

1. copia le immagini in `sorgenti/`;
2. `python importa_immagini.py` (crea le schede provvisorie in `opere.json`);
3. apri `opere.json` e scrivi titolo, sottotitolo, testo, alt, serie;
4. `python costruisci_sito.py`.

L'`alt` non è decorativo: è quello che leggono Google Immagini e gli screen
reader. Descrivi cosa si vede, in italiano, senza parole chiave ammassate.

## Pubblicare su Blogger

1. Blogger → **Pagine** → **Nuova pagina**.
2. Titolo: `Opere` (o `Galleria`).
3. Passa alla **vista HTML** (icona `< >`) e incolla tutto il contenuto di
   `blogger.html`.
4. Pubblica.

### Le immagini su Blogger

`blogger.html` non contiene immagini: punta agli stessi file del sito, già
online dentro SHOCKNOMICS (`SITO["asset_base_blogger"]`). Quindi la pagina
Blogger resta leggerissima e le immagini si aggiornano da sole quando
ripubblichi il sito con `pubblica_shocknomics.py`.

Se un giorno cambi indirizzo al sito, aggiorna `SITO["asset_base_blogger"]`
e rigenera.

### Impostazioni Blogger da sistemare

- **Impostazioni → Metadati** → attiva la descrizione di ricerca e incolla:
  *Campagne pubblicitarie immaginarie: classicismo, frutta e psichedelia anni
  Settanta. Quattro opere in download gratuito.*
- **Impostazioni → Crawler e indicizzazione** → attiva `robots.txt` personalizzato
  e `robots` header personalizzato con `all, noodp`.
- **Impostazioni → Feed** → "Feed completo" (aiuta la scoperta).
- **Tema** → lascia il tema attuale ma togli la sidebar, così la pagina respira.

## Farsi trovare (SEO: aspettative oneste)

Non esiste un interruttore "rendimi famoso". Quello che possiamo fare è
togliere tutti gli ostacoli tecnici e dare a Google motivi per sceglierti:

1. **Search Console** (search.google.com/search-console) → aggiungi la
   proprietà, verifica, invia `sitemap.xml` (Blogger: `.../sitemap.xml`).
   Senza questo passaggio l'indicizzazione può richiedere mesi.
2. **Titoli e descrizioni** — già scritti nel file. Per ogni post nuovo usa un
   titolo specifico ("Sovereign Vision, manifesto immaginario") e non
   "Nuovo post".
3. **Alt text** — già compilato per tutte le 13 opere.
4. **Condivisione** — incolla il link della pagina principale su Pinterest,
   Reddit (`r/psychedelicart`, `r/artstore`), Facebook. Pinterest porta molto
   traffico alle immagini.
5. **Backlink** — un link da un forum di grafica, da un blog amico o da un
   profilo Behance/Instagram vale più di dieci parole chiave.
6. **Tempo** — 4-8 settimane per le prime posizioni su query lunghe
   ("manifesto psichedelico anni 70 frutta", "arte psichedelica classica").
   Le query competitive ("arte psichedelica") sono fuori portata per un blog
   singolo: punta sul lungo-coda.

## Licenza dei download

Impostata a **CC BY-NC-ND 4.0**: scarico, stampa e condivisione liberi con
attribuzione, senza modifiche e senza uso commerciale. Se vuoi cambiarla,
modifica `SITO["licenza"]` e `SITO["licenza_url"]`.
