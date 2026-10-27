#!/usr/bin/env bash
# Arranca un KWin anidado, en una ventana, con una configuracion AISLADA.
#
# Para esto existe: puedes probar la decoracion de ventana sin tocar tu sesion
# real. Si el tema esta roto, cierras la ventana y ya esta — tu escritorio ni
# se entera.
set -euo pipefail

for c in kwin_wayland dbus-run-session kwriteconfig6; do
    command -v "$c" >/dev/null || { echo "falta: $c"; exit 1; }
done
APP="${1:-konsole}"
command -v "$APP" >/dev/null || { echo "falta la aplicacion de prueba: $APP"; exit 1; }

TMP="$(mktemp -d /tmp/bliss-test-XXXXXX)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/config"

# Config minima que solo activa Bliss. XDG_DATA_HOME se deja intacto para que
# encuentre los temas ya instalados con `make install`.
cat > "$TMP/config/kwinrc" <<RC
[org.kde.kdecoration2]
library=org.kde.kwin.aurorae
theme=__aurorae__svg__Bliss
RC
kwriteconfig6 --file "$TMP/config/kdeglobals" --group General --key ColorScheme Bliss
kwriteconfig6 --file "$TMP/config/kdeglobals" --group KDE     --key widgetStyle Breeze

echo ">> KWin anidado 1280x800 con Bliss. Cierra la ventana para salir."
XDG_CONFIG_HOME="$TMP/config" \
    dbus-run-session -- kwin_wayland --width 1280 --height 800 --xwayland -- "$APP"
