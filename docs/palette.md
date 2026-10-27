# Paleta de Bliss

Dos familias que se mezclan: la base es **Luna Blue** de Windows XP; el acento
es **Frutiger Aero** (aqua, verde hoja, cristal).

## Luna — valores canonicos

Estos salen del registro de XP, no son aproximaciones:

| Rol | Hex | RGB | Donde se usa |
|---|---|---|---|
| ButtonFace / fondo de ventana | `#ECE9D8` | 236,233,216 | el beige de todo XP |
| Window / campos | `#FFFFFF` | 255,255,255 | listas, editores |
| Highlight (seleccion) | `#316AC5` | 49,106,197 | filas seleccionadas |
| ActiveTitle | `#0054E3` | 0,84,227 | inicio del degradado del titulo |
| GradientActiveTitle | `#3D95FF` | 61,149,255 | final del degradado |
| InactiveTitle | `#7A96DF` | 122,150,223 | titulo sin foco |
| GradientInactiveTitle | `#A6CAF0` | 166,202,240 | |
| InfoWindow (tooltip) | `#FFFFE1` | 255,255,225 | el amarillo palido |
| ButtonShadow | `#ACA899` | 172,168,153 | biseles, texto deshabilitado |

## Aero — acentos

| Rol | Hex | RGB |
|---|---|---|
| Aqua (hover, brillo) | `#4FC3F7` | 79,195,247 |
| Verde hoja (positivo) | `#5CB82E` | 92,184,46 |
| Ambar (neutro) | `#F0A30A` | 240,163,10 |
| Rojo (negativo) | `#D43A2F` | 212,58,47 |
| Oceano (complementario) | `#0A3E8C` | 10,62,140 |

## Degradados compuestos

No son colores planos, son los degradados que llevan el peso visual. Estan
definidos en los `<defs>` de cada SVG, no en el esquema de color.

**Barra de titulo** (`g-title`, vertical, en `aurorae/Bliss/decoration.svg`):

    0%   #2B7FEF      52%  #0A52C6
    6%   #4C9DFB      86%  #0B57CC
    14%  #1668DE      93%  #2E80E9   <- el "rebote" claro de Luna
                      100% #0E4FBB

**Barra de tareas** (`g-taskbar`, en `plasma/.../panel-background.svg`):

    0%   #3C81F3      88%  #215CD4
    10%  #2C6BE0     100%  #3A7FEE
    45%  #1F57CE

**Cristal Aero** (`g-gloss`): blanco de 55% a 0% de opacidad sobre la mitad
superior de cada superficie. Es la unica pieza que no es XP, y es lo que hace
que el tema no parezca un calco.

## Como afinar esto de verdad

Los degradados de arriba estan calibrados a ojo. Si quieres exactitud:

1. Consigue una captura de XP a 1:1, sin escalar ni recomprimir (un PNG).
2. Abrela en GIMP, amplia al 800% sobre la barra de titulo.
3. Usa el cuentagotas columna a columna, de arriba a abajo, y anota los stops.
4. Sustituye los `<stop>` en el SVG.

Una barra de titulo de Luna son ~30 filas de pixeles; muestrear 7 u 8 basta.

---

# Bliss Dark (planificado)

Windows XP no tuvo modo oscuro, asi que esto no puede ser "Luna pero oscuro":
no hay original al que ser fiel. La salida es apoyarse en la otra mitad del
concepto — Frutiger Aero — y leerlo como **cristal de oceano profundo**:
azules saturados, acentos aqua, el mismo brillo glossy. La geometria no cambia;
solo cambia el pigmento.

## Paleta

| Rol | Hex | Nota |
|---|---|---|
| Fondo de ventana / face | `#2E343B` | gris azulado, no negro |
| Base (listas, editores) | `#22272D` | |
| Fila alterna | `#272D34` | |
| Texto | `#E8EDF2` | 10:1 sobre el fondo |
| Texto deshabilitado | `#7A848E` | |
| Borde / sombra | `#171B20` | |
| Arista clara (bisel) | `#454D56` | sustituye al blanco del bisel claro |
| Seleccion | `#2F6ABF` | azul Luna oscurecido; 5.4:1 con texto blanco |
| Texto seleccionado | `#FFFFFF` | |
| Tooltip | `#3A4149` / texto `#E8EDF2` | el amarillo de XP no funciona en oscuro |
| Aqua (hover) | `#4FC3F7` | |
| Verde hoja | `#7CC95A` | |
| Ambar | `#F0A30A` | |
| Rojo | `#E05A4F` | |

El azul de seleccion esta oscurecido a proposito: `#316AC5`, el de Luna, solo
da 4.4:1 con texto blanco y se queda por debajo de AA para texto pequeno.

## Degradados

**Barra de titulo** — misma forma, tonos hundidos:

    0%   #2A62C4      52%  #0E2E63
    6%   #3B7CE0      86%  #10336E
    14%  #15417F      93%  #2A62C4
                      100% #0B2655

**Barra de tareas:** `#1E3F6B` -> `#16283F` -> `#244A7A`

El brillo (`g-gloss`) no cambia: blanco al 55% que cae a cero. Sobre azul
oscuro produce exactamente el cristal de Aero.
