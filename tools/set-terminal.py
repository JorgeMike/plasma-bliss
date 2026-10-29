#!/usr/bin/env python3
"""Pone (o quita) el aspecto de consola antigua en Konsole y starship.

    python3 tools/set-terminal.py [--revert] [--only konsole|starship]

Toca configuracion del USUARIO, no del tema, igual que set-start-button.py:

  - el perfil por defecto de Konsole, para apuntarlo a Bliss.colorscheme
  - ~/.config/starship.toml, que afecta a TODAS las terminales, no solo a
    Konsole. Por eso se guarda copia antes y --revert la devuelve

Lo que habia se guarda en backup/terminal/, que esta fuera de git. Sin esa
copia no hay vuelta atras posible, asi que si falta, --revert lo dice en vez
de dejar el sistema a medias.
"""
import argparse
import configparser
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HOME = pathlib.Path.home()
KONSOLE_DIR = HOME / ".local/share/konsole"
KONSOLERC = HOME / ".config/konsolerc"
STARSHIP = HOME / ".config/starship.toml"
STATE = ROOT / "backup" / "terminal"

SCHEME = "Bliss"


def default_profile():
    """El perfil que Konsole abre al arrancar, segun konsolerc."""
    if not KONSOLERC.exists():
        return None
    c = configparser.ConfigParser(strict=False)
    c.read(KONSOLERC)
    name = c.get("Desktop Entry", "DefaultProfile", fallback="").strip()
    if not name:
        return None
    p = KONSOLE_DIR / name
    return p if p.exists() else None


def read_scheme(profile):
    c = configparser.ConfigParser(strict=False)
    c.read(profile)
    return c.get("Appearance", "ColorScheme", fallback="")


def write_scheme(profile, value):
    subprocess.run(["kwriteconfig6", "--file", str(profile),
                    "--group", "Appearance", "--key", "ColorScheme", value],
                   check=True)


def do_konsole(revert):
    profile = default_profile()
    if profile is None:
        print("   konsole   -- sin perfil por defecto en konsolerc, omitido")
        return
    mark = STATE / "konsole-colorscheme"
    if revert:
        if not mark.exists():
            print("   konsole   -- no hay nada guardado que restaurar")
            return
        old = mark.read_text().strip()
        write_scheme(profile, old)
        mark.unlink()
        print(f"   konsole   -> {profile.name}: ColorScheme={old or '(vacio)'}")
        return

    current = read_scheme(profile)
    if current == SCHEME:
        print(f"   konsole   -- {profile.name} ya usa {SCHEME}")
        return
    STATE.mkdir(parents=True, exist_ok=True)
    mark.write_text(current)
    write_scheme(profile, SCHEME)
    print(f"   konsole   -> {profile.name}: ColorScheme={SCHEME} "
          f"(antes: {current or '(vacio)'})")


def do_starship(revert):
    src = ROOT / "src/starship/bliss.toml"
    saved = STATE / "starship.toml"
    if revert:
        if saved.exists():
            shutil.copy2(saved, STARSHIP)
            saved.unlink()
            print(f"   starship  -> restaurado tu {STARSHIP.name} de antes")
        elif (STATE / "starship.absent").exists():
            STARSHIP.unlink(missing_ok=True)
            (STATE / "starship.absent").unlink()
            print("   starship  -> borrado (antes no tenias archivo)")
        else:
            print("   starship  -- no hay nada guardado que restaurar")
        return

    if not src.exists():
        sys.exit(f"!! falta {src}")
    STATE.mkdir(parents=True, exist_ok=True)
    if STARSHIP.exists():
        if not saved.exists():        # no pisar la copia buena al repetir
            shutil.copy2(STARSHIP, saved)
            print(f"   starship  -- copia de tu config en "
                  f"{saved.relative_to(ROOT)}")
    else:
        (STATE / "starship.absent").touch()
    shutil.copy2(src, STARSHIP)
    print(f"   starship  -> {STARSHIP}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--revert", action="store_true")
    ap.add_argument("--only", choices=("konsole", "starship"))
    a = ap.parse_args()

    if a.only in (None, "konsole"):
        do_konsole(a.revert)
    if a.only in (None, "starship"):
        do_starship(a.revert)

    if not a.revert:
        print("   las pestañas de Konsole ya abiertas no cambian de esquema: "
              "abre una nueva")
    return 0


if __name__ == "__main__":
    sys.exit(main())
