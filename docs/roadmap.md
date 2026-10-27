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

- [ ] Afinar los stops del degradado contra una captura real (ver `palette.md`)
- [ ] `alldesktops.svg`, `keepabove.svg`, `keepbelow.svg`, `shade.svg`, `help.svg`
- [ ] Prefijo `decoration-maximized`: en XP la ventana maximizada pierde los
      bordes laterales
- [ ] Probar con HiDPI: los biseles de 1 px son el punto debil del vectorial

## Fase 2 — que las aplicaciones se vean XP

- [ ] `sudo apt install qt6-style-kvantum`
- [ ] Partir de un tema Kvantum existente y reemplazar su SVG
- [ ] Botones, pestanas, campos de texto, barras de desplazamiento
- [ ] Decidir que hacer con las apps GTK (no obedecen a Kvantum: hacen falta
      un tema GTK aparte y `gtk.css`)

## Fase 3 — el escritorio

- [ ] `tasks.svg` — los botones de ventana en la barra de tareas
- [ ] `background.svg` + `listitem.svg` — el menu Inicio
- [ ] Boton Inicio verde: un plasmoide propio, o `kickoff` con un icono a medida
- [ ] Reloj y bandeja del sistema
- [ ] Fondo de pantalla

## Fase 4 — acabado

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
