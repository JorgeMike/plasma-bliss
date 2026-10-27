#!/usr/bin/env python3
"""Genera bliss-dark.svg a partir de bliss.svg.

La composicion no cambia: es el mismo paisaje al anochecer. Lo unico que se
sustituye es el pigmento, y se hace con un mapa explicito color->color en vez
de escalar luminancias, porque aqui no basta con oscurecer: el cielo tiene que
virar a azul de noche y la hierba perder saturacion, no solo luz.

Cualquier color del maestro que no este en el mapa es un error: asi, si
manana se anade una forma nueva y se olvida su equivalente oscuro, el script
lo dice en vez de dejar un trozo diurno en mitad de la noche.
"""
import random
import re
import sys
import pathlib
import xml.etree.ElementTree as ET

# claro -> oscuro
PALETTE = {
    # Cielo: de mediodia a noche cerrada, conservando el degradado.
    "1b5ac0": "03070f",
    "2f7bdf": "071024",
    "68aef2": "0d2147",
    "a8d8fa": "173c70",
    "e8f6fe": "27548f",

    # Blancos: nubes, resplandor, brillo de hierba y burbujas. De noche no son
    # blancos sino luz de luna, fria y mucho mas apagada. El propio
    # stop-opacity del maestro hace el resto.
    "ffffff": "7891c0",
    "c9dcf2": "101f33",   # panza de nube

    # Loma. Pierde luz y saturacion: de noche el verde tira a gris azulado.
    "a6dc55": "243f1e",
    "86c93f": "1c3318",
    "5fa92e": "152612",
    "3c821f": "132410",
    "2b6a17": "0d1a0a",
    "c9ee7e": "4e6b38",   # canto de la cresta
    "9cc49a": "1a3356",   # loma de fondo: a esa distancia es ya casi cielo

    # Vineta. Igual de negra, pero mas marcada.
    "000000": "000000",
}

HEX = re.compile(r"#([0-9a-fA-F]{6})\b")


def stars(seed: int = 20060101) -> str:
    """Un campo de estrellas reproducible.

    Solo existe en la variante oscura, por eso se inyecta aqui y no esta en
    el maestro: de dia serian puntos blancos sobre el cielo azul.

    La semilla es fija para que dos ejecuciones den el mismo fichero y el
    diff de git siga siendo legible. Se mantienen por encima de y=1150, que
    es donde arranca la loma.
    """
    rng = random.Random(seed)
    out = ['  <g id="stars">']
    for _ in range(90):
        x = rng.uniform(20, 3820)
        y = rng.uniform(20, 1150)
        # Mas densas arriba, donde el cielo es mas oscuro y se ven de verdad.
        if rng.random() > (1.0 - y / 1400.0):
            continue
        r = rng.choice([3.0, 3.5, 4.0, 4.5, 6.0])
        o = round(rng.uniform(0.25, 0.85), 2)
        out.append(f'    <circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" '
                   f'fill="#dfe9fb" opacity="{o}"/>')
    out.append("  </g>")
    return "\n".join(out)


def main(src: str, dst: str) -> int:
    text = pathlib.Path(src).read_text()

    found = {m.group(1).lower() for m in HEX.finditer(text)}
    missing = sorted(found - PALETTE.keys())
    if missing:
        print(f"!! sin equivalente oscuro: {', '.join('#' + c for c in missing)}",
              file=sys.stderr)
        print("   anade cada uno a PALETTE en tools/make-dark-wallpaper.py",
              file=sys.stderr)
        return 1

    out = HEX.sub(lambda m: "#" + PALETTE[m.group(1).lower()], text)

    sky = '<rect x="0" y="0" width="3840" height="2400" fill="url(#g-sky)"/>'
    assert out.count(sky) == 1, "no encuentro el rectangulo del cielo"
    out = out.replace(sky, sky + "\n\n" + stars())

    # La vineta nocturna aguanta mas: el escritorio ya es oscuro y sin ella
    # las esquinas quedan planas.
    out = out.replace('stop-color="#000000" stop-opacity="0.16"',
                      'stop-color="#000000" stop-opacity="0.30"')

    out = out.replace("Bliss — fondo de escritorio maestro.",
                      "Bliss — fondo de escritorio, variante oscura.\n"
                      "  GENERADO por tools/make-dark-wallpaper.py desde bliss.svg. No lo edites.")

    ET.fromstring(out)        # que no salga un SVG roto de aqui
    pathlib.Path(dst).write_text(out)
    print(f"   fondo oscuro -> {dst}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("uso: make-dark-wallpaper.py <bliss.svg> <bliss-dark.svg>")
    sys.exit(main(sys.argv[1], sys.argv[2]))
