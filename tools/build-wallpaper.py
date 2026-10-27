#!/usr/bin/env python3
"""Arma el paquete de fondo de pantalla a partir de los SVG maestros.

Plasma busca los ficheros por nombre de resolucion dentro de
contents/images/ (claro) y contents/images_dark/ (oscuro), y se queda con el
mas parecido a la pantalla. Aqui se publican SVG, no PNG, por dos razones:
pesan unos pocos kilobytes en vez de decenas de megas en el repositorio, y
el dibujo es vectorial, asi que se rasteriza nitido a cualquier densidad.

Como un SVG se estira a lo que le pidan, publicar uno solo deformaria el
paisaje en pantallas con otra proporcion. Por eso cada resolucion lleva su
propio recorte del mismo maestro: cambia el viewBox, no el dibujo.

El recorte vertical se ancla al horizonte, no al centro del lienzo: en 4:3 o
en vertical lo que no puede moverse es la linea donde la loma corta el cielo.
"""
import pathlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

MASTER_W, MASTER_H = 3840.0, 2400.0

# Altura del horizonte en el maestro, y en que fraccion de alto queremos que
# caiga en el recorte. Por debajo de 0.5 el cielo manda; 0.56 deja la loma
# algo mas presente, como en el encuadre original.
HORIZON_Y = 1300.0
HORIZON_AT = 0.56

# Una por proporcion util. Plasma interpola el resto eligiendo la mas cercana.
TARGETS = [
    (1920, 1080),   # 16:9
    (2560, 1440),   # 16:9 (pantallas densas)
    (3840, 2160),   # 16:9 4K
    (1920, 1200),   # 16:10
    (2560, 1600),   # 16:10
    (1600, 1200),   # 4:3
    (1280, 1024),   # 5:4
    (3440, 1440),   # 21:9 ultrapanoramica
    (1080, 1920),   # vertical
]

ROOT_RE = re.compile(r"<svg\b[^>]*>", re.S)


def crop_for(w: int, h: int) -> tuple[float, float, float, float]:
    """Mayor rectangulo de proporcion w:h que cabe en el maestro."""
    aspect = w / h
    if aspect >= MASTER_W / MASTER_H:
        cw, ch = MASTER_W, MASTER_W / aspect
    else:
        cw, ch = MASTER_H * aspect, MASTER_H

    x = (MASTER_W - cw) / 2.0
    y = HORIZON_Y - HORIZON_AT * ch
    y = max(0.0, min(MASTER_H - ch, y))        # sin salirse del lienzo
    return x, y, cw, ch


def retarget(master: str, w: int, h: int) -> str:
    """Mismo SVG, otra ventana. Solo se reescribe la etiqueta raiz."""
    x, y, cw, ch = crop_for(w, h)
    root = ROOT_RE.search(master)
    if not root:
        raise SystemExit("!! el maestro no tiene etiqueta <svg> reconocible")

    new = (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{w}" height="{h}" '
        f'viewBox="{x:.1f} {y:.1f} {cw:.1f} {ch:.1f}" '
        'preserveAspectRatio="xMidYMid slice">'
    )
    return master[:root.start()] + new + master[root.end():]


METADATA = """{
    "KPlugin": {
        "Authors": [
            {
                "Name": "Miguel"
            }
        ],
        "Description": "Colina y cielo, al estilo de Windows XP",
        "Description[en]": "Rolling hill and sky, Windows XP style",
        "Id": "Bliss",
        "License": "CC-BY-SA-4.0",
        "Name": "Bliss",
        "Version": "1.0"
    },
    "KPackageStructure": "Wallpaper/Images"
}
"""


def main(srcdir: str) -> int:
    src = pathlib.Path(srcdir)
    contents = src / "contents"

    pairs = [("bliss.svg", "images"), ("bliss-dark.svg", "images_dark")]
    for name, subdir in pairs:
        master_path = src / name
        if not master_path.exists():
            print(f"!! falta {master_path}", file=sys.stderr)
            return 1
        master = master_path.read_text()

        out = contents / subdir
        out.mkdir(parents=True, exist_ok=True)
        for old in out.glob("*.svg"):
            old.unlink()

        for w, h in TARGETS:
            svg = retarget(master, w, h)
            ET.fromstring(svg)              # nada roto sale de aqui
            (out / f"{w}x{h}.svg").write_text(svg)
        print(f"   {subdir:<11} -> {len(TARGETS)} recortes")

    (src / "metadata.json").write_text(METADATA)

    # Miniatura para el selector de fondos de Plasma. Es el unico PNG del
    # paquete y por eso se deja pequeno.
    shot = contents / "screenshot.png"
    try:
        subprocess.run(
            ["inkscape", str(contents / "images" / "1920x1080.svg"),
             "-w", "640", "-h", "360", "-o", str(shot)],
            check=True, capture_output=True)
        print(f"   miniatura   -> {shot.relative_to(src)}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("   miniatura   -- omitida: falta inkscape")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "src/wallpapers/Bliss"))
