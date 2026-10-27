# Bliss

Tema global para **KDE Plasma 6**: Windows XP *Luna* con un acabado de cristal
*Frutiger Aero*.

Pensado para Plasma 6.3 / Qt6 / KF6. Desarrollado y probado en Debian 13 sobre
Wayland.

## Empezar

    make check     # valida SVG, JSON y los IDs que KSvg necesita
    make install   # copia a ~/.local/share — no cambia nada visible todavia
    make apply     # activa colores + Plasma style + decoracion de ventana

Para volver atras, en cualquier momento:

    make revert

`make apply` **no toca tu panel**. Para la disposicion completa tipo XP
(barra inferior, Inicio, lista de ventanas) usa `make apply-global`, que hace
un backup automatico antes porque rehace el panel.

## Que hay aqui

    src/color-schemes/Bliss.colors      Paleta Luna para todas las apps Qt
    src/aurorae/Bliss/                  Barra de titulo y botones
    src/plasma/desktoptheme/Bliss/      Barra de tareas y widgets del escritorio
    src/kvantum/Bliss/                  Interior de las aplicaciones (falta el SVG)
    src/icons/Bliss/                    Iconos (hereda de Breeze)
    src/look-and-feel/org.bliss.desktop Meta-paquete que enlaza todo lo anterior

    docs/palette.md    los colores, de donde salen y como afinarlos
    docs/formats.md    referencia de formatos verificada en este sistema
    docs/roadmap.md    que falta, en orden de impacto

    tools/check-ids.py     valida los IDs de los SVG
    tools/test-nested.sh   KWin anidado con config aislada para probar sin riesgo

## El concepto que cuesta mas

Un "tema global" de KDE es un **meta-paquete**. Casi no contiene arte: su
`contents/defaults` apunta a otros temas que van por separado y en formatos
distintos. Son ocho sub-proyectos, no uno.

Y el que mas confunde: **el Plasma style no estiliza tus aplicaciones.** Solo
pinta el escritorio — panel, menu Inicio, popups. Dolphin y Kate los pinta el
*widget style* (Breeze, Fusion o Kvantum), que es otro motor con otro formato.
Para el aspecto XP completo hacen falta los dos.

## Probar sin romper nada

    ./tools/test-nested.sh

Arranca un KWin dentro de una ventana, con su propia configuracion. Si el tema
esta roto, cierras la ventana y tu sesion ni se entera.

Si alguna vez te quedas sin panel ni escritorio: `Ctrl+Alt+F3` te da una
consola, y `make restore` devuelve la configuracion guardada.

## Dependencias

Ya presentes: `plasma-workspace`, `kwin-wayland`, `kconfig-bin`, `python3`.

Para seguir avanzando:

    sudo apt install inkscape plasma-sdk qt6-style-kvantum

- **inkscape** — editar los SVG. Imprescindible: hay que tocar IDs de objeto
  a mano constantemente.
- **plasma-sdk** — `plasmoidviewer`, `lookandfeelexplorer`, `cuttlefish`.
- **qt6-style-kvantum** — el estilo de widgets de aplicacion.

## Estado

Fase 0 completada: el esqueleto se instala, Plasma lo reconoce y se puede
aplicar. El arte es un punto de partida calibrado a ojo, no un calco fiel.
Ver `docs/roadmap.md`.

## Licencia

GPL-3.0-or-later. El aspecto de Windows XP es una reinterpretacion en
vectores; este repositorio no contiene ningun archivo original de Microsoft.
Ver la nota de licencias al final de `docs/roadmap.md`.
