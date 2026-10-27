# Falta `Bliss.svg`

Kvantum necesita **dos** archivos con el mismo nombre base: el `.kvconfig`
(ya esta) y un `Bliss.svg` con los graficos. Sin el SVG, Kvantum cae a su
tema por defecto y los colores de `[GeneralColors]` se aplican a medias.

Camino corto (recomendado): parte de un tema existente en lugar de dibujar
desde cero.

    sudo apt install qt6-style-kvantum
    cp /usr/share/Kvantum/KvArc/KvArc.svg ./Bliss.svg

Luego abre `Bliss.svg` en Inkscape. Los IDs siguen el patron
`<elemento>-<estado>-<parte>`, por ejemplo:

    button-normal-top        button-focused-left     button-pressed-center
    lineedit-normal-topleft  tab-toggled-center      menuitem-focused-center

Misma logica de 9-slice que Aurorae y que el Plasma style.
