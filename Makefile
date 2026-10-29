# Bliss — tema global de Plasma 6 (Windows XP Luna x Frutiger Aero)
#
#   make            muestra esta ayuda
#   make install    copia los componentes a ~/.local/share (NO cambia nada visible)
#   make apply      activa colores + Plasma style + decoracion de ventana
#   make revert     vuelve a Breeze
#
SHELL := /bin/bash

NAME   := Bliss
DARK   := Bliss-Dark
LNF_ID := org.bliss.desktop
LNF_DK := org.bliss.dark.desktop
SRC    := src
DEST   ?= $(HOME)/.local/share
CFG    ?= $(HOME)/.config
STAMP  := $(shell date +%Y%m%d-%H%M%S)

# Tema Kvantum base del que se derivan Bliss.svg y Bliss.kvconfig.
# KvBeige se eligio porque su boton ya tiene la estructura de Luna: borde
# crisp de 1 px, bisel vertical y pulsado invertido.
# La variante OSCURA sale de la MISMA base que la clara. Antes salia de
# KvCurves3d, que es oscuro de serie, pero con su geometria venian botones en
# forma de capsula; Luna los tiene a 3 px de radio. Compartiendo base, claro y
# oscuro comparten geometria exacta y solo se diferencian en el pigmento.
KV_BASE := KvBeige
KV_DARK := $(KV_BASE)
KV_DIR  := /usr/share/Kvantum/$(KV_BASE)
KV_DDIR := $(KV_DIR)

KWRITE := $(shell command -v kwriteconfig6 2>/dev/null)
KREAD  := $(shell command -v kreadconfig6 2>/dev/null)
QDBUS  := $(shell command -v qdbus6 2>/dev/null || command -v qdbus 2>/dev/null)

.DEFAULT_GOAL := help
.PHONY: help install uninstall apply apply-deco apply-global revert backup restore \
        kvantum kvantum-dark aurorae-dark dark apply-dark apply-light _apply \
        reload start-button start-button-revert \
        check list install-colors install-aurorae install-plasma install-lnf \
        install-icons install-kvantum install-wallpaper \
        wallpaper wallpaper-apply icons

help:
	@printf "\033[1mBliss\033[0m — tema global de Plasma 6\n"
	@printf "\n"
	@printf "  \033[36mmake install\033[0m       instala los componentes en ~/.local/share\n"
	@printf "  \033[36mmake uninstall\033[0m     los borra\n"
	@printf "  \033[36mmake apply\033[0m         activa la variante CLARA\n"
	@printf "  \033[36mmake apply-dark\033[0m    activa la variante OSCURA\n"
	@printf "  \033[36mmake dark\033[0m          regenera la variante oscura desde la clara\n"
	@printf "  \033[36mmake apply-global\033[0m  aplica el tema global entero (REHACE el panel)\n"
	@printf "  \033[36mmake revert\033[0m        vuelve a Breeze\n"
	@printf "  \033[36mmake backup\033[0m        guarda tu config actual en ./backup/\n"
	@printf "  \033[36mmake restore\033[0m       restaura el backup mas reciente\n"
	@printf "  \033[36mmake kvantum\033[0m       regenera el tema Kvantum desde $(KV_BASE)\n"
	@printf "  \033[36mmake icons\033[0m         espiga los iconos XP de LinXP a build/\n"
	@printf "  \033[36mmake wallpaper\033[0m     regenera el fondo desde bliss.svg\n"
	@printf "  \033[36mmake wallpaper-apply\033[0m pone el fondo en tu escritorio\n"
	@printf "  \033[36mmake start-button\033[0m  pone el icono Inicio verde en tu panel\n"
	@printf "  \033[36mmake reload\033[0m        reinicia plasmashell para ver los cambios\n"
	@printf "  \033[36mmake check\033[0m         valida SVG y JSON antes de instalar\n"
	@printf "  \033[36mmake list\033[0m          muestra que hay instalado ahora mismo\n"
	@printf "\n"
	@printf "Ciclo normal:  make check && make install && make apply\n"

# ---------------------------------------------------------------- instalacion
install: install-colors install-aurorae install-plasma install-lnf install-icons \
         install-kvantum install-wallpaper
	@echo ">> instalado. Ahora: make apply"

install-colors:
	@install -Dm644 $(SRC)/color-schemes/$(NAME).colors $(DEST)/color-schemes/$(NAME).colors
	@install -Dm644 $(SRC)/color-schemes/$(DARK).colors $(DEST)/color-schemes/$(DARK).colors
	@echo "   colores      -> $(NAME) y $(DARK)"

install-aurorae:
	@rm -rf $(DEST)/aurorae/themes/$(NAME)
	@mkdir -p $(DEST)/aurorae/themes
	@rm -rf $(DEST)/aurorae/themes/$(DARK)
	@cp -r $(SRC)/aurorae/$(NAME) $(DEST)/aurorae/themes/
	@cp -r $(SRC)/aurorae/$(DARK) $(DEST)/aurorae/themes/
	@echo "   decoracion   -> $(NAME) y $(DARK)"

install-plasma:
	@rm -rf $(DEST)/plasma/desktoptheme/$(NAME)
	@mkdir -p $(DEST)/plasma/desktoptheme
	@cp -r $(SRC)/plasma/desktoptheme/$(NAME) $(DEST)/plasma/desktoptheme/
	@echo "   plasma style -> $(DEST)/plasma/desktoptheme/$(NAME)"

install-icons:
	@rm -rf $(DEST)/icons/$(NAME)
	@mkdir -p $(DEST)/icons
	@cp -r $(SRC)/icons/$(NAME) $(DEST)/icons/
	-@gtk-update-icon-cache -qtf $(DEST)/icons/$(NAME) 2>/dev/null || true
# El icono de Inicio va TAMBIEN a hicolor: el tema de iconos activo del
# usuario no tiene por que ser Bliss, y hicolor es el respaldo universal
# al que llega cualquier tema por herencia.
	@install -Dm644 $(SRC)/icons/$(NAME)/scalable/apps/bliss-start.svg \
		$(DEST)/icons/hicolor/scalable/apps/bliss-start.svg
	-@gtk-update-icon-cache -qtf $(DEST)/icons/hicolor 2>/dev/null || true
# Los mapas de bits espigados de LinXP viven en build/, fuera del repositorio,
# asi que se mezclan aqui si estan. Si no estan, el tema sigue siendo valido:
# todo cae a breeze-dark por herencia.
	@if [ -d build/icons/$(NAME) ]; then \
		cp -r build/icons/$(NAME)/. $(DEST)/icons/$(NAME)/; \
		echo "   iconos       -> $(DEST)/icons/$(NAME) (+ $$(find build/icons/$(NAME) -name '*.png' | wc -l) PNG de LinXP)"; \
	else \
		echo "   iconos       -> $(DEST)/icons/$(NAME) (sin los de LinXP: ejecuta make icons)"; \
	fi
	-@gtk-update-icon-cache -qtf $(DEST)/icons/$(NAME) 2>/dev/null || true

install-lnf:
	@rm -rf $(DEST)/plasma/look-and-feel/$(LNF_ID)
	@mkdir -p $(DEST)/plasma/look-and-feel
	@rm -rf $(DEST)/plasma/look-and-feel/$(LNF_DK)
	@cp -r $(SRC)/look-and-feel/$(LNF_ID) $(DEST)/plasma/look-and-feel/
	@cp -r $(SRC)/look-and-feel/$(LNF_DK) $(DEST)/plasma/look-and-feel/
	@echo "   tema global  -> $(LNF_ID) y $(LNF_DK)"

install-wallpaper:
	@rm -rf $(DEST)/wallpapers/$(NAME)
	@mkdir -p $(DEST)/wallpapers
	@cp -r $(SRC)/wallpapers/$(NAME) $(DEST)/wallpapers/
	@echo "   fondo        -> $(DEST)/wallpapers/$(NAME)"

install-kvantum:
	@for v in $(NAME) $(DARK); do \
		if [ -f $(SRC)/kvantum/$$v/$$v.svg ]; then \
			mkdir -p $(CFG)/Kvantum/$$v; \
			cp $(SRC)/kvantum/$$v/$$v.svg $(SRC)/kvantum/$$v/$$v.kvconfig $(CFG)/Kvantum/$$v/; \
			echo "   kvantum      -> $(CFG)/Kvantum/$$v"; \
		else \
			echo "   kvantum      -- omitido: falta $(SRC)/kvantum/$$v/$$v.svg"; \
		fi; \
	done

uninstall:
	@rm -rf $(DEST)/color-schemes/$(NAME).colors \
		$(DEST)/aurorae/themes/$(NAME) $(DEST)/aurorae/themes/$(DARK) \
		$(DEST)/plasma/desktoptheme/$(NAME) \
		$(DEST)/plasma/look-and-feel/$(LNF_ID) $(DEST)/plasma/look-and-feel/$(LNF_DK) \
		$(DEST)/icons/$(NAME) \
		$(DEST)/icons/hicolor/scalable/apps/bliss-start.svg \
		$(CFG)/Kvantum/$(NAME) $(CFG)/Kvantum/$(DARK) \
		$(DEST)/wallpapers/$(NAME)
	@echo ">> desinstalado (la config activa no se ha tocado; usa: make revert)"

# ----------------------------------------------------------------- aplicacion
apply: apply-light

apply-light:
	@$(MAKE) --no-print-directory _apply VARIANT=$(NAME)

apply-dark:
	@$(MAKE) --no-print-directory _apply VARIANT=$(DARK)

# El Plasma style es el MISMO en claro y oscuro: el chrome del shell ya es
# azul oscuro en ambos, igual que la barra de tareas de Windows 7 o 10. Solo
# cambian el esquema de color, la decoracion y el estilo de widgets.
_apply:
	@plasma-apply-colorscheme $(VARIANT)
	@plasma-apply-desktoptheme $(NAME)
	@if [ -z "$(KWRITE)" ]; then echo "!! falta kwriteconfig6"; exit 1; fi
	@$(KWRITE) --file kwinrc --group org.kde.kdecoration2 --key library org.kde.kwin.aurorae
	@$(KWRITE) --file kwinrc --group org.kde.kdecoration2 --key theme __aurorae__svg__$(VARIANT)
	@if [ -d $(CFG)/Kvantum/$(VARIANT) ] && command -v kvantummanager >/dev/null; then \
		kvantummanager --set $(VARIANT) >/dev/null 2>&1; \
		$(KWRITE) --file kdeglobals --group KDE --key widgetStyle kvantum; \
		echo "   estilo de widgets -> kvantum/$(VARIANT)"; \
	fi
# El tema de iconos es el MISMO en claro y oscuro: Bliss solo sobrescribe
# carpetas, dispositivos y tipos de archivo, y hereda el resto de breeze-dark.
	@$(KWRITE) --file kdeglobals --group Icons --key Theme $(NAME)
	@echo "   iconos            -> $(NAME) (hereda de breeze-dark)"
	@if [ -n "$(QDBUS)" ]; then $(QDBUS) org.kde.KWin /KWin reconfigure; fi
	@echo ">> $(VARIANT) aplicado. El panel NO se ha tocado."
	@echo "   las aplicaciones Qt ya abiertas no releen los iconos: reinicialas"

# Sobrescribe la disposicion del panel. Hace backup automatico antes.
apply-global: backup
	@plasma-apply-lookandfeel -a $(LNF_ID)
	@echo ">> tema global aplicado. Si el panel queda raro: make restore"

revert:
	-@plasma-apply-colorscheme BreezeLight
	-@plasma-apply-desktoptheme default
	@if [ -n "$(KWRITE)" ]; then \
		$(KWRITE) --file kwinrc --group org.kde.kdecoration2 --key library org.kde.breeze; \
		$(KWRITE) --file kwinrc --group org.kde.kdecoration2 --key theme Breeze; \
	$(KWRITE) --file kdeglobals --group KDE --key widgetStyle Breeze; \
		$(KWRITE) --file kdeglobals --group Icons --key Theme breeze-dark; \
	fi
	@if [ -n "$(QDBUS)" ]; then $(QDBUS) org.kde.KWin /KWin reconfigure; fi
	@echo ">> de vuelta en Breeze"

# ------------------------------------------------------------- red de seguridad
backup:
	@mkdir -p backup/$(STAMP)
	@for f in kdeglobals kwinrc plasmarc plasmashellrc \
		plasma-org.kde.plasma.desktop-appletsrc; do \
		[ -f $(CFG)/$$f ] && cp $(CFG)/$$f backup/$(STAMP)/ || true; \
	done
	@echo ">> config guardada en backup/$(STAMP)/"

restore:
	@last=$$(ls -1d backup/*/ 2>/dev/null | tail -1); \
	if [ -z "$$last" ]; then echo "!! no hay backups"; exit 1; fi; \
	cp $$last/* $(CFG)/ && echo ">> restaurado desde $$last"; \
	echo "   cierra sesion, o ejecuta: plasmashell --replace &"

# -------------------------------------------------------------------- iconos
# Los iconos XP NO estan en el repositorio. LinXP no publica licencia, asi que
# se bajan a build/ y de ahi los recoge `make install`. Mismo trato que
# KvBeige: la base vive fuera, nosotros guardamos la receta.
icons:
	@python3 -I tools/fetch-icons.py

# --------------------------------------------------------------------- fondo
# bliss-dark.svg y contents/ son GENERADOS. La unica fuente es bliss.svg: para
# cambiar el paisaje, editalo (Inkscape vale) y vuelve a ejecutar esto.
wallpaper:
	@python3 -I tools/make-dark-wallpaper.py \
		$(SRC)/wallpapers/$(NAME)/bliss.svg $(SRC)/wallpapers/$(NAME)/bliss-dark.svg
	@python3 -I tools/build-wallpaper.py $(SRC)/wallpapers/$(NAME)

# Fuera de `make apply` a proposito: esto toca el escritorio del usuario.
# No hay version clara y otra oscura que aplicar: el paquete lleva las dos y
# Plasma elige segun la paleta de las aplicaciones, asi que el fondo sigue
# solo a `make apply` y `make apply-dark`.
wallpaper-apply:
	@plasma-apply-wallpaperimage $(DEST)/wallpapers/$(NAME)

# ------------------------------------------------------------------- kvantum
# Bliss.svg y Bliss.kvconfig son GENERADOS. Para cambiar la paleta, edita las
# rampas de tools/recolor-kvantum.py y vuelve a ejecutar esto.
kvantum:
	@test -d $(KV_DIR) || { echo "!! falta $(KV_DIR) (sudo apt install qt6-style-kvantum)"; exit 1; }
	@python3 -I tools/recolor-kvantum.py $(KV_DIR)/$(KV_BASE).svg src/kvantum/$(NAME)/$(NAME).svg
	@python3 -I tools/make-kvconfig.py $(KV_DIR)/$(KV_BASE).kvconfig src/kvantum/$(NAME)/$(NAME).kvconfig

# Kickoff guarda su icono en la config del PANEL del usuario, no en el tema,
# asi que esto toca plasma-org.kde.plasma.desktop-appletsrc. Es reversible.
start-button:
	@python3 -I tools/set-start-button.py
	@$(MAKE) --no-print-directory reload

start-button-revert:
	@python3 -I tools/set-start-button.py --revert
	@$(MAKE) --no-print-directory reload

# Las tres piezas oscuras se GENERAN desde las claras o desde una base oscura.
# La geometria no cambia en ninguna: solo el pigmento.
dark: aurorae-dark kvantum-dark
	@echo ">> variante oscura regenerada"

aurorae-dark:
	@python3 -I tools/make-dark-aurorae.py

kvantum-dark:
	@test -d $(KV_DDIR) || { echo "!! falta $(KV_DDIR)"; exit 1; }
	@mkdir -p $(SRC)/kvantum/$(DARK)
	@python3 -I tools/recolor-kvantum.py $(KV_DDIR)/$(KV_DARK).svg $(SRC)/kvantum/$(DARK)/$(DARK).svg --dark
	@python3 -I tools/make-kvconfig.py $(KV_DDIR)/$(KV_DARK).kvconfig $(SRC)/kvantum/$(DARK)/$(DARK).kvconfig --dark

# Plasma cachea el Plasma style: si cambias un SVG sin cambiar el nombre del
# tema, hay que reiniciar el shell para verlo.
reload:
	@rm -rf $(HOME)/.cache/plasma-svgelements* $(HOME)/.cache/plasma_theme_$(NAME)* 2>/dev/null || true
	@if systemctl --user is-active --quiet plasma-plasmashell; then \
		systemctl --user restart plasma-plasmashell; \
		echo ">> plasmashell reiniciado"; \
	else \
		(plasmashell --replace >/dev/null 2>&1 &); \
		echo ">> plasmashell relanzado"; \
	fi

# ----------------------------------------------------------------- validacion
check:
	@ok=0; \
	for f in $$(find $(SRC) -name "*.svg"); do \
		python3 -I -c "import xml.etree.ElementTree as E,sys; E.parse(sys.argv[1])" $$f \
			|| { echo "!! SVG invalido: $$f"; ok=1; }; \
	done; \
	for f in $$(find $(SRC) -name "*.json"); do \
		python3 -I -m json.tool $$f >/dev/null \
			|| { echo "!! JSON invalido: $$f"; ok=1; }; \
	done; \
	for p in decoration close minimize maximize restore; do \
		[ -f $(SRC)/aurorae/$(NAME)/$$p.svg ] \
			|| { echo "!! falta aurorae/$$p.svg"; ok=1; }; \
	done; \
	python3 -I tools/check-ids.py || ok=1; \
	if [ $$ok -eq 0 ]; then echo ">> todo correcto"; else exit 1; fi

list:
	@echo "-- instalado en $(DEST):"
	-@ls -d $(DEST)/color-schemes/$(NAME).colors $(DEST)/aurorae/themes/$(NAME) \
		$(DEST)/plasma/desktoptheme/$(NAME) $(DEST)/plasma/look-and-feel/$(LNF_ID) \
		$(DEST)/icons/$(NAME) 2>/dev/null
	@echo "-- activo ahora:"
	@if [ -n "$(KREAD)" ]; then \
		printf "   esquema de color : "; $(KREAD) --file kdeglobals --group General --key ColorScheme; \
		printf "   plasma style     : "; $(KREAD) --file plasmarc --group Theme --key name; \
		printf "   decoracion       : "; $(KREAD) --file kwinrc --group org.kde.kdecoration2 --key theme; \
		printf "   estilo de widgets: "; $(KREAD) --file kdeglobals --group KDE --key widgetStyle; \
	fi
