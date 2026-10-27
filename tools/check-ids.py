#!/usr/bin/env python3
"""Comprueba que los SVG tienen los IDs que KSvg::FrameSvg va a pedir.

Un SVG puede ser XML perfectamente valido y aun asi dibujarse como basura si le
falta un ID. Esta es la comprobacion que de verdad importa.

Referencia (leida de /usr/share/kwin/aurorae/*.qml en Plasma 6.3):
  decoration.svg -> prefijos "decoration", "decoration-inactive", "mask",
                    y opcionales "decoration-maximized", "innerborder"
  botones        -> prefijos "active" (obligatorio), "hover", "pressed",
                    "inactive", "deactivated"
Cada prefijo necesita las 9 partes del 9-slice.
"""
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

PARTS = ["topleft", "top", "topright", "left", "center", "right",
         "bottomleft", "bottom", "bottomright"]


def ids(path):
    return {e.get("id") for e in ET.parse(path).iter() if e.get("id")}


def need(found, label, required, fmt):
    missing = [p for p in required if fmt(p) not in found]
    if missing:
        print(f"  FALTA  {label}: {', '.join(fmt(p) for p in missing)}")
        return 1
    print(f"  ok     {label}")
    return 0


def boxes(path):
    """Caja de cada elemento con id, tal y como la ve el renderizador.

    Kvantum escala cada pieza del 9-slice a su hueco, asi que la caja es lo
    que fija el radio de esquina y el grosor del bisel. Comparar cajas entre
    claro y oscuro es, literalmente, comprobar que tienen la misma forma.
    """
    out = subprocess.run(["inkscape", "--query-all", path],
                         capture_output=True, text=True).stdout
    box = {}
    for line in out.splitlines():
        parts = line.split(",")
        if len(parts) == 5:
            box[parts[0]] = tuple(round(float(v), 2) for v in parts[1:])
    return box


def kvantum_geometry():
    """Bliss y Bliss-Dark salen de la misma base, asi que deben coincidir.

    Es la comprobacion que habria cazado el fallo de origen: la oscura se
    generaba desde KvCurves3d y traia botones en forma de capsula, cuando
    Luna los quiere a 3 px de radio.
    """
    light = "src/kvantum/Bliss/Bliss.svg"
    dark = "src/kvantum/Bliss-Dark/Bliss-Dark.svg"
    if not (os.path.exists(light) and os.path.exists(dark)):
        print("  --     kvantum: sin generar, omitido")
        return 0
    if not shutil.which("inkscape"):
        print("  --     kvantum: falta inkscape, omitido")
        return 0

    # Solo los ids ESCRITOS en el fichero. Inkscape inventa un id por cada
    # elemento anonimo ("circle346") numerandolos por orden de documento, asi
    # que en cuanto una variante tiene un elemento de mas — la fase 2 clona
    # degradados — esos nombres dejan de referirse a la misma forma y la
    # comparacion da falsos positivos. Los ids del tema si son estables.
    named = ids(light) & ids(dark)
    a = {k: v for k, v in boxes(light).items() if k in named}
    b = {k: v for k, v in boxes(dark).items() if k in named}

    only = (set(a) ^ set(b))
    moved = [k for k in set(a) & set(b) if a[k] != b[k]]
    if only or moved:
        print(f"  FALTA  kvantum: Bliss-Dark no comparte geometria con Bliss "
              f"({len(moved)} elementos movidos, {len(only)} descuadrados)")
        for k in sorted(moved)[:5]:
            print(f"           {k}: {a[k]} vs {b[k]}")
        return 1
    print(f"  ok     kvantum: Bliss-Dark comparte geometria con Bliss "
          f"({len(a)} elementos)")
    return 0


def main():
    bad = 0
    # La variante oscura se genera desde la clara y debe tener EXACTAMENTE los
    # mismos ids: si divergen, el generador ha roto algo.
    for theme in ("Bliss", "Bliss-Dark"):
        base = f"src/aurorae/{theme}"
        if not os.path.isdir(base):
            print(f"  FALTA  {base} (ejecuta: make dark)")
            bad = 1
            continue
        deco = ids(f"{base}/decoration.svg")
        for prefix in ("decoration", "decoration-inactive", "mask",
                       "decoration-maximized", "decoration-maximized-inactive"):
            bad |= need(deco, f"{theme}/decoration.svg [{prefix}]", PARTS,
                        lambda p, x=prefix: f"{x}-{p}")

        for btn in ("close", "minimize", "maximize", "restore", "alldesktops",
                    "keepabove", "keepbelow", "shade", "help"):
            found = ids(f"{base}/{btn}.svg")
            bad |= need(found, f"{theme}/{btn}.svg",
                        ["active", "hover", "pressed", "inactive"],
                        lambda s: f"{s}-center")

    if os.path.isdir("src/aurorae/Bliss-Dark"):
        same = ids("src/aurorae/Bliss/decoration.svg") == ids("src/aurorae/Bliss-Dark/decoration.svg")
        print(("  ok     " if same else "  FALTA  ")
              + "Bliss-Dark comparte geometria con Bliss")
        bad |= 0 if same else 1

    plasma = "src/plasma/desktoptheme/Bliss"
    panel = ids(f"{plasma}/widgets/panel-background.svg")
    bad |= need(panel, "panel-background.svg", PARTS, lambda p: p)

    # tasks.svg: taskPrefix() de tools.js devuelve ["south-<p>", "<p>"], asi que
    # el prefijo sin direccion cubre los cuatro bordes del panel.
    tasks = ids(f"{plasma}/widgets/tasks.svg")
    for prefix in ("normal", "hover", "focus", "minimized", "attention",
                   "launcher-hover"):
        bad |= need(tasks, f"tasks.svg [{prefix}]", PARTS,
                    lambda p, x=prefix: f"{x}-{p}")

    item = ids(f"{plasma}/widgets/listitem.svg")
    for prefix in ("normal", "hover", "pressed", "section", "separator"):
        bad |= need(item, f"listitem.svg [{prefix}]", PARTS,
                    lambda p, x=prefix: f"{x}-{p}")

    # dialogs/background.svg usa prefijo VACIO, mas "mask" para las esquinas
    dlg = ids(f"{plasma}/dialogs/background.svg")
    bad |= need(dlg, "dialogs/background.svg", PARTS, lambda p: p)
    bad |= need(dlg, "dialogs/background.svg [mask]", PARTS, lambda p: f"mask-{p}")

    # El tooltip va DOS veces: ToolTip.qml pide "solid/widgets/tooltip"
    # literalmente, y otros componentes usan "widgets/tooltip".
    for where in ("widgets", "solid/widgets"):
        tip = ids(f"{plasma}/{where}/tooltip.svg")
        bad |= need(tip, f"{where}/tooltip.svg", PARTS, lambda p: p)
        bad |= need(tip, f"{where}/tooltip.svg [mask]", PARTS, lambda p: f"mask-{p}")

    bad |= kvantum_geometry()

    return bad


if __name__ == "__main__":
    sys.exit(main())
