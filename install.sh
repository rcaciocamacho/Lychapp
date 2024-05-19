#!/bin/bash

# Nombre del proyecto y ruta de instalación
PROJECT_NAME="Lychapp"
INSTALL_DIR="$HOME/.config/$PROJECT_NAME"

# Crear el directorio de instalación si no existe
mkdir -p "$INSTALL_DIR"

# Copiar los archivos del proyecto al directorio de instalación
cp -r *.{py,css,env} "$INSTALL_DIR"
cp -r themes "$INSTALL_DIR"

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
