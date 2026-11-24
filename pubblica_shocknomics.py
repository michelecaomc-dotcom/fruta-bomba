"""Copia il sito Fruta Bomba dentro il repository SHOCKNOMICS e lo pubblica.

Il sito finisce in una cartella sua, `fruta-bomba/`, quindi resta una pagina
a parte: non tocca index.html, i PDF né il resto del repository.

    python pubblica_shocknomics.py            # copia + commit + push
    python pubblica_shocknomics.py --solo-copia
"""

import datetime
import os
import shutil
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(os.path.dirname(BASE), "Repo SHOCKNOMICS")
DEST = os.path.join(REPO, "fruta-bomba")
CARTELLE = ("img", "download")


def git(*args):
    return subprocess.run(
        ["git", *args], cwd=REPO, text=True, capture_output=True
    )


def copia():
    if not os.path.isdir(REPO):
        sys.exit(f"Repository SHOCKNOMICS non trovato in:\n  {REPO}")

    os.makedirs(DEST, exist_ok=True)
    shutil.copy2(os.path.join(BASE, "index.html"),
                 os.path.join(DEST, "index.html"))

    for cartella in CARTELLE:
        sorgente = os.path.join(BASE, cartella)
        destinazione = os.path.join(DEST, cartella)
        if os.path.isdir(destinazione):
            shutil.rmtree(destinazione)
        shutil.copytree(sorgente, destinazione)

    peso = sum(
        os.path.getsize(os.path.join(r, f))
        for r, _, files in os.walk(DEST) for f in files
    )
    print(f"copiati index.html, img/ e download/ in {DEST}")
    print(f"peso totale: {peso / 1024 / 1024:.1f} MB")


def pubblica():
    git("add", "--", "fruta-bomba")
    stato = git("status", "--porcelain", "--", "fruta-bomba")
    if not stato.stdout.strip():
        print("niente da pubblicare: il sito è già aggiornato.")
        return

    data = datetime.date.today().isoformat()
    commit = git("commit", "-m", f"Fruta Bomba: aggiornamento {data}")
    if commit.returncode != 0:
        sys.exit(commit.stderr or commit.stdout)
    print("commit fatto")

    push = git("push", "origin", "HEAD")
    if push.returncode != 0:
        sys.exit(push.stderr or push.stdout)
    print("pubblicato su GitHub Pages.")


def main():
    solo_copia = "--solo-copia" in sys.argv

    print("1) Rigenero il sito...")
    esito = subprocess.run([sys.executable, "costruisci_sito.py"], cwd=BASE)
    if esito.returncode != 0:
        sys.exit("la generazione del sito è fallita")

    print("2) Copio dentro SHOCKNOMICS...")
    copia()

    if solo_copia:
        print("\nFatto (solo copia). Per pubblicare: git push dentro il repo.")
        return

    print("3) Pubblico...")
    pubblica()
    print("\nOnline: "
          "https://michelecaomc-dotcom.github.io/SHOCKNOMICS/fruta-bomba/")


if __name__ == "__main__":
    main()
