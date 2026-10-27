# Bliss

Tema global para **KDE Plasma 6**: Windows XP *Luna* con un acabado de cristal
*Frutiger Aero*.

Pensado para Plasma 6.3 / Qt6 / KF6. Desarrollado y probado en Debian 13 sobre
Wayland.

## Empezar

    make check     # valida SVG, JSON y los IDs que KSvg necesita
    make install   # copia a ~/.local/share — no cambia nada visible todavia
    make apply     # activa colores + Plasma style + decoracion de ventana

Si cambias un SVG del Plasma style sin cambiar el nombre del tema, Plasma lo
sirve de cache. Para verlo:

    make reload

Para volver atras, en cualquier momento:

    make revert

`make apply` **no toca tu panel**. Para la disposicion completa tipo XP
(barra inferior, Inicio, lista de ventanas) usa `make apply-global`, que hace
un backup automatico antes porque rehace el panel.

## Que hay aqui

    src/color-schemes/Bliss.colors      Paleta Luna para todas las apps Qt
    src/aurorae/Bliss/                  Barra de titulo y botones
    src/plasma/desktoptheme/Bliss/      Shell de Plasma: barra, popups, filas
      widgets/panel-background.svg        fondo de la barra de tareas
      widgets/tasks.svg                   botones de ventana
      widgets/listitem.svg                filas con hover y seleccion
      dialogs/background.svg              fondo de popups y menu Inicio
      colors                              colores del SHELL (no de las apps)
    src/kvantum/Bliss/                  Interior de las aplicaciones (GENERADO)
    src/icons/Bliss/                    Iconos (hereda de Breeze)
    src/look-and-feel/org.bliss.desktop Meta-paquete que enlaza todo lo anterior

    docs/palette.md    los colores, de donde salen y como afinarlos
    docs/formats.md    referencia de formatos verificada en este sistema
    docs/roadmap.md    que falta, en orden de impacto

    tools/check-ids.py        valida los IDs de los SVG
    tools/test-nested.sh      KWin anidado con config aislada, para probar sin riesgo
    tools/recolor-kvantum.py  remapea la paleta de un tema Kvantum
    tools/make-kvconfig.py    genera el kvconfig con la paleta Luna

## El tema Kvantum es generado

`src/kvantum/Bliss/Bliss.svg` y `Bliss.kvconfig` **no se editan a mano**: salen
de `make kvantum`, que deriva ambos de KvBeige.

KvBeige se eligio como base porque su boton ya tiene la estructura de Luna:
borde crisp de 1 px, bisel vertical y estado pulsado invertido. Lo unico que
cambia es el pigmento. Cada color pasa a HSL y su luminosidad indexa una rampa
de material anclada en dos valores canonicos de XP, `#ACA899` (ButtonShadow) y
`#ECE9D8` (ButtonFace). Eso conserva el modelado y solo cambia el color.

Una segunda fase reasigna las superficies que no son del material: la fila
seleccionada es azul Luna y la barra de progreso verde. Sin ella quedarian
color crema, es decir invisibles.

Para cambiar la paleta, edita las rampas de `tools/recolor-kvantum.py` y
vuelve a ejecutar `make kvantum`. Ese mismo mecanismo es el que hara barato el
modo oscuro (ver `docs/roadmap.md`).

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

Instalados: `inkscape`, `qt6-style-kvantum` (con `kvantummanager` y
`kvantumpreview`).

Pendiente, util pero no bloqueante:

    sudo apt install plasma-sdk

Aporta `plasmoidviewer`, `lookandfeelexplorer` y `cuttlefish`.

## Dos archivos de color que no son el mismo

Esto se presta a confusion y cuesta una tarde:

    src/color-schemes/Bliss.colors          -> las aplicaciones Qt. CLARO.
    src/plasma/.../Bliss/colors             -> el shell de Plasma. OSCURO.

El contenido del panel se pinta con `[Colors:Window]` del **Plasma style**. Si
ahi pones el esquema claro, los iconos de la bandeja salen negros sobre la
barra azul. Y como Plasma no deja dar colores distintos al panel y a los
popups, todo el chrome comparte paleta oscura. Detalles en `docs/formats.md`.

## Estado

Fases 1 a 3 casi completas: la ventana (barra de titulo, nueve botones,
maximizado), el interior de las aplicaciones Qt y el escritorio (barra de
tareas, popups, filas de menu). Faltan el boton Inicio verde, el tooltip
amarillo y los iconos.

El modo oscuro esta disenado pero no construido: paleta en `docs/palette.md`,
plan en la fase 4 de `docs/roadmap.md`. Sale barato porque la geometria se
reutiliza entera.

El arte es un punto de partida calibrado a ojo, no un calco fiel.

## Licencia

GPL-3.0-or-later. El aspecto de Windows XP es una reinterpretacion en
vectores; este repositorio no contiene ningun archivo original de Microsoft.
Ver la nota de licencias al final de `docs/roadmap.md`.
