#!/usr/bin/env python3
"""Pone el icono y la etiqueta de Bliss en el boton Inicio del panel actual.

    python3 tools/set-start-button.py            # aplica
    python3 tools/set-start-button.py --revert   # vuelve al de Plasma

Kickoff acepta dos ajustes, `icon` y `menuLabel`, pero viven en el archivo de
configuracion del panel del usuario, no en el tema. Este script localiza el
applet de Kickoff — su numero cambia en cada equipo — y escribe ahi.

Toca la configuracion viva de plasmashell, asi que hace falta `make reload`
despues. Es reversible con --revert.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

CFG_NAME = "plasma-org.kde.plasma.desktop-appletsrc"
CFG = Path.home() / ".config" / CFG_NAME
PLUGIN = "org.kde.plasma.kickoff"
GROUP = re.compile(r"^\[Containments\]\[(\d+)\]\[Applets\]\[(\d+)\]$")


def find_kickoff():
    """Devuelve [(containment, applet)] de cada Kickoff del panel."""
    found, current = [], None
    for line in CFG.read_text().splitlines():
        if line.startswith("["):
            m = GROUP.match(line.strip())
            current = m.groups() if m else None
        elif current and line.strip() == f"plugin={PLUGIN}":
            found.append(current)
            current = None
    return found


def write(cont, applet, key, value):
    cmd = ["kwriteconfig6", "--file", CFG_NAME,
           "--group", "Containments", "--group", cont,
           "--group", "Applets", "--group", applet,
           "--group", "Configuration", "--group", "General",
           "--key", key]
    cmd += ["--delete"] if value is None else [value]
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--icon", default="bliss-start")
    ap.add_argument("--label", default="Inicio")
    ap.add_argument("--revert", action="store_true")
    a = ap.parse_args()

    if not CFG.exists():
        sys.exit(f"no encuentro {CFG}")
    targets = find_kickoff()
    if not targets:
        sys.exit("no hay ningun Kickoff en el panel. Anade primero un menu de aplicaciones.")

    for cont, applet in targets:
        if a.revert:
            write(cont, applet, "icon", None)
            write(cont, applet, "menuLabel", None)
            print(f"  Kickoff [{cont}][{applet}] -> restaurado")
        else:
            write(cont, applet, "icon", a.icon)
            write(cont, applet, "menuLabel", a.label)
            print(f"  Kickoff [{cont}][{applet}] -> icono {a.icon!r}, etiqueta {a.label!r}")
    print("Ahora: make reload")


if __name__ == "__main__":
    main()
