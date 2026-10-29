# Plan de trabajo

Ordenado por impacto visual por hora invertida, no por dificultad tecnica.

## Hecho

- [x] Esquema de color Luna completo y funcional
- [x] Tema Aurorae instalable: barra de titulo con degradado + 3 botones
- [x] Fondo de la barra de tareas (Plasma style minimo)
- [x] Meta-paquete de tema global que enlaza todo
- [x] Makefile con install / apply / revert / backup / check
- [x] Validador de IDs de SVG y sesion KWin anidada para probar sin riesgo

## Fase 1 — que la ventana se vea XP

- [x] Prefijos `decoration-maximized` / `-inactive` (sin ellos la barra de
      titulo desaparece al maximizar)
- [x] `alldesktops.svg`, `keepabove.svg`, `keepbelow.svg`, `shade.svg`, `help.svg`
- [x] Documentadas las claves de `Blissrc` que Plasma 6 ya no lee
- [ ] Afinar los stops del degradado contra una captura real (ver `palette.md`)
- [ ] Probar con HiDPI: los biseles de 1 px son el punto debil del vectorial

## Fase 2 — que las aplicaciones se vean XP

- [x] Kvantum instalado
- [x] `Bliss.svg` derivado de KvBeige por remapeo de material (`make kvantum`)
- [x] `Bliss.kvconfig` con la paleta Luna y los colores de texto corregidos
- [x] Acentos fuera del material: seleccion azul, barra de progreso verde
- [x] `make apply` activa tambien el estilo de widgets
- [x] Radio de esquina. **Este punto estaba mal planteado.** Decia que KvBeige
      redondeaba ~6 px frente a los ~3 de Luna, y que habria que editar rutas
      en Inkscape. Medido sobre `kvantumpreview`, la variante clara ya daba
      3 px exactos: la esquina del SVG es un cuarto de circulo que ocupa la
      pieza entera, y Kvantum la escala a `frame.left` x `frame.top`, que vale
      3. Quien redondeaba de mas era la variante OSCURA, porque salia de otra
      base (KvCurves3d) y heredaba su geometria de capsula. Arreglado
      generando las dos desde la misma base; no hubo que tocar una sola ruta
- [~] Barra de progreso segmentada. **No es posible desde el tema.** Kvantum
      pinta lo relleno solo con `renderFrame`, un 9-slice, que estira sus
      piezas en vez de repetirlas; el interior no se dibuja para
      `[ProgressbarContents]`, asi que `interior.x.patternsize` no sirve ahi.
      Comprobado con cuatro pruebas en `kvantumpreview`, anotadas en
      `formats.md`. Lo que si salio de ahi: el canal estaba verde, porque el
      acento alcanzaba tambien a `progress-normal*`. Arreglado
- [ ] Opcional: cuadrar los extremos de la barra (`frame.expansion=0`) y
      subir `progressbar_thickness` de 8 a ~14, que es lo de Luna. Es cosmetico
      y el grosor afecta a la maquetacion de todas las aplicaciones, asi que
      se deja a decision
- [ ] Decidir que hacer con las apps GTK (no obedecen a Kvantum: hacen falta
      un tema GTK aparte y `gtk.css`)

## Fase 3 — el escritorio

- [x] `colors` del Plasma style separado del esquema de aplicaciones. Eran el
      mismo archivo y los iconos de la bandeja salian negros sobre el azul
- [x] `widgets/tasks.svg` — botones de ventana, cinco estados
- [x] `dialogs/background.svg` — fondo de popups y del menu Inicio
- [x] `widgets/listitem.svg` — filas con hover y seleccion
- [x] Boton Inicio verde: icono propio + etiqueta, via `make start-button`
- [x] `widgets/tooltip.svg` + `solid/widgets/tooltip.svg` — oscuros, no
      amarillos: una de las dos rutas de tooltip fuerza texto blanco
- [x] Fondo de pantalla: paquete `Wallpaper/Images` de SVG, con recorte por
      proporcion y variante oscura generada. Detalles en `formats.md`

### Decidido: el menu Inicio se queda azul oscuro

XP tiene la barra oscura y el menu Inicio claro, pero Plasma no lo permite
desde el tema: panel y popups comparten `[Colors:Window]` (ver `formats.md`).
Se valoro escribir un plasmoide de menu propio que fijase sus colores al
margen del tema, pero el azul oscuro convencio al verlo, asi que se queda.
Queda aqui escrito por si alguien se pregunta por que no es como XP.

## Fase 4 — modo oscuro (Bliss Dark)  ·  HECHA

XP no tuvo modo oscuro, asi que esto es una interpretacion, no una
reconstruccion: se apoya en la mitad Frutiger Aero del concepto y la lee como
cristal de oceano profundo. La paleta completa esta en `palette.md`.

Lo que lo hace barato es que **la geometria no cambia**. Todo el trabajo ya
hecho — el 9-slice de Aurorae, el contrato de IDs, el recolorizador de
Kvantum — se reutiliza tal cual. Solo cambia el pigmento.

- [x] `src/color-schemes/Bliss-Dark.colors`, con el contraste comprobado:
      todos los pares criticos pasan AA, el peor es 5.3:1
- [x] Aurorae `Bliss-Dark` generado desde el claro por escalado de
      luminosidad. `make check` verifica que comparte geometria exacta
- [x] Kvantum oscuro con `recolor-kvantum.py --dark`, desde la MISMA base
      que la clara (antes desde KvCurves3d, que traia botones de capsula)
- [x] Segundo look-and-feel `org.bliss.dark.desktop`
- [x] `make apply-dark` / `make apply-light` para alternar
- [x] Plasma style: NO se duplica. El chrome ya es oscuro en ambas variantes,
      como la barra de tareas de Windows 7 o 10
- [x] Fondo oscuro: no hay nada que aplicar. El plugin de imagen elige
      `images_dark` por la paleta de las aplicaciones, que ya cambia
- [ ] Decidir el cambio automatico dia/noche. Plasma no trae un conmutador de
      tema global por horario; habria que comprobar si merece la pena un
      script con `plasma-apply-lookandfeel` o dejarlo manual

## Fase 5 — acabado

- [ ] Iconos: forkear Breeze y rehacer solo los 40 visibles a diario
- [ ] Cursores
- [ ] Splash (QML)
- [ ] Tema SDDM (paquete aparte, no entra en el tema global)
- [ ] Capturas de pantalla y `previews/` para la KDE Store

## Limitaciones conocidas

- **Wayland + CSD.** Las apps GTK4, Electron y Firefox con barra de titulo
  propia ignoran la decoracion. No tiene arreglo desde el tema; se mitiga app
  por app. Conviene asumirlo ahora, no en la fase 4.
- **HiDPI.** XP es un diseno de 96 dpi a base de lineas de 1 px. A 150% de
  escala los biseles se emborronan. Si usas escalado fraccionario, disena los
  biseles de 2 px desde el principio.
- **Blur.** El cristal de Frutiger Aero depende del efecto Blur de KWin. Si el
  usuario lo tiene desactivado, el tema pierde la mitad de la gracia.

## Licencias

Los bitmaps originales de Luna (`luna.msstyles`, iconos, el fondo Bliss) son de
Microsoft. Para uso personal da igual. Si publicas: **recrea en vectores, no
extraigas los archivos originales**, y deja fuera logos y marcas. El aspecto se
puede reinterpretar; los archivos no se pueden redistribuir.
