// Disposicion tipo Windows XP: barra inferior de 30 px con menu Inicio,
// lanzadores rapidos, lista de ventanas, bandeja y reloj.
//
// Se ejecuta SOLO al aplicar el tema global (plasma-apply-lookandfeel -a).
// Sobrescribe la disposicion actual del usuario: por eso `make apply` no lo
// toca y hay un objetivo aparte, `make apply-global`.

var desktop = desktopForScreen(0) || desktops()[0];
desktop.wallpaperPlugin = "org.kde.image";

var panel = new Panel;
panel.location = "bottom";
panel.height    = 30;
panel.alignment = "left";
panel.hiding    = "none";

var kickoff = panel.addWidget("org.kde.plasma.kickoff");
kickoff.currentConfigGroup = ["General"];
kickoff.writeConfig("icon", "bliss-start");         // src/icons/Bliss/scalable/apps/
// sin menuLabel: solo el icono, sin texto
panel.addWidget("org.kde.plasma.showdesktop");      // "Mostrar escritorio"

var tasks = panel.addWidget("org.kde.plasma.taskmanager");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("groupingStrategy", 1);           // agrupa como XP
tasks.writeConfig("showOnlyCurrentDesktop", false);
tasks.writeConfig("iconsOnly", false);              // icono + texto, como XP

panel.addWidget("org.kde.plasma.systemtray");
panel.addWidget("org.kde.plasma.digitalclock");
