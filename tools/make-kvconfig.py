#!/usr/bin/env python3
"""Genera Bliss.kvconfig a partir del kvconfig de un tema base.

    python3 tools/make-kvconfig.py <base.kvconfig> <destino.kvconfig> [--dark]

La geometria y los nombres de grupo del tema base se conservan INTACTOS: tienen
que seguir cuadrando con los IDs de Bliss.svg, que sale del mismo tema. Solo se
reescribe la paleta y los colores de texto que el tema base daba por supuestos.
"""
import re
import sys

GENERAL = {
    "author": "Miguel (derivado de KvBeige, de Tsu Jan)",
    "comment": "Bliss — Windows XP Luna x Frutiger Aero",
}

COLORS = {
    "window.color": "#ECE9D8", "base.color": "#FFFFFF", "alt.base.color": "#F4F3EB",
    "button.color": "#ECE9D8", "light.color": "#FFFFFF", "mid.light.color": "#F5F3E9",
    "dark.color": "#716F64", "mid.color": "#ACA899",
    "highlight.color": "#316AC5", "inactive.highlight.color": "#7A96DF",
    "text.color": "#000000", "inactive.text.color": "#000000bf",
    "window.text.color": "#000000", "inactive.window.text.color": "#000000bf",
    "button.text.color": "#000000", "inactive.button.text.color": "#000000bf",
    "disabled.text.color": "#ACA899", "tooltip.text.color": "#000000",
    "highlight.text.color": "#FFFFFF",
    "link.color": "#0066CC", "link.visited.color": "#551A8B",
    "progress.indicator.text.color": "#FFFFFF",
}

# KvBeige pone el texto de menu en BLANCO porque su fondo de menu es oscuro.
# El de XP es casi blanco, asi que heredarlo dejaria el texto invisible.
# El resaltado si es azul Luna, y ahi el texto va blanco.
TEXT_FIXES = {
    "MenuItem": {"text.normal.color": "#000000",
                 "text.normal.inactive.color": "#000000bf",
                 "text.focus.color": "#FFFFFF"},
    "MenuBarItem": {"text.normal.color": "#000000",
                    "text.focus.color": "#FFFFFF",
                    "text.press.color": "#FFFFFF"},
    "ItemView": {"text.toggle.color": "#FFFFFF",
                 "text.press.color": "#FFFFFF"},
}

DARK = {
    "window.color": "#2E343B", "base.color": "#22272D", "alt.base.color": "#272D34",
    "button.color": "#394048", "light.color": "#454D56", "mid.light.color": "#3A4149",
    "dark.color": "#171B20", "mid.color": "#2A3036",
    "highlight.color": "#2F6ABF", "inactive.highlight.color": "#3A4A60",
    "text.color": "#E8EDF2", "inactive.text.color": "#E8EDF2bf",
    "window.text.color": "#E8EDF2", "inactive.window.text.color": "#E8EDF2bf",
    "button.text.color": "#E8EDF2", "inactive.button.text.color": "#E8EDF2bf",
    "disabled.text.color": "#7A848E", "tooltip.text.color": "#E8EDF2",
    "highlight.text.color": "#FFFFFF",
    "link.color": "#6DBAF5", "link.visited.color": "#B496DC",
    "progress.indicator.text.color": "#FFFFFF",
}

# En oscuro el fondo del menu ya es oscuro, asi que el texto normal va claro.
DARK_TEXT_FIXES = {
    "MenuItem": {"text.normal.color": "#E8EDF2",
                 "text.normal.inactive.color": "#E8EDF2bf",
                 "text.focus.color": "#FFFFFF"},
    "MenuBarItem": {"text.normal.color": "#E8EDF2",
                    "text.focus.color": "#FFFFFF",
                    "text.press.color": "#FFFFFF"},
    "ItemView": {"text.toggle.color": "#FFFFFF",
                 "text.press.color": "#FFFFFF"},
}

HEADER = """# Bliss.kvconfig — estilo de widgets de aplicacion
#
# GENERADO por tools/make-kvconfig.py. No editar a mano: usa `make kvantum`.
#
# Derivado de KvBeige (Tsu Jan, GPL). La geometria y los nombres de grupo se
# conservan porque tienen que cuadrar con los IDs de Bliss.svg, que sale del
# mismo tema base.
#
# Aplicar:       kvantummanager --set Bliss
# Previsualizar: kvantumpreview
"""


def patch(text, group, mapping):
    m = re.search(rf"(^\[{re.escape(group)}\]\n)(.*?)(?=^\[|\Z)", text, re.S | re.M)
    if not m:
        return text + f"\n[{group}]\n" + "".join(f"{k}={v}\n" for k, v in mapping.items())
    lines = m.group(2).splitlines()
    while lines and not lines[-1].strip():   # las claves nuevas van DENTRO del grupo
        lines.pop()
    body, seen = [], set()
    for line in lines:
        key = line.split("=", 1)[0].strip()
        if key in mapping:
            body.append(f"{key}={mapping[key]}")
            seen.add(key)
        else:
            body.append(line)
    body += [f"{k}={v}" for k, v in mapping.items() if k not in seen]
    return text[:m.start(2)] + "\n".join(body).rstrip() + "\n\n" + text[m.end(2):]


def main(src, dst, dark=False):
    cfg = open(src).read()
    general = dict(GENERAL)
    if dark:
        general["comment"] = "Bliss Dark — cristal de oceano profundo"
    cfg = patch(cfg, "%General", general)
    cfg = patch(cfg, "GeneralColors", DARK if dark else COLORS)
    for group, fixes in (DARK_TEXT_FIXES if dark else TEXT_FIXES).items():
        cfg = patch(cfg, group, fixes)
    open(dst, "w").write(HEADER + "\n" + cfg)
    fixes = DARK_TEXT_FIXES if dark else TEXT_FIXES
    print(f"{dst}: paleta {'pizarra (oscuro)' if dark else 'Luna (claro)'} "
          f"+ {len(fixes)} grupos de texto corregidos")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        sys.exit(__doc__)
    main(args[0], args[1], dark="--dark" in sys.argv)
