#!/usr/bin/env python3
"""Pone el fondo de Bliss, recordando cual habia.

    python3 tools/set-wallpaper.py [--revert]

`plasma-apply-wallpaperimage` no guarda nada: cambia el fondo de todos los
escritorios y lo anterior se pierde. Aqui se lee antes, se anota en
backup/wallpaper/ y --revert lo devuelve. Sin eso, `make revert-all` no
podria deshacer el fondo y seria un "revertir todo" a medias.
"""
import argparse
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HOME = pathlib.Path.home()
APPLETSRC = HOME / ".config/plasma-org.kde.plasma.desktop-appletsrc"
STATE = ROOT / "backup" / "wallpaper"
MARK = STATE / "previous"
PACKAGE = HOME / ".local/share/wallpapers/Bliss"

# [Containments][N][Wallpaper][org.kde.image][General] ... Image=...
GROUP = re.compile(
    r"^\[Containments\]\[\d+\]\[Wallpaper\]\[org\.kde\.image\]\[General\]\n"
    r"((?:(?!\[).*\n)*)", re.M)


def current():
    """El primer fondo que tenga configurado un escritorio, si hay alguno."""
    if not APPLETSRC.exists():
        return None
    text = APPLETSRC.read_text()
    for m in GROUP.finditer(text):
        img = re.search(r"^Image=(.*)$", m.group(1), re.M)
        if img and img.group(1).strip():
            return img.group(1).strip()
    return None


def apply_image(path):
    if not shutil.which("plasma-apply-wallpaperimage"):
        sys.exit("!! falta plasma-apply-wallpaperimage (paquete plasma-workspace)")
    subprocess.run(["plasma-apply-wallpaperimage", str(path)], check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--revert", action="store_true")
    a = ap.parse_args()

    if a.revert:
        if not MARK.exists():
            print("   fondo     -- no hay nada guardado que restaurar")
            return 0
        old = MARK.read_text().strip()
        MARK.unlink()
        if not old:
            print("   fondo     -- antes no tenias ninguno configurado, se deja asi")
            return 0
        apply_image(old)
        print(f"   fondo     -> restaurado: {old}")
        return 0

    if not PACKAGE.exists():
        sys.exit(f"!! falta {PACKAGE}. Ejecuta antes: make install")

    old = current()
    # Si ya estaba puesto el nuestro no se pisa la anotacion: repetir el
    # comando dejaria "Bliss" como el fondo "de antes".
    if old and "wallpapers/Bliss" not in old:
        STATE.mkdir(parents=True, exist_ok=True)
        MARK.write_text(old)
        print(f"   fondo     -- anotado el anterior en {MARK.relative_to(ROOT)}")
    elif not MARK.exists():
        # Aqui `old` esta vacio o YA es el nuestro. En los dos casos la marca
        # debe quedar vacia: anotar "Bliss" como el fondo de antes haria que
        # --revert volviese a poner el nuestro, que no es revertir nada.
        STATE.mkdir(parents=True, exist_ok=True)
        MARK.write_text("")

    apply_image(PACKAGE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
