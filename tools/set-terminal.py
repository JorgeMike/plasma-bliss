#!/usr/bin/env python3
"""Pone (o quita) el aspecto de consola antigua en Konsole y starship.

    python3 tools/set-terminal.py [--revert] [--only konsole|starship]

Toca configuracion del USUARIO, no del tema, igual que set-start-button.py:

  - el perfil por defecto de Konsole, para apuntarlo a Bliss.colorscheme
  - ~/.config/starship.toml, que afecta a TODAS las terminales, no solo a
    Konsole. Por eso se guarda copia antes y --revert la devuelve
  - ~/.config/shell/common.sh, solo el bloque FZF_DEFAULT_OPTS: ahi vivian
    los colores de la busqueda inversa (Ctrl+R). Lo cargan .zshrc y .bashrc
  - ~/.config/btop/btop.conf, solo cinco claves, para que btop use los
    dieciseis colores del terminal en vez de sus gradientes de 24 bits

Lo que habia se guarda en backup/terminal/, que esta fuera de git. Sin esa
copia no hay vuelta atras posible, asi que si falta, --revert lo dice en vez
de dejar el sistema a medias.
"""
import argparse
import configparser
import re
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HOME = pathlib.Path.home()
KONSOLE_DIR = HOME / ".local/share/konsole"
KONSOLERC = HOME / ".config/konsolerc"
STARSHIP = HOME / ".config/starship.toml"
# Lo cargan .zshrc y .bashrc, asi que afecta a los dos interpretes.
COMMON = HOME / ".config/shell/common.sh"
BTOP = HOME / ".config/btop/btop.conf"
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


# Ctrl+R lo atiende fzf, y fzf se pinta con lo que diga FZF_DEFAULT_OPTS. Si
# esa variable trae colores hex — el bloque que venia era Tokyo Night — la
# busqueda inversa ignora el palé del terminal y aparece con los colores de
# antes sobre el fondo negro. Mismo problema que tenia el prompt.
#
# Aqui solo hay indices ANSI: -1 es "el color por defecto del terminal", y la
# linea seleccionada va en video inverso (texto 0 sobre fondo 7), que es como
# resaltaba una consola de verdad.
FZF_BLOCK = '''# fzf: colores del terminal (tema Bliss)
export FZF_DEFAULT_OPTS="--height 45% --layout=reverse --border=sharp --info=inline \\
--color=fg:-1,bg:-1,hl:3 \\
--color=fg+:0,bg+:7,hl+:3 \\
--color=prompt:15,pointer:15,marker:10,spinner:8,info:8,header:8,border:8"'''

FZF_RE = re.compile(
    r'^(?:#[^\n]*\n)?export FZF_DEFAULT_OPTS="[^"]*"', re.M)


def do_fzf(revert):
    saved = STATE / "common.sh"
    if revert:
        if saved.exists():
            shutil.copy2(saved, COMMON)
            saved.unlink()
            print(f"   fzf       -> restaurado tu {COMMON.name} de antes")
        else:
            print("   fzf       -- no hay nada guardado que restaurar")
        return

    if not COMMON.exists():
        print(f"   fzf       -- no existe {COMMON}, omitido")
        return
    text = COMMON.read_text()
    if "tema Bliss" in text:
        print("   fzf       -- ya estaba puesto")
        return
    if not FZF_RE.search(text):
        print(f"   fzf       -- no encuentro el bloque FZF_DEFAULT_OPTS en "
              f"{COMMON.name}, omitido")
        return

    STATE.mkdir(parents=True, exist_ok=True)
    if not saved.exists():
        shutil.copy2(COMMON, saved)
        print(f"   fzf       -- copia de {COMMON.name} en "
              f"{saved.relative_to(ROOT)}")
    COMMON.write_text(FZF_RE.sub(FZF_BLOCK, text, count=1))
    print(f"   fzf       -> {COMMON} (Ctrl+R sigue al palé del terminal)")


# btop se pinta con su propio tema, no con el del terminal: de serie usa
# gradientes de 24 bits. Con estas claves pasa a los dieciseis ANSI y hereda
# el palé. Se escriben SOLO estas; el resto del fichero no se toca, porque
# btop guarda ahi todas las preferencias del usuario.
BTOP_KEYS = {
    "color_theme": '"TTY"',
    "theme_background": "False",
    "truecolor": "False",
    "force_tty": "True",
    "rounded_corners": "False",
}


def do_btop(revert):
    saved = STATE / "btop.conf"
    created = STATE / "btop.created"
    if revert:
        if saved.exists():
            shutil.copy2(saved, BTOP)
            saved.unlink()
            print("   btop      -> restaurado tu btop.conf de antes")
        elif created.exists():
            BTOP.unlink(missing_ok=True)
            created.unlink()
            print("   btop      -> borrado (antes no tenias configuracion)")
        else:
            print("   btop      -- no hay nada guardado que restaurar")
        return

    STATE.mkdir(parents=True, exist_ok=True)
    if BTOP.exists():
        if not saved.exists():
            shutil.copy2(BTOP, saved)
            print(f"   btop      -- copia en {saved.relative_to(ROOT)}")
        lines = BTOP.read_text().splitlines()
    else:
        BTOP.parent.mkdir(parents=True, exist_ok=True)
        created.touch()
        lines = []

    seen = set()
    out = []
    for line in lines:
        key = line.split("=", 1)[0].strip()
        if key in BTOP_KEYS and not line.lstrip().startswith("#"):
            out.append(f"{key} = {BTOP_KEYS[key]}")
            seen.add(key)
        else:
            out.append(line)
    out += [f"{k} = {v}" for k, v in BTOP_KEYS.items() if k not in seen]
    BTOP.write_text("\n".join(out) + "\n")
    print(f"   btop      -> {BTOP} ({len(BTOP_KEYS)} claves)")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--revert", action="store_true")
    ap.add_argument("--only", choices=("konsole", "starship", "fzf", "btop"))
    a = ap.parse_args()

    if a.only in (None, "konsole"):
        do_konsole(a.revert)
    if a.only in (None, "starship"):
        do_starship(a.revert)
    if a.only in (None, "fzf"):
        do_fzf(a.revert)
    if a.only in (None, "btop"):
        do_btop(a.revert)

    if not a.revert:
        print("   las pestañas de Konsole ya abiertas no cambian de esquema: "
              "abre una nueva")
    return 0


if __name__ == "__main__":
    sys.exit(main())
