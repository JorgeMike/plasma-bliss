#!/usr/bin/env python3
"""Espiga iconos de LinXP para el tema Bliss.

    python3 tools/fetch-icons.py [--list] [--keep-cache]

LinXP (github.com/B00merang-Artwork/LinXP) es una recreacion de los iconos de
Windows XP modelada sobre Mint-X: dibujo propio, no archivos extraidos de
Microsoft. Eso lo hace utilizable aqui, donde la regla es no redistribuir los
originales.

Pero NO se mete en el repositorio, por dos razones. No trae fichero de
licencia, asi que no podemos redistribuirlo; y es PNG, que no es lo que este
proyecto guarda como fuente. Se baja a build/, que esta fuera de git, y de
ahi lo recoge `make install`. Es el mismo trato que damos a KvBeige: la base
vive en el sistema, nosotros guardamos la receta.

Por que espigar y no usar LinXP entero:

  - De los 1025 nombres que declara, solo 210 tienen DIBUJO PROPIO. Los otros
    815 son alias que su script de compilacion rellena copiandolos de Mint-X,
    que ni es XP ni esta instalado en esta maquina. Se ve en los ficheros
    `meta` de cada icono: los que no traen PNG numerado solo listan rutas
    marcadas "Mint-X:".
  - Su index.theme hereda de gnome, hicolor y Mint-X-Yellow. En una Debian con
    KDE no hay ninguno de los tres, asi que instalado tal cual no se ve
    incompleto: se ve roto.

Aqui se coge solo lo que se ve a diario — carpetas, dispositivos y tipos de
archivo — y el resto lo pone breeze-dark por herencia, que es de lo que hereda
nuestro index.theme.

La seleccion no esta escrita a mano: son los iconos de LinXP cuyo nombre
tambien define Breeze. Es decir, los que el escritorio pide de verdad. Si un
dia LinXP crece, la lista crece sola.
"""
import argparse
import os
import pathlib
import shutil
import subprocess
import sys
import tarfile
import tempfile

URL = "https://codeload.github.com/B00merang-Artwork/LinXP/tar.gz/refs/heads/master"
ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "build" / "cache"
DEST = ROOT / "build" / "icons" / "Bliss"

# Contexto de LinXP -> contextos de Breeze contra los que se compara.
#
# No siempre coinciden: LinXP mete en `apps` los iconos que Breeze guarda en
# `preferences` (los paneles de Ajustes del sistema). Comparando solo contra
# `apps` se perdian doce, incluido el `utilities-terminal` que pide el
# lanzador de Konsole.
CONTEXTS = {
    "places": ("places",),
    "devices": ("devices",),
    "mimetypes": ("mimetypes",),
    "apps": ("apps", "preferences", "categories"),
}

# Nombres que KDE pide y LinXP llama de otra forma. Sin esto, la carpeta
# personal — de los iconos mas visibles que hay — se quedaria sin cambiar.
#
# El origen puede venir de OTRO contexto, escrito "contexto/nombre". Hace
# falta para inode-directory, que es el tipo MIME de una carpeta y que Breeze
# define en mimetypes aunque el dibujo este en places. Sin esa linea, las
# carpetas se quedaban con el icono heredado en las vistas que piden el
# tipo MIME en vez del lugar.
#   destino: origen en LinXP
ALIASES = {
    "places": {
        "user-home": "folder-home",
        "folder-downloads": "folder-download",
        "folder-videos": "folder-video",
        "folder-images": "folder-pictures",
        "network-workgroup": "folder-remote",
    },
    "devices": {
        "drive-removable-media-usb": "drive-removable-media",
    },
    "mimetypes": {
        "inode-directory": "places/folder",
    },
    "apps": {
        # Ajustes del sistema pide "preferences-system", que LinXP no tiene
        # con ese nombre. cs-general es su panel de control: un engranaje.
        "preferences-system": "apps/cs-general",
        # Dolphin pide su nombre propio, y LinXP no conoce Dolphin. Se le
        # pone la carpeta amarilla, que es lo que habria usado XP.
        "system-file-manager": "places/folder",
        "org.kde.dolphin": "places/folder",
        # Discover pide su nombre propio. system-software-installer es una
        # caja de software con un CD, que es justo lo que es.
        # El notificador de Discover NO colisiona: pide
        # system-software-update, con otro nombre.
        "plasmadiscover": "apps/system-software-installer",
    },
}

# OJO con lo que se anhade aqui: software-properties, de LinXP, es
# literalmente la bandera de Microsoft. No entra, ni como alias. La regla del
# proyecto es recrear el aspecto, nunca usar marcas.

# Nombres que NO se cogen aunque encajen en el criterio.
#
# La bandeja del sistema los usa como icono propio, y ahi un mapa de bits a
# todo color no vale: el panel es azul oscuro y espera glifos monocromos que
# Plasma retiñe. Se comprobo apartando el fichero y recargando plasmashell:
# con audio-x-generic puesto, el applet de volumen mostraba una pagina blanca
# con una nota musical en lugar del altavoz.
#
# El coste es que esos tipos de archivo se quedan con el icono de breeze en
# el gestor de archivos. Es mejor trato que un icono permanentemente roto en
# el panel, que se ve siempre.
DENY = {
    "mimetypes": {"audio-x-generic", "unknown"},
    "devices": set(),
    "places": set(),
    "apps": set(),
}

REFERENCE = "/usr/share/icons/breeze"


def reference_names(contexts):
    """Nombres que define el tema de referencia, en esos contextos.

    Breeze ordena contexto/tamano. Se lee Breeze porque es el tema de KDE: lo
    que el nombra es lo que el escritorio pide.
    """
    out = set()
    for context in contexts:
        base = pathlib.Path(REFERENCE) / context
        if base.is_dir():
            out |= {p.stem for p in base.glob("*/*")
                    if p.suffix in (".svg", ".png")}
    return out


def available(src, context):
    """Iconos que LinXP trae en ese contexto. Cada uno es un directorio."""
    base = src / context
    if not base.is_dir():
        return {}
    out = {}
    for d in base.iterdir():
        if not (d.is_dir() and d.name.endswith(".png")):
            continue
        # Solo dibujo propio. Un directorio sin PNG numerado es un alias que
        # su script rellena desde Mint-X, y eso no lo queremos: no es XP.
        sizes = {p.stem: p for p in d.glob("*.png") if p.stem.isdigit()}
        if sizes:
            out[d.name[:-4]] = sizes
    return out


def download():
    CACHE.mkdir(parents=True, exist_ok=True)
    tar = CACHE / "linxp.tar.gz"
    if not tar.exists():
        print(f"   bajando LinXP -> {tar.relative_to(ROOT)}")
        subprocess.run(["curl", "-sL", "--fail", "--max-time", "180",
                        "-o", str(tar), URL], check=True)
    else:
        print(f"   usando la copia de {tar.relative_to(ROOT)}")

    out = CACHE / "linxp"
    if not out.exists():
        # Se extrae en su propio directorio y no se ejecuta nada de dentro:
        # el repositorio trae scripts de compilacion que no nos hacen falta.
        with tarfile.open(tar) as t:
            members = [m for m in t.getmembers()
                       if not (m.name.startswith("/") or ".." in m.name)]
            t.extractall(out, members=members, filter="data")
    roots = list(out.glob("LinXP-*/icon-build"))
    if not roots:
        sys.exit("!! el archivo no tiene LinXP-*/icon-build dentro")
    return roots[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--list", action="store_true",
                    help="solo enumera lo que se cogeria")
    ap.add_argument("--keep-cache", action="store_true",
                    help="no borrar build/cache al terminar")
    args = ap.parse_args()

    if not pathlib.Path(REFERENCE).is_dir():
        sys.exit(f"!! falta {REFERENCE}, que es de donde sale la seleccion")

    src = download()
    taken = 0
    if DEST.exists():
        shutil.rmtree(DEST)

    for context, refs in CONTEXTS.items():
        have = available(src, context)
        wanted = reference_names(refs)

        # los que coinciden de nombre, mas los alias
        picks = {n: (have, n) for n in sorted(have)
                 if n in wanted and n not in DENY[context]}
        # Los alias NO exigen que Breeze nombre el destino. El filtro de
        # arriba existe para no instalar nombres que nadie pide; un alias
        # escrito a mano ya dice que ese nombre se pide. Hace falta para
        # org.kde.dolphin, que lo declara el propio Dolphin y Breeze no.
        for target, source in ALIASES[context].items():
            src_ctx, _, src_name = source.rpartition("/")
            pool = available(src, src_ctx) if src_ctx else have
            if src_name in pool and target not in DENY[context]:
                picks[target] = (pool, src_name)

        for target in sorted(picks):
            pool, source = picks[target]
            for size, path in sorted(pool[source].items(),
                                     key=lambda kv: int(kv[0])):
                d = DEST / f"{size}x{size}" / context
                d.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, d / f"{target}.png")
            taken += 1
        print(f"   {context:<10} {len(picks):>3} cogidos "
              f"de {len(have)} con dibujo propio")

    if args.list:
        shutil.rmtree(DEST)
        print("   (--list: no se ha escrito nada)")
        return 0

    files = sum(1 for _ in DEST.rglob("*.png"))
    print(f"   total      {taken} iconos, {files} archivos "
          f"-> {DEST.relative_to(ROOT)}")
    print("   no van al repositorio: LinXP no trae licencia")

    if not args.keep_cache:
        shutil.rmtree(CACHE, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
