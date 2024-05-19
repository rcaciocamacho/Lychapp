#!/bin/bash

# Nombre del proyecto y ruta de instalación
PROJECT_NAME="Lychapp"
INSTALL_DIR="$HOME/.config/$PROJECT_NAME"

# Crear el directorio de instalación si no existe
mkdir -p "$INSTALL_DIR"

# Copiar los archivos del proyecto al directorio de instalación
cp -r *.{py,css,env} "$INSTALL_DIR"

# Crear un archivo .desktop para el lanzador
DESKTOP_ENTRY="[Desktop Entry]
Name=$PROJECT_NAME
Comment=Launches the $PROJECT_NAME
Exec=python3 $INSTALL_DIR/main.py
Icon=$INSTALL_DIR/launcher.ico
Terminal=false
Type=Application
Categories=Utility;
StartupNotify=true
"

# Guardar el archivo .desktop en el directorio de aplicaciones locales
echo "$DESKTOP_ENTRY" > "$HOME/.local/share/applications/$PROJECT_NAME.desktop"

# Función para configurar el atajo de teclado en GNOME
configure_gnome_shortcut() {
    SCHEMA="org.gnome.settings-daemon.plugins.media-keys"
    CUSTOM_KEYBINDINGS_PATH="/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings"

    # Encuentra la primera clave personalizada no utilizada
    N=$(gsettings get $SCHEMA custom-keybindings | grep -oP "(?<=custom).*(?=\')" | awk -F'/' '{print $NF}' | grep -Eo '[0-9]+' | sort -n | tail -n1)
    NEW_N=$((N+1))
    NEW_BINDING="$CUSTOM_KEYBINDINGS_PATH/custom$NEW_N/"

    # Añadir la nueva clave personalizada
    gsettings set $SCHEMA custom-keybindings "$(gsettings get $SCHEMA custom-keybindings | sed -e "s/]$/, '$NEW_BINDING']/")"
    gsettings set "$SCHEMA.custom-keybinding:$NEW_BINDING" name "Launch $PROJECT_NAME"
    gsettings set "$SCHEMA.custom-keybinding:$NEW_BINDING" command "python3 $INSTALL_DIR/main.py"
    gsettings set "$SCHEMA.custom-keybinding:$NEW_BINDING" binding "<Super>,"

    echo "Atajo de teclado configurado en GNOME: Super+,"
}

# Función para configurar el atajo de teclado en XFCE
configure_xfce_shortcut() {
    xfconf-query --channel xfce4-keyboard-shortcuts --property "/commands/custom/<Super>," --create --type string --set "python3 $INSTALL_DIR/main.py"
    echo "Atajo de teclado configurado en XFCE: Super+,"
}

# Función para configurar el atajo de teclado en KDE
configure_kde_shortcut() {
    # Crear un archivo kglobalshortcuts
    KDE_SHORTCUTS_FILE="$HOME/.local/share/kglobalshortcutsrc"
    SHORTCUT="[Data Entry]
_kwin__CustomShortcuts=Launch $PROJECT_NAME
_launch=python3 $INSTALL_DIR/main.py
_kdese=Super+,
    "
    echo "$SHORTCUT" >> "$KDE_SHORTCUTS_FILE"
    echo "Atajo de teclado configurado en KDE: Super+,"
}

# Detectar el entorno de escritorio y configurar el atajo de teclado
if [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]]; then
    configure_gnome_shortcut
elif [[ "$XDG_CURRENT_DESKTOP" == *"XFCE"* ]]; then
    configure_xfce_shortcut
elif [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]]; then
    configure_kde_shortcut
else
    echo "Entorno de escritorio no soportado para crear atajo automático. Configura el atajo de teclado manualmente."
fi


# Función para instalar dependencias en distribuciones basadas en Debian (Ubuntu, etc.)
install_debian_dependencies() {
    echo "Instalando dependencias para Debian/Ubuntu..."
    sudo apt update
    sudo apt install -y python3-gi python3-venv bluetoothctl network-manager pavucontrol acpi grep free
}

# Función para instalar dependencias en distribuciones basadas en Fedora
install_fedora_dependencies() {
    echo "Instalando dependencias para Fedora..."
    sudo dnf install -y python3-gobject python3-venv bluez-utils NetworkManager pavucontrol acpi grep procps-ng
}

# Función para instalar dependencias en distribuciones basadas en Arch Linux
install_arch_dependencies() {
    echo "Instalando dependencias para Arch Linux..."
    sudo pacman -Sy --noconfirm python-gobject python-virtualenv bluez-utils networkmanager pavucontrol acpi grep procps-ng
}

# Detectar la distribución del sistema operativo
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
    else
        OS=$(uname -s)
    fi
}

# Instalar dependencias según la distribución detectada
install_dependencies() {
    case "$OS" in
        debian|ubuntu)
            install_debian_dependencies
            ;;
        fedora)
            install_fedora_dependencies
            ;;
        arch|manjaro)
            install_arch_dependencies
            ;;
        *)
            echo "Distribución no soportada: $OS"
            exit 1
            ;;
    esac
}

echo "Instalando dependencias del sistema..."
install_dependencies

echo "Instalación completa."
