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


def main():
    bad = 0
    deco = ids("src/aurorae/Bliss/decoration.svg")
    for prefix in ("decoration", "decoration-inactive", "mask",
                   "decoration-maximized", "decoration-maximized-inactive"):
        bad |= need(deco, f"decoration.svg [{prefix}]", PARTS,
                    lambda p, x=prefix: f"{x}-{p}")

    for btn in ("close", "minimize", "maximize", "restore", "alldesktops",
                "keepabove", "keepbelow", "shade", "help"):
        found = ids(f"src/aurorae/Bliss/{btn}.svg")
        bad |= need(found, f"{btn}.svg",
                    ["active", "hover", "pressed", "inactive"],
                    lambda s: f"{s}-center")

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

    return bad


if __name__ == "__main__":
    sys.exit(main())
