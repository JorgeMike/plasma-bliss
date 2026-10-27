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
- [ ] Radio de esquina: Luna usa ~3 px, KvBeige ~6. Es geometria, no color,
      asi que toca editar rutas en Inkscape
- [ ] Barra de progreso segmentada (XP la dibuja a bloques, no continua)
- [ ] Decidir que hacer con las apps GTK (no obedecen a Kvantum: hacen falta
      un tema GTK aparte y `gtk.css`)

## Fase 3 — el escritorio

- [x] `colors` del Plasma style separado del esquema de aplicaciones. Eran el
      mismo archivo y los iconos de la bandeja salian negros sobre el azul
- [x] `widgets/tasks.svg` — botones de ventana, cinco estados
- [x] `dialogs/background.svg` — fondo de popups y del menu Inicio
- [x] `widgets/listitem.svg` — filas con hover y seleccion
- [ ] Boton Inicio verde: un plasmoide propio, o `kickoff` con un icono a medida
- [ ] `widgets/tooltip.svg` — el amarillo palido de XP (ahora hereda Breeze)
- [ ] Fondo de pantalla

### Pendiente de decidir: el menu Inicio claro

XP tiene la barra oscura y el menu Inicio claro. Plasma no lo permite desde el
tema: panel y popups comparten `[Colors:Window]` (ver `formats.md`). Ahora
mismo todo el chrome va azul oscuro, que es coherente y legible pero no es XP.

Las salidas, de menos a mas trabajo:

1. Aceptarlo. Un menu Inicio azul oscuro con texto blanco no desentona.
2. Un plasmoide de menu propio que fije sus colores sin depender del tema.
   Es QML de verdad, no SVG.
3. Sustituir Kickoff por otro menu que ya permita tematizarse aparte.

## Fase 4 — modo oscuro (Bliss Dark)

XP no tuvo modo oscuro, asi que esto es una interpretacion, no una
reconstruccion: se apoya en la mitad Frutiger Aero del concepto y la lee como
cristal de oceano profundo. La paleta completa esta en `palette.md`.

Lo que lo hace barato es que **la geometria no cambia**. Todo el trabajo ya
hecho — el 9-slice de Aurorae, el contrato de IDs, el recolorizador de
Kvantum — se reutiliza tal cual. Solo cambia el pigmento.

- [ ] `src/color-schemes/Bliss-Dark.colors` (copia con la paleta oscura)
- [ ] Aurorae `Bliss-Dark`: mismo `decoration.svg`, otros `<defs>`. Conviene
      extraer los degradados a un fragmento compartido antes de duplicar
- [ ] Kvantum: `make kvantum KV_BASE=KvCurves3d` con una RAMP oscura en
      `tools/recolor-kvantum.py`. KvCurves3d ya se comprobo que es oscuro y
      tiene la misma cobertura de estados que KvBeige
- [ ] Plasma style: `panel-background.svg` con el degradado hundido
- [ ] Segundo look-and-feel `org.bliss.dark.desktop`
- [ ] `make apply-dark` / `make apply-light` para alternar
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
