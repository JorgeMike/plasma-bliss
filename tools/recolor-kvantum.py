#!/usr/bin/env python3
"""Reescribe la paleta de un tema Kvantum sin tocar su geometria.

    python3 tools/recolor-kvantum.py <origen.svg> <destino.svg>

Dos fases.

FASE 1 — material. Cada color pasa a HSL y su LUMINOSIDAD indexa una rampa.
Eso conserva el modelado (bisel, degradado, sombra) y solo cambia el pigmento,
que es lo que se quiere al partir de un tema cuya estructura ya es correcta.
La rampa de Bliss esta anclada en dos valores canonicos de Windows XP:
    luminosidad 0.63 -> #ACA899 (ButtonShadow)
    luminosidad 0.84 -> #ECE9D8 (ButtonFace)

FASE 2 — acentos. Algunas superficies NO son del material: la fila
seleccionada es azul Luna y la barra de progreso es verde. La fase 1 las
dejaria color crema, invisibles. Esta fase las reasigna por ID de elemento,
siguiendo la cadena de degradados y clonando los que esten compartidos con
elementos que no son objetivo, para no danarlos.

Para el modo oscuro: cambia RAMP y parte de un tema oscuro (KvCurves3d).
"""
import colorsys
import re
import sys

# --------------------------------------------------------------- fase 1
RAMP = [
    (0.00, "2b2821"), (0.27, "6b6758"), (0.35, "8a8574"), (0.50, "9e9a88"),
    (0.63, "aca899"), (0.71, "d8d4c2"), (0.76, "e4e0ce"), (0.84, "ece9d8"),
    (0.90, "f4f1e4"), (0.98, "fdfcf6"), (1.00, "ffffff"),
]
ACCENT = {"0067ce": "0054e3", "ce0400": "d43a2f"}
KEEP = {"b74aff"}          # marcadores con los que Kvantum mide las sombras
SAT_KEEP = 0.45

# --------------------------------------------------------------- fase 2
# Rampas de acento: luminosidad de origen -> color. Mismo principio que arriba,
# asi el degradado original sobrevive al cambio de tono.
BLUE = [(0.00, "123a7d"), (0.40, "2a5fb8"), (0.62, "316ac5"),
        (0.80, "5b8ddb"), (1.00, "a9c6ef")]
GREEN = [(0.00, "1d6b12"), (0.35, "2e9b18"), (0.60, "3cae1f"),
         (0.80, "5cc733"), (1.00, "8fe05c")]

ACCENT_ELEMENTS = [
    (re.compile(r"^itemview-(toggled|pressed)(-|$)"), BLUE),
    (re.compile(r"^(expand-)?progress-(normal|pattern-normal)(-|$)"), GREEN),
]


def rgb(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def hx(t):
    return "".join(f"{round(max(0, min(1, c)) * 255):02x}" for c in t)


def through(ramp, lightness):
    for (la, ca), (lb, cb) in zip(ramp, ramp[1:]):
        if la <= lightness <= lb:
            t = 0 if lb == la else (lightness - la) / (lb - la)
            a, b = rgb(ca), rgb(cb)
            return hx(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))
    return ramp[-1][1]


def material(h):
    h = h.lower()
    if h in KEEP:
        return h
    if h in ACCENT:
        return ACCENT[h]
    _, lightness, saturation = colorsys.rgb_to_hls(*rgb(h))
    return h if saturation > SAT_KEEP else through(RAMP, lightness)


def phase1(svg):
    return re.sub(r"#([0-9a-fA-F]{6})\b", lambda m: "#" + material(m.group(1)), svg)


# ---------------------------------------------------------------- utilidades
TAG = r'<[^<>]*\bid="{}"[^<>]*>'


def tag_of(svg, eid):
    m = re.search(TAG.format(re.escape(eid)), svg)
    return m


def grad_of(tag_text):
    m = re.search(r"url\(#([^)]+)\)", tag_text)
    return m.group(1) if m else None


def grad_body(svg, gid):
    return re.search(rf'id="{re.escape(gid)}"(.*?)</(?:linear|radial)Gradient>', svg, re.S)


def resolve_chain(svg, gid, seen=None):
    """Devuelve la lista de gradientes de la cadena href, del hijo a la raiz."""
    seen = seen or []
    if gid in seen:
        return seen
    seen = seen + [gid]
    b = grad_body(svg, gid)
    if not b:
        return seen
    href = re.search(r'href="#([^"]+)"', b.group(1))
    return resolve_chain(svg, href.group(1), seen) if href else seen


def grad_element(svg, gid):
    """Texto completo del <linearGradient>/<radialGradient> con ese id."""
    m = re.search(rf'<(?:linear|radial)Gradient[^<>]*\bid="{re.escape(gid)}"[^<>]*/>', svg)
    if m:
        return m.group(0)
    m = re.search(
        rf'<(?:linear|radial)Gradient[^<>]*\bid="{re.escape(gid)}"[^<>]*>.*?</(?:linear|radial)Gradient>',
        svg, re.S)
    return m.group(0) if m else None


def element_span(svg, eid):
    """(inicio, fin) del elemento COMPLETO, con sus hijos.

    Hace falta porque muchas piezas del 9-slice son <g> contenedores: el color
    no esta en la etiqueta sino en los hijos. Teñir solo la etiqueta dejaba el
    marco de la fila seleccionada color crema alrededor de un interior azul.
    """
    m = re.search(rf'<(\w+)[^<>]*\bid="{re.escape(eid)}"[^<>]*>', svg)
    if not m:
        return None
    if m.group(0).rstrip().endswith("/>"):
        return m.start(), m.end()
    name, depth, pos = m.group(1), 1, m.end()
    for t in re.finditer(rf'<(/?){name}\b[^<>]*>', svg[pos:]):
        if t.group(0).rstrip().endswith("/>"):
            continue
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return m.start(), pos + t.end()
    return None


def _retint(text, ramp):
    for c in sorted(set(re.findall(r"#([0-9a-fA-F]{6})\b", text))):
        if c.lower() in KEEP:
            continue
        _, L, _ = colorsys.rgb_to_hls(*rgb(c))
        text = re.sub(rf"#{c}\b", "#" + through(ramp, L), text)
    return text


def phase2(svg):
    """Reasigna las superficies que no son del material: seleccion y progreso.

    Sin aritmetica de desplazamientos: se acumulan sustituciones de texto y se
    aplican al final. Insertar los clones antes de </defs> invalida cualquier
    indice calculado previamente.
    """
    targets = {}
    for eid in re.findall(r'id="([a-zA-Z][\w-]*)"', svg):
        for pat, ramp in ACCENT_ELEMENTS:
            if pat.match(eid):
                targets[eid] = ramp
                break
    if not targets:
        return svg, 0, []

    spans = {}
    for eid in targets:
        sp = element_span(svg, eid)
        if sp:
            spans[eid] = sp
    # descartar objetivos contenidos dentro de otro objetivo: se tratan al teñir el padre
    nested = {a for a in spans for b in spans
              if a != b and spans[b][0] <= spans[a][0] and spans[a][1] <= spans[b][1]}

    edits, clones, problems = [], [], []
    counter = 0
    for eid in sorted(spans):
        if eid in nested:
            continue
        ramp = targets[eid]
        a, b = spans[eid]
        body = svg[a:b]
        new_body = _retint(body, ramp)

        for gid in sorted(set(re.findall(r"url\(#([^)]+)\)", body))):
            chain = resolve_chain(svg, gid)
            counter += 1
            rename = {g: f"blissAccent{counter}_{i}" for i, g in enumerate(chain)}
            made = []
            for g in chain:
                gel = grad_element(svg, g)
                if gel is None:
                    problems.append(f"{eid}: gradiente {g} ilegible")
                    continue
                gel = re.sub(rf'\bid="{re.escape(g)}"', f'id="{rename[g]}"', gel, count=1)
                for o, n in rename.items():
                    gel = gel.replace(f'href="#{o}"', f'href="#{n}"')
                made.append(_retint(gel, ramp))
            if made:
                clones += made
                new_body = new_body.replace(f"url(#{gid})", f"url(#{rename[gid]})")

        if new_body != body:
            edits.append((body, new_body))

    for old_t, new_t in edits:
        svg = svg.replace(old_t, new_t, 1)
    if clones:
        svg = svg.replace("</defs>", "\n".join(clones) + "\n</defs>", 1)
    return svg, len(edits), problems


def main(src, dst):
    svg = open(src).read()
    n_colors = len(set(re.findall(r"#[0-9a-fA-F]{6}", svg)))
    n_ids_before = len(set(re.findall(r'id="([^"]+)"', svg)))
    svg = phase1(svg)
    svg, n_accent, problems = phase2(svg)
    open(dst, "w").write(svg)
    print(f"{dst}")
    print(f"  fase 1: {n_colors} colores distintos pasados por la rampa de material")
    print(f"  fase 2: {n_accent} elementos de acento reasignados")
    for p in problems:
        print(f"    AVISO {p}")
    # guardas: el XML debe seguir siendo valido y no puede perderse ningun id
    import xml.etree.ElementTree as ET
    ET.parse(dst)
    n_after = len(set(re.findall(r'id="([^"]+)"', open(dst).read())))
    assert n_after >= n_ids_before, f"se perdieron ids: {n_ids_before} -> {n_after}"
    print(f"  guardas: XML valido, {n_after} ids (antes {n_ids_before})")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
