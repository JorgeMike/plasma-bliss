# SVG que faltan en este Plasma style

Plasma hereda de Breeze cualquier SVG ausente, asi que el tema funciona
incompleto. Esta es la lista real del tema `default` del sistema, en orden
sugerido de ataque (los primeros son los que mas se ven):

1. `panel-background.svg`  — HECHO (barra de tareas)
2. `tasks.svg`             — HECHO (botones de ventana en la barra)
3. `../dialogs/background.svg` — HECHO (fondo de popups y menu Inicio)
4. `listitem.svg`          — HECHO (filas con hover y seleccion)
5. `button.svg`            — botones de los plasmoides
6. `frame.svg`             — marcos genericos
7. `tooltip.svg`           — el amarillo palido de XP
8. `lineedit.svg`          — campos de texto
8. `tabbar.svg`, `scrollbar.svg`, `slider.svg`, `toolbar.svg`
9. `checkmarks.svg`, `radiobutton.svg`, `switch.svg`, `arrows.svg`
10. `clock.svg`, `calendar.svg`, `pager.svg`, `plasmoidheading.svg`

Inspecciona cualquiera de ellos para ver la convencion de IDs:

    zcat /usr/share/plasma/desktoptheme/default/widgets/button.svgz | less

Plasma acepta `.svg` y `.svgz` (gzip). Durante el desarrollo usa `.svg`.
