#!/usr/bin/env python3
"""Genera el tema Aurorae oscuro a partir del claro.

    python3 tools/make-dark-aurorae.py

La GEOMETRIA no cambia: mismos ids, mismo 9-slice, mismo Blissrc salvo el
nombre. Solo se escala la LUMINOSIDAD de cada color, conservando tono y
saturacion. Por eso el modo oscuro sale barato: todo el trabajo de estructura
ya esta hecho y validado.

Dos factores distintos a proposito:
  decoracion 0.58 — la barra de titulo debe hundirse para no deslumbrar
                    contra ventanas oscuras
  botones    0.82 — son lo interactivo y tienen que seguir leyendose

El blanco puro se deja intacto: define la mascara de opacidad, el brillo de
cristal y los glifos de los botones. Escalarlo romperia los tres.
"""
import colorsys
import json
import re
import shutil
from pathlib import Path

SRC = Path("src/aurorae/Bliss")
DST = Path("src/aurorae/Bliss-Dark")
FACTOR = {"decoration.svg": 0.58}
DEFAULT_FACTOR = 0.82
KEEP = {"ffffff", "fff"}


def darken(hexstr, factor):
    if hexstr.lower() in KEEP:
        return hexstr
    r, g, b = (int(hexstr[i:i + 2], 16) / 255 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(h, max(0.0, min(1.0, l * factor)), s)
    return "".join(f"{round(c * 255):02x}" for c in (r, g, b))


def main():
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST)

    for svg in sorted(DST.glob("*.svg")):
        factor = FACTOR.get(svg.name, DEFAULT_FACTOR)
        text = svg.read_text()
        out = re.sub(r"#([0-9a-fA-F]{6})\b",
                     lambda m: "#" + darken(m.group(1), factor), text)
        out = out.replace("<!--\n  Bliss —", "<!--\n  Bliss Dark (GENERADO por tools/make-dark-aurorae.py) —")
        svg.write_text(out)
        print(f"  {svg.name:16} luminosidad x{factor}")

    # el rc cambia de nombre pero NO de geometria
    rc = (DST / "Blissrc")
    body = rc.read_text()
    body = body.replace("# Bliss — configuracion de la decoracion Aurorae",
                        "# Bliss Dark — GENERADO por tools/make-dark-aurorae.py\n"
                        "# Geometria identica a Bliss: solo cambian los colores de texto.")
    body = body.replace("ActiveTextShadowColor=0,40,110,160",
                        "ActiveTextShadowColor=0,0,0,180")
    body = body.replace("InactiveTextColor=222,233,250", "InactiveTextColor=154,165,177")
    body = body.replace("InactiveTextShadowColor=60,90,150,120",
                        "InactiveTextShadowColor=0,0,0,140")
    rc.unlink()
    (DST / "Bliss-Darkrc").write_text(body)

    meta = json.loads((DST / "metadata.json").read_text())
    meta["KPlugin"]["Id"] = "Bliss-Dark"
    meta["KPlugin"]["Name"] = "Bliss Dark"
    meta["KPlugin"]["Description"] = "Luna geometry, deep-ocean Aero palette"
    (DST / "metadata.json").write_text(json.dumps(meta, indent=4) + "\n")
    print(f"  {DST} listo")


if __name__ == "__main__":
    main()
