# SVG que faltan en este Plasma style

Plasma hereda de Breeze cualquier SVG ausente, asi que el tema funciona
incompleto. Esta es la lista real del tema `default` del sistema, en orden
sugerido de ataque (los primeros son los que mas se ven):

1. `panel-background.svg`  — hecho (barra de tareas)
2. `tasks.svg`             — botones de ventana en la barra
3. `button.svg`            — botones de los plasmoides
4. `background.svg`        — fondo de popups y del menu de inicio
5. `frame.svg`             — marcos genericos
6. `listitem.svg`          — filas seleccionables (menu de inicio)
7. `lineedit.svg`          — campos de texto
8. `tabbar.svg`, `scrollbar.svg`, `slider.svg`, `toolbar.svg`
9. `checkmarks.svg`, `radiobutton.svg`, `switch.svg`, `arrows.svg`
10. `clock.svg`, `calendar.svg`, `pager.svg`, `plasmoidheading.svg`

Inspecciona cualquiera de ellos para ver la convencion de IDs:

    zcat /usr/share/plasma/desktoptheme/default/widgets/button.svgz | less

Plasma acepta `.svg` y `.svgz` (gzip). Durante el desarrollo usa `.svg`.
