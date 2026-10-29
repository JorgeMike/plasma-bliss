# Bliss

Tema global para **KDE Plasma 6**: Windows XP *Luna* con un acabado de cristal
*Frutiger Aero*.

Pensado para Plasma 6.3 / Qt6 / KF6. Desarrollado y probado en Debian 13 sobre
Wayland.

No es un calco: los archivos originales de Luna son de Microsoft y no se
redistribuyen. Todo lo que hay aqui esta **recreado en vectores**, calibrado
contra los valores canonicos de XP que estan anotados en `docs/palette.md`.

## Como se ve

### La barra de tareas

![Barra de tareas](docs/screenshots/panel.png)

Degradado azul de Luna, boton Inicio verde, y los botones de ventana con su
bisel. El panel esta en modo flotante: cuando no hay ninguna ventana abierta
se despega del borde y entonces se ven sus cuatro esquinas redondeadas.

### Ventanas y controles

La decoracion de ventana es Aurorae; el interior de las aplicaciones Qt lo
pinta Kvantum. Las dos variantes comparten geometria exacta — mismo radio de
esquina, mismo bisel, mismo grosor de borde — y solo cambian de pigmento.

| Claro | Oscuro |
|---|---|
| ![Claro](docs/screenshots/widgets-light.png) | ![Oscuro](docs/screenshots/widgets-dark.png) |

### Fondo de pantalla

| Claro | Oscuro |
|---|---|
| ![Fondo claro](docs/screenshots/wallpaper-light.jpg) | ![Fondo oscuro](docs/screenshots/wallpaper-dark.jpg) |

Dibujo propio en SVG, no la fotografia de Microsoft. Se publica como paquete
de vectores, asi que pesa 470 KB en lugar de decenas de megas y sale nitido a
cualquier densidad. La variante oscura se genera de la clara con un mapa de
color explicito, y las estrellas solo existen ahi.

### Iconos

![Iconos](docs/screenshots/icons.png)

Fondo verde: lo sirve Bliss. Fondo azul: cae por herencia a breeze-dark. No
se dibuja ni se forkea nada — `make icons` espiga de LinXP los iconos que el
escritorio pide de verdad y el resto se hereda.

### Terminal

![Terminal](docs/screenshots/terminal.png)

Konsole en negro con el pale de dieciseis colores que cmd.exe arrastro desde
DOS, y el prompt de starship reescrito en colores ANSI para que siga al
terminal en lugar de ignorarlo. *(Esta imagen esta compuesta a partir del
pale y de la salida real del prompt, no es una captura de pantalla.)*

## Empezar

    make check     # valida SVG, JSON y los IDs que KSvg necesita
    make install   # copia a ~/.local/share — no cambia nada visible todavia
    make apply     # activa colores + Plasma style + decoracion de ventana

El boton Inicio verde va aparte, porque Kickoff guarda su icono en la
configuracion de tu panel y no en el tema:

    make start-button          # y make start-button-revert para deshacerlo

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
    src/color-schemes/Bliss-Dark.colors Variante oscura (GENERADA a mano, ver palette.md)
    src/aurorae/Bliss/                  Barra de titulo y botones
    src/plasma/desktoptheme/Bliss/      Shell de Plasma: barra, popups, filas
      widgets/panel-background.svg        fondo de la barra de tareas
      widgets/tasks.svg                   botones de ventana
      widgets/listitem.svg                filas con hover y seleccion
      widgets/tooltip.svg                 tooltip oscuro (ver formats.md)
      dialogs/background.svg              fondo de popups y menu Inicio
      colors                              colores del SHELL (no de las apps)
    src/kvantum/Bliss/                  Interior de las aplicaciones (GENERADO)
    src/icons/Bliss/                    index.theme; los mapas de bits los
                                        trae `make icons` a build/
    src/wallpapers/Bliss/               Fondo en SVG (contents/ es GENERADO)
    src/konsole/Bliss.colorscheme       Consola negra con el pale de DOS
    src/starship/bliss.toml             Prompt en colores ANSI
    src/btop/btop.conf                  Claves que llevan btop a 16 colores
    src/look-and-feel/org.bliss.desktop Meta-paquete que enlaza todo lo anterior

    docs/palette.md    los colores, de donde salen y como afinarlos
    docs/formats.md    referencia de formatos verificada en este sistema
    docs/roadmap.md    que falta, en orden de impacto

    tools/check-ids.py        valida los IDs de los SVG
    tools/test-nested.sh      KWin anidado con config aislada, para probar sin riesgo
    tools/recolor-kvantum.py  remapea la paleta de un tema Kvantum
    tools/make-kvconfig.py    genera el kvconfig con la paleta Luna
    tools/set-start-button.py pone el icono Inicio en el panel del usuario
    tools/make-dark-aurorae.py   genera la decoracion oscura desde la clara
    tools/make-dark-wallpaper.py genera el fondo oscuro con un mapa de color
    tools/build-wallpaper.py     recorta el fondo por proporcion de pantalla
    tools/fetch-icons.py         espiga iconos XP de LinXP a build/
    tools/set-terminal.py        Konsole, starship, fzf y btop (reversible)

## La variante oscura se genera, no se duplica

Bliss Dark no es un segundo tema escrito a mano: es el claro pasado por una
transformacion. La geometria — el 9-slice, los ids, los margenes, el `rc` de
Aurorae — es **identica**, y `make check` lo verifica comparando los ids de
las dos decoraciones. Si divergen, el generador ha roto algo.

    make dark          # regenera Aurorae oscuro + Kvantum oscuro
    make apply-dark    # lo activa

- **Aurorae**: `tools/make-dark-aurorae.py` escala la luminosidad de cada
  color conservando tono y saturacion. Factor 0.58 en la decoracion, para que
  la barra de titulo se hunda y no deslumbre, y 0.82 en los botones, que son
  lo interactivo y deben seguir leyendose. El blanco puro queda intacto:
  define la mascara de opacidad, el brillo de cristal y los glifos.
- **Kvantum**: el mismo recolorizador con `--dark`, partiendo de la MISMA
  base que la variante clara. Ahi no se conserva ningun color por saturado y
  la fase 2 devuelve el azul de seleccion. La rampa de pizarra no invierte la
  luminosidad, la comprime: invertirla pondria la luz debajo y los biseles se
  verian hundidos. `make check` comprueba que las dos variantes comparten la
  caja de los 433 elementos con nombre, es decir, la misma forma.
- **Iconos**: no cambian entre claro y oscuro. `Bliss` solo sobrescribe
  carpetas, dispositivos y tipos de archivo, y hereda el resto de
  breeze-dark. Los mapas de bits los trae `make icons` desde LinXP a
  `build/`, fuera del repositorio, porque LinXP no publica licencia.
- **Terminal**: `make terminal`. Konsole en negro con el palé de DOS, y el
  prompt de starship reescrito en colores ANSI — el preset que traias usaba
  hex fijos y habria seguido siendo una cinta azul sobre el negro. Toca
  configuracion tuya, guarda copia y se deshace con `make terminal-revert`.
- **Plasma style**: no cambia. El chrome del shell ya es azul oscuro en ambas
  variantes, igual que la barra de tareas de Windows 7 o 10 se mantiene
  oscura con independencia del modo de las aplicaciones.

El contraste de la paleta oscura esta comprobado: todos los pares criticos
pasan AA, el peor es 5.3:1 (texto blanco sobre seleccion).

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

Completo y en uso: la ventana (barra de titulo, nueve botones, maximizado),
el interior de las aplicaciones Qt, el escritorio (barra de tareas, popups,
filas de menu), la variante oscura entera, el fondo de pantalla, los iconos
y la terminal.

Lo que queda esta en `docs/roadmap.md`. Lo principal: las aplicaciones GTK,
que ignoran Kvantum y necesitarian un tema aparte, y el cambio automatico
dia/noche, que Plasma no trae.

El arte es un punto de partida calibrado a ojo, no un calco fiel.

## Licencia

GPL-3.0-or-later. El aspecto de Windows XP es una reinterpretacion en
vectores; este repositorio no contiene ningun archivo original de Microsoft.
Ver la nota de licencias al final de `docs/roadmap.md`.
