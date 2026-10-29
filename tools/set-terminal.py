#!/usr/bin/env python3
"""Pone (o quita) el aspecto de consola antigua en Konsole y starship.

    python3 tools/set-terminal.py [--revert] [--only konsole|starship]

Toca configuracion del USUARIO, no del tema, igual que set-start-button.py:

  - el perfil por defecto de Konsole, para apuntarlo a Bliss.colorscheme
  - ~/.config/starship.toml, que afecta a TODAS las terminales, no solo a
    Konsole. Por eso se guarda copia antes y --revert la devuelve
  - el bloque FZF_DEFAULT_OPTS, alla donde lo tengas: ahi viven los colores
    de la busqueda inversa (Ctrl+R). Se busca en ~/.config/shell/common.sh,
    .zshrc, .bashrc, .zshenv y .profile, y se toma el primero que lo defina
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
# FZF_DEFAULT_OPTS puede estar en cualquiera de estos. No hay un sitio
# estandar: ~/.config/shell/common.sh es una convencion personal, no de fzf.
# Se toma el PRIMERO que lo defina.
FZF_FILES = [
    HOME / ".config/shell/common.sh",
    HOME / ".zshrc",
    HOME / ".bashrc",
    HOME / ".zshenv",
    HOME / ".profile",
]
BTOP = HOME / ".config/btop/btop.conf"
STATE = ROOT / "backup" / "terminal"

SCHEME = "Bliss"


# Perfil minimo para cuando Konsole no tiene ninguno propio. Parent=FALLBACK/
# es el perfil integrado: heredamos todo y solo fijamos el esquema. No se
# toca la fuente a proposito — en una instalacion recien hecha no se sabe
# cual hay, y la de Konsole ya es monoespaciada.
NEW_PROFILE = """[Appearance]
ColorScheme=Bliss

[General]
Name=Bliss
Parent=FALLBACK/
"""


def default_profile():
    """El perfil que Konsole abre al arrancar, segun konsolerc.

    En una instalacion recien hecha no hay ninguno: Konsole usa su perfil
    integrado, que no tiene fichero, y konsolerc ni siquiera existe. Por eso
    devuelve tambien si lo encontro o no, para poder crearlo.
    """
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
    mark = STATE / "konsole-colorscheme"
    created = STATE / "konsole-profile-created"
    profile = default_profile()

    if revert:
        if created.exists():
            # El perfil lo creamos nosotros: se borra entero y se quita de
            # konsolerc, en vez de dejar un perfil huerfano por ahi.
            (KONSOLE_DIR / "Bliss.profile").unlink(missing_ok=True)
            subprocess.run(["kwriteconfig6", "--file", str(KONSOLERC),
                            "--group", "Desktop Entry",
                            "--key", "DefaultProfile", "--delete"], check=False)
            # Si konsolerc se queda sin una sola clave, lo creamos nosotros al
            # escribir DefaultProfile: se borra para dejarlo como estaba. Si
            # tiene cualquier otro ajuste del usuario, se respeta.
            if KONSOLERC.exists() and not any(
                    "=" in line for line in KONSOLERC.read_text().splitlines()):
                KONSOLERC.unlink()
            created.unlink()
            mark.unlink(missing_ok=True)
            print("   konsole   -> perfil Bliss borrado (antes no tenias ninguno)")
            return
        if profile is None or not mark.exists():
            print("   konsole   -- no hay nada guardado que restaurar")
            return
        old = mark.read_text().strip()
        write_scheme(profile, old)
        mark.unlink()
        print(f"   konsole   -> {profile.name}: ColorScheme={old or '(vacio)'}")
        return

    if profile is None:
        # Sin perfil propio, Konsole usa el integrado, que no tiene fichero
        # que parchear. Se crea uno que hereda de el y solo fija el esquema.
        if not shutil.which("konsole"):
            print("   konsole   -- no esta instalado, omitido")
            return
        KONSOLE_DIR.mkdir(parents=True, exist_ok=True)
        profile = KONSOLE_DIR / "Bliss.profile"
        profile.write_text(NEW_PROFILE)
        KONSOLERC.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["kwriteconfig6", "--file", str(KONSOLERC),
                        "--group", "Desktop Entry",
                        "--key", "DefaultProfile", "Bliss.profile"], check=True)
        STATE.mkdir(parents=True, exist_ok=True)
        created.touch()
        print(f"   konsole   -> creado {profile.name} y puesto por defecto "
              f"(no tenias perfil propio)")
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
    absent = STATE / "starship.absent"
    if STARSHIP.exists():
        # Ni al repetir se pisa la copia buena, ni se toma copia de lo que
        # escribimos nosotros (que es lo que dice el marcador `absent`).
        if not saved.exists() and not absent.exists():
            shutil.copy2(STARSHIP, saved)
            print(f"   starship  -- copia de tu config en "
                  f"{saved.relative_to(ROOT)}")
    else:
        absent.touch()
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


def fzf_file():
    """El primer fichero del usuario que defina FZF_DEFAULT_OPTS."""
    for f in FZF_FILES:
        if f.exists() and FZF_RE.search(f.read_text()):
            return f
    return None


def do_fzf(revert):
    saved = STATE / "fzf-source"
    name_mark = STATE / "fzf-source-name"
    if revert:
        if saved.exists() and name_mark.exists():
            target = pathlib.Path(name_mark.read_text().strip())
            shutil.copy2(saved, target)
            saved.unlink()
            name_mark.unlink()
            print(f"   fzf       -> restaurado tu {target.name} de antes")
        else:
            print("   fzf       -- no hay nada guardado que restaurar")
        return

    # Si ya esta puesto, no hay que buscar mas.
    for f in FZF_FILES:
        if f.exists() and "tema Bliss" in f.read_text():
            print("   fzf       -- ya estaba puesto")
            return

    target = fzf_file()
    if target is None:
        # No es un fallo: sin FZF_DEFAULT_OPTS propio, fzf usa los colores
        # del terminal, que es exactamente lo que queremos.
        print("   fzf       -- no defines FZF_DEFAULT_OPTS; Ctrl+R ya usa "
              "los colores del terminal")
        return

    STATE.mkdir(parents=True, exist_ok=True)
    if not saved.exists():
        shutil.copy2(target, saved)
        name_mark.write_text(str(target))
        print(f"   fzf       -- copia de {target.name} en "
              f"{saved.relative_to(ROOT)}")
    target.write_text(FZF_RE.sub(FZF_BLOCK, target.read_text(), count=1))
    print(f"   fzf       -> {target} (Ctrl+R sigue al palé del terminal)")


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
        # Si `created` existe, este fichero lo escribimos nosotros en una
        # pasada anterior: guardarlo como "original" dejaria a --revert
        # restaurando nuestra propia configuracion en vez de la de antes.
        if not saved.exists() and not created.exists():
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
