# Bliss — tema global de Plasma 6 (Windows XP Luna x Frutiger Aero)
#
#   make            muestra esta ayuda
#   make install    copia los componentes a ~/.local/share (NO cambia nada visible)
#   make apply      activa colores + Plasma style + decoracion de ventana
#   make revert     vuelve a Breeze
#
SHELL := /bin/bash

NAME   := Bliss
LNF_ID := org.bliss.desktop
SRC    := src
DEST   ?= $(HOME)/.local/share
CFG    ?= $(HOME)/.config
STAMP  := $(shell date +%Y%m%d-%H%M%S)

# Tema Kvantum base del que se derivan Bliss.svg y Bliss.kvconfig.
# KvBeige se eligio porque su boton ya tiene la estructura de Luna: borde
# crisp de 1 px, bisel vertical y pulsado invertido.
KV_BASE := KvBeige
KV_DIR  := /usr/share/Kvantum/$(KV_BASE)

KWRITE := $(shell command -v kwriteconfig6 2>/dev/null)
KREAD  := $(shell command -v kreadconfig6 2>/dev/null)
QDBUS  := $(shell command -v qdbus6 2>/dev/null || command -v qdbus 2>/dev/null)

.DEFAULT_GOAL := help
.PHONY: help install uninstall apply apply-deco apply-global revert backup restore \
        kvantum apply-kvantum reload \
        check list install-colors install-aurorae install-plasma install-lnf \
        install-icons install-kvantum

help:
	@printf "\033[1mBliss\033[0m — tema global de Plasma 6\n"
	@printf "\n"
	@printf "  \033[36mmake install\033[0m       instala los componentes en ~/.local/share\n"
	@printf "  \033[36mmake uninstall\033[0m     los borra\n"
	@printf "  \033[36mmake apply\033[0m         activa colores + Plasma style + decoracion\n"
	@printf "  \033[36mmake apply-global\033[0m  aplica el tema global entero (REHACE el panel)\n"
	@printf "  \033[36mmake revert\033[0m        vuelve a Breeze\n"
	@printf "  \033[36mmake backup\033[0m        guarda tu config actual en ./backup/\n"
	@printf "  \033[36mmake restore\033[0m       restaura el backup mas reciente\n"
	@printf "  \033[36mmake kvantum\033[0m       regenera el tema Kvantum desde $(KV_BASE)\n"
	@printf "  \033[36mmake reload\033[0m        reinicia plasmashell para ver los cambios\n"
	@printf "  \033[36mmake check\033[0m         valida SVG y JSON antes de instalar\n"
	@printf "  \033[36mmake list\033[0m          muestra que hay instalado ahora mismo\n"
	@printf "\n"
	@printf "Ciclo normal:  make check && make install && make apply\n"

# ---------------------------------------------------------------- instalacion
install: install-colors install-aurorae install-plasma install-lnf install-icons install-kvantum
	@echo ">> instalado. Ahora: make apply"

install-colors:
	@install -Dm644 $(SRC)/color-schemes/$(NAME).colors $(DEST)/color-schemes/$(NAME).colors
	@echo "   colores      -> $(DEST)/color-schemes/$(NAME).colors"

install-aurorae:
	@rm -rf $(DEST)/aurorae/themes/$(NAME)
	@mkdir -p $(DEST)/aurorae/themes
	@cp -r $(SRC)/aurorae/$(NAME) $(DEST)/aurorae/themes/
	@echo "   decoracion   -> $(DEST)/aurorae/themes/$(NAME)"

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
	@echo "   iconos       -> $(DEST)/icons/$(NAME)"

install-lnf:
	@rm -rf $(DEST)/plasma/look-and-feel/$(LNF_ID)
	@mkdir -p $(DEST)/plasma/look-and-feel
	@cp -r $(SRC)/look-and-feel/$(LNF_ID) $(DEST)/plasma/look-and-feel/
	@echo "   tema global  -> $(DEST)/plasma/look-and-feel/$(LNF_ID)"

install-kvantum:
	@if [ -f $(SRC)/kvantum/$(NAME)/$(NAME).svg ]; then \
		mkdir -p $(CFG)/Kvantum/$(NAME); \
		cp $(SRC)/kvantum/$(NAME)/$(NAME).svg $(SRC)/kvantum/$(NAME)/$(NAME).kvconfig $(CFG)/Kvantum/$(NAME)/; \
		echo "   kvantum      -> $(CFG)/Kvantum/$(NAME)"; \
	else \
		echo "   kvantum      -- omitido: falta $(SRC)/kvantum/$(NAME)/$(NAME).svg"; \
	fi

uninstall:
	@rm -rf $(DEST)/color-schemes/$(NAME).colors \
		$(DEST)/aurorae/themes/$(NAME) \
		$(DEST)/plasma/desktoptheme/$(NAME) \
		$(DEST)/plasma/look-and-feel/$(LNF_ID) \
		$(DEST)/icons/$(NAME) \
		$(CFG)/Kvantum/$(NAME)
	@echo ">> desinstalado (la config activa no se ha tocado; usa: make revert)"

# ----------------------------------------------------------------- aplicacion
apply:
	@plasma-apply-colorscheme $(NAME)
	@plasma-apply-desktoptheme $(NAME)
	@$(MAKE) --no-print-directory apply-deco
	@$(MAKE) --no-print-directory apply-kvantum
	@echo ">> aplicado. El panel NO se ha tocado (eso es: make apply-global)."

apply-kvantum:
	@if [ -d $(CFG)/Kvantum/$(NAME) ] && command -v kvantummanager >/dev/null; then \
		kvantummanager --set $(NAME) >/dev/null 2>&1; \
		$(KWRITE) --file kdeglobals --group KDE --key widgetStyle kvantum; \
		echo "   estilo de widgets -> kvantum/$(NAME)"; \
	else \
		echo "   kvantum -- no instalado, omitido"; \
	fi

apply-deco:
	@if [ -z "$(KWRITE)" ]; then echo "!! falta kwriteconfig6 (paquete kconfig-bin)"; exit 1; fi
	@$(KWRITE) --file kwinrc --group org.kde.kdecoration2 --key library org.kde.kwin.aurorae
	@$(KWRITE) --file kwinrc --group org.kde.kdecoration2 --key theme __aurorae__svg__$(NAME)
	@if [ -n "$(QDBUS)" ]; then $(QDBUS) org.kde.KWin /KWin reconfigure; \
	else echo "   (sin qdbus: cierra sesion para ver la decoracion)"; fi

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

# ------------------------------------------------------------------- kvantum
# Bliss.svg y Bliss.kvconfig son GENERADOS. Para cambiar la paleta, edita las
# rampas de tools/recolor-kvantum.py y vuelve a ejecutar esto.
kvantum:
	@test -d $(KV_DIR) || { echo "!! falta $(KV_DIR) (sudo apt install qt6-style-kvantum)"; exit 1; }
	@python3 -I tools/recolor-kvantum.py $(KV_DIR)/$(KV_BASE).svg src/kvantum/$(NAME)/$(NAME).svg
	@python3 -I tools/make-kvconfig.py $(KV_DIR)/$(KV_BASE).kvconfig src/kvantum/$(NAME)/$(NAME).kvconfig

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
