# Referencia de formatos (verificada en este sistema)

Plasma 6.3.6 · KF6 · Debian 13. Todo lo de aqui esta leido de los binarios y
del QML instalados, no de documentacion de internet que puede ir por detras.

## Donde vive cada cosa

| Componente | Destino | Tipo de kpackagetool6 |
|---|---|---|
| Esquema de color | `~/.local/share/color-schemes/X.colors` | — (archivo suelto) |
| Decoracion | `~/.local/share/aurorae/themes/X/` | `KWin/Aurorae` |
| Plasma style | `~/.local/share/plasma/desktoptheme/X/` | `Plasma/Theme` |
| Tema global | `~/.local/share/plasma/look-and-feel/ID/` | `Plasma/LookAndFeel` |
| Iconos | `~/.local/share/icons/X/` | — |
| Kvantum | `~/.config/Kvantum/X/` | — |

## Aurorae

Ground truth: `/usr/share/kwin/aurorae/aurorae.qml` y `AuroraeButton.qml`.

**`decoration.svg`** — prefijos de `KSvg::FrameSvg`:

| Prefijo | Obligatorio | Para que |
|---|---|---|
| `decoration` | si | ventana activa |
| `decoration-inactive` | no | ventana sin foco |
| `decoration-maximized` | no | maximizada (borde superior solo) |
| `decoration-maximized-inactive` | no | |
| `innerborder`, `innerborder-inactive` | no | linea interior |
| `mask` | no | region opaca; sin el, esquinas cuadradas |

Cada prefijo necesita las nueve partes:
`-topleft -top -topright -left -center -right -bottomleft -bottom -bottomright`

**Botones** (`close.svg`, `minimize.svg`, `maximize.svg`, `restore.svg`,
`alldesktops.svg`, `keepabove.svg`, `keepbelow.svg`, `shade.svg`, `help.svg`):

| Prefijo | Obligatorio |
|---|---|
| `active` | si |
| `hover`, `pressed`, `inactive`, `deactivated` | no (cae a `active`) |
| `hover-inactive`, `pressed-inactive`, `deactivated-inactive` | no |

**`<Nombre>rc`** — dos grupos, `[General]` y `[Layout]`. Lista exacta de claves
que el binario `org.kde.kwin.aurorae.so` contiene como cadena, es decir, las
unicas que puede leer:

    [General]  ActiveTextColor InactiveTextColor UseTextShadow
               ActiveTextShadowColor InactiveTextShadowColor
               TextShadowOffsetX TextShadowOffsetY
               TitleAlignment TitleVerticalAlignment Animation
               LeftButtons RightButtons

    [Layout]   BorderTop BorderBottom BorderSize
               TitleHeight TitleEdgeTop TitleEdgeBottom
               TitleEdgeLeft TitleEdgeRight
               TitleEdgeTopMaximized TitleEdgeBottomMaximized
               TitleEdgeLeftMaximized TitleEdgeRightMaximized
               TitleBorderLeft TitleBorderRight
               ButtonWidth ButtonHeight ButtonSpacing ButtonMarginTop
               ButtonWidthClose ButtonWidthMinimize ButtonWidthMaximizeRestore
               ButtonWidthMenu ButtonWidthHelp ButtonWidthShade
               ButtonWidthKeepabove ButtonWidthKeepbelow
               ButtonWidthAlldesktops ButtonWidthAppMenu
               ExplicitButtonSpacer ButtonMarginTopMaximized
               PaddingTop PaddingBottom PaddingLeft PaddingRight

**Claves que NO existen en el binario de 6.3**, aunque medio internet y muchos
temas de la KDE Store las usen:

    BorderLeft  BorderRight  BorderLeftMaximized  BorderRightMaximized
    BorderBottomMaximized  BorderTopMaximized
    LeftButtons  RightButtons  Shadow

Consecuencias practicas:

- El **ancho de los bordes laterales** no lo decide el tema. Sale de
  Preferencias del sistema > Decoracion de ventanas > Tamano del borde.
- El **orden de los botones** tampoco. Sale del mismo sitio.
- Comprobar esto es una linea:
  `strings /usr/lib/x86_64-linux-gnu/qt6/plugins/org.kde.kdecoration3/org.kde.kwin.aurorae.so | grep -x BorderLeft`

**El boton de menu no necesita `menu.svg`.** `MenuButton.qml` dibuja el icono
de la aplicacion con `Kirigami.Icon`, no un SVG del tema. Lo mismo
`AppMenuButton.qml`. Los demas botones si necesitan su archivo: sin el,
`visible: buttonSvg.imagePath != ""` los oculta.

### La trampa de la ventana maximizada

Si el tema no define el prefijo `decoration-maximized`, `aurorae.qml` hace esto:

    decorationActive.shown:  (!maximized || !supportsMaximized) && ...
    decorationActive.enabledBorders:  maximized ? NoBorder : Top|Bottom|Left|Right

Es decir, sigue dibujando el marco normal pero con `NoBorder`, y `FrameSvg` con
`NoBorder` dibuja **solo el elemento `-center`** estirado. Si tu
`decoration-center` es transparente — que es lo normal, porque ahi va el
contenido de la ventana — la barra de titulo de una ventana maximizada
desaparece y queda el texto flotando.

Por eso Bliss define `decoration-maximized` y `decoration-maximized-inactive`,
con el degradado completo en el `-center`.

El borde superior real es `TitleHeight + TitleEdgeTop + TitleEdgeBottom`.
En Bliss: 22 + 4 + 4 = **30 px**, la altura de la barra de Luna a 96 dpi.
`Padding*` es espacio para la sombra dibujada por el tema (Bliss usa 0: en
Wayland la sombra la pone KWin).

**Letras de botones** en `LeftButtons`/`RightButtons`:
`M` menu · `S` pegajosa (todos los escritorios) · `H` ayuda · `I` minimizar ·
`A` maximizar · `X` cerrar · `F` mantener encima · `B` mantener debajo ·
`L` enrollar · `_` espaciador

## Plasma style

Igual, pero **sin prefijo**: los IDs son `topleft`, `top`, `center`, …
Extras opcionales:

- `hint-tile-center` — repite el centro en vez de estirarlo
- `hint-{top,bottom,left,right}-margin` — margenes de contenido; cuenta el
  TAMANO del rect, no su posicion
- `hint-{top,bottom,left,right}-inset`
- `hint-stretch-borders`, `hint-no-border-padding`
- `current-color-scheme` — bloque `<style>` que Plasma reescribe en caliente
  para seguir los colores del usuario. **Bliss no lo usa** a proposito: el azul
  de Luna es fijo, no debe seguir al esquema.

Acepta `.svg` y `.svgz` (gzip). Usa `.svg` mientras desarrollas.

### El archivo `colors` del Plasma style no es el esquema de las aplicaciones

Son dos cosas distintas y confundirlas tiene un sintoma muy concreto:

| Archivo | Tiñe |
|---|---|
| `~/.local/share/color-schemes/X.colors` | las aplicaciones Qt |
| `<desktoptheme>/X/colors` | el shell de Plasma: panel, popups, widgets |

El contenido del panel — texto del reloj, iconos monocromos de la bandeja — se
pinta con **`[Colors:Window] ForegroundNormal` del Plasma style**. Copiar ahi
el esquema claro de las aplicaciones deja los iconos negros sobre la barra
azul. Se puede verificar en el tema del sistema: `breeze-light/colors` tiene
Window en 35,38,41 (oscuro, panel claro) y `breeze-dark/colors` en 252,252,252.

**Plasma no permite dar un grupo de color distinto al panel y a los popups.**
Se comprobo: el unico sitio que usa `Complementary` es la pantalla de bloqueo
(`LockScreenUi.qml`), y ni el contenedor del panel ni Kickoff fijan
`Kirigami.Theme.colorSet`. El reloj usa `Kirigami.Theme.textColor` con el
grupo por defecto, y su calendario emergente fija explicitamente `Window`, el
mismo del panel. O todo el chrome es claro, o todo oscuro.

### Prefijos de `widgets/tasks.svg`

`normal`, `hover`, `focus` (ventana activa), `minimized`, `attention`,
`launcher-hover`. **No hacen falta las variantes `north-`/`east-`/`west-`**:
`taskPrefix()` de
`plasmoids/org.kde.plasma.taskmanager/contents/ui/code/tools.js` devuelve
`["south-<p>", "<p>"]` y `FrameSvgItem` usa el primero que exista, asi que el
prefijo sin direccion sirve para los cuatro bordes.

El prefijo **vacio** es el fondo de los lanzadores en reposo. Omitirlo los
deja sin marco, que es justo el aspecto del inicio rapido de XP.

Para inspeccionar el tema del sistema:

    zcat /usr/share/plasma/desktoptheme/default/widgets/button.svgz

## Tema global (look-and-feel)

`contents/defaults` enlaza todos los componentes. **Trampa verificada:** el
grupo sigue llamandose `org.kde.kdecoration2` aunque Plasma 6 use
KDecoration**3** por dentro. Si lo "corriges" a `kdecoration3`, deja de
funcionar. Comprobado contra el `defaults` de Breeze del sistema.

El nombre del tema Aurorae va prefijado:

    theme=__aurorae__svg__Bliss

`contents/layouts/org.kde.plasma.desktop-layout.js` solo se ejecuta con
`plasma-apply-lookandfeel -a` y **rehace el panel del usuario**.

## El boton Inicio no se define en el tema

Kickoff acepta `icon` y `menuLabel`, pero viven en la configuracion del PANEL
del usuario (`plasma-org.kde.plasma.desktop-appletsrc`), no en el tema global.
El numero del applet cambia en cada equipo, asi que hay que buscarlo:
`tools/set-start-button.py` lo localiza por `plugin=org.kde.plasma.kickoff` y
escribe con `kwriteconfig6`. `make start-button` lo aplica y
`make start-button-revert` lo deshace.

**El icono se instala en `hicolor`, no solo en el tema Bliss.** El tema de
iconos activo del usuario no tiene por que ser el del tema global — en este
equipo es Papirus-Dark — y un icono que solo exista en `icons/Bliss/` no
resolveria. `hicolor` es el respaldo universal: toda cadena de herencia acaba
ahi. Se puede comprobar leyendo los `Inherits` de cada `index.theme`:

    Papirus-Dark -> breeze-dark -> hicolor -> breeze

Por eso `make install` copia `bliss-start.svg` a las dos rutas.

## Hay DOS rutas de tooltip, y usan grupos de color distintos

| Componente | SVG que pide | colorSet |
|---|---|---|
| `PlasmaComponents.ToolTip` | **`solid/widgets/tooltip`** | `Tooltip` |
| `PlasmaCore.ToolTipArea` → `DefaultToolTip.qml` | `dialogs/background` | `Window`, con `inherit: false` |

Dos trampas:

1. **El prefijo `solid/`.** `ToolTip.qml` pide literalmente
   `"solid/widgets/tooltip"`. Un tema que solo tenga `widgets/tooltip.svg`
   no cubre esa ruta. El tema del sistema tiene un directorio `solid/` con
   `background`, `panel-background` y `tooltip` justo por esto.
2. **`DefaultToolTip.qml` fuerza `colorSet: Window` con `inherit: false`**, asi
   que `[Colors:Tooltip]` no se aplica en esa ruta. Con el chrome oscuro eso
   significa texto BLANCO. Un fondo amarillo claro de XP lo deja invisible, y
   el sintoma es exactamente "un recuadro blanco y nada dentro".

Por eso en Bliss el tooltip va oscuro con texto blanco: es lo unico legible
con los dos grupos a la vez. El amarillo de XP exigiria chrome claro, que es
lo contrario de lo que necesita el panel.

El SVG de Breeze usa las clases `ColorScheme-Background` y `ColorScheme-Text`,
asi que Plasma lo recolorea en caliente con el grupo activo. Bliss hardcodea
los colores a proposito y no incluye `current-color-scheme`.

## Fondo de pantalla

Un fondo "de tema" no es un archivo suelto: es un paquete KPackage del tipo
`Wallpaper/Images`, que vive en `~/.local/share/wallpapers/<Id>/`.

```
Bliss/
  metadata.json              KPlugin.Id + KPackageStructure
  contents/
    screenshot.png           miniatura del selector
    images/1920x1080.svg     variante clara
    images_dark/1920x1080.svg  variante oscura
```

Plasma lee el nombre del archivo como resolucion y se queda con el mas
cercano al tamano de la pantalla. No hay que cubrir todas: con una por
proporcion util basta.

### Acepta SVG, no solo PNG

Comprobado en `libplasma_wallpaper_imageplugin.so`: enlaza con `KSvg::Svg`
(`_ZN4KSvg3Svg12setImagePathERK7QString`) y lleva las cadenas `:svgz` e
`image/svg`. Un paquete de SVG pesa kilobytes en vez de decenas de megas y se
rasteriza nitido a cualquier densidad.

El precio es que lo pinta **QSvgRenderer**, no librsvg ni Inkscape. Eso es
SVG Tiny 1.2 con anadidos, asi que en el dibujo no puede haber filtros
(`feGaussianBlur`), ni mascaras, ni `clip-path`, ni CSS, ni variables. Lo que
si hay, verificado con `strings` sobre `libQt6Svg.so.6`: `use`, `ellipse`,
`gradientUnits`, `stop-opacity`, `preserveAspectRatio`. Por eso las nubes de
`bliss.svg` son gradientes radiales y no desenfoques.

Un SVG se estira a lo que le pidan, asi que publicar uno solo deformaria el
dibujo en pantallas de otra proporcion. Por eso cada resolucion lleva su
propio recorte: el mismo archivo con otro `viewBox`.

### Quien elige entre `images` e `images_dark`

El plugin, por la **paleta de las aplicaciones** (`slotSystemPaletteChanged`,
senal `colorSchemeChanged`), no por el Plasma style.

Para Bliss esto sale gratis y es justo lo que queremos: el Plasma style es el
mismo en claro y oscuro (chrome azul oscuro siempre), pero el esquema de color
si cambia, asi que el fondo sigue solo a `make apply` y `make apply-dark`. No
hay nada que aplicar dos veces.

### `kpackagetool6` exige `KPackageStructure`

Los fondos de serie (`/usr/share/wallpapers/Next`) traen solo `KPlugin` y
funcionan, porque el plugin de imagen los carga por ruta. Pero
`kpackagetool6 --type Wallpaper/Images --list` no los reconoce. Anadir
`"KPackageStructure": "Wallpaper/Images"` al `metadata.json` no cambia nada
para Plasma y hace que las herramientas de KPackage vean el paquete.
