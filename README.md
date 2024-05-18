# Lychapp

Lychapp es una aplicación lanzador de aplicaciones y comandos del sistema para entornos Linux utilizando GTK 4. Permite buscar y ejecutar aplicaciones, así como ejecutar comandos del sistema y de conectividad desde una interfaz gráfica sencilla.

## Características

- **Filtrado de Aplicaciones**: Busca y filtra aplicaciones instaladas en el sistema.
- **Comandos del Sistema**: Ejecuta comandos del sistema como apagar, reiniciar, cerrar sesión y bloquear sesión.
- **Comandos de Conectividad**: Accede a configuraciones de Bluetooth, WiFi, Audio y actualización del sistema.
- **Estado del Sistema**: Muestra el estado de la batería, la carga de la CPU y el uso de la memoria en tiempo real.
- **Ventana de Ayuda**: Muestra los comandos disponibles y los atajos de teclado.
- **Atajo de Teclado**: Abre la aplicación con un atajo de teclado configurable.

## Requisitos

- Python 3
- PyGObject (GTK 4)
- `bluetoothctl`, `nmcli`, `pactl`, `acpi`, `grep`, `free`
- Un entorno de escritorio que soporte atajos de teclado personalizados (e.g., GNOME, KDE)

## Instalación

### 1. Clonar el repositorio

```sh
git clone https://github.com/tu_usuario/Lychapp.git
cd Lychapp
```

### 2. Crear entorno virtual (opcional pero recomendado)

```sh
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```sh
pip install -r requirements.txt
```

#### Renombrar fichero de configuración

   1. Renobrar fichero sample.env a .env.
   2. Modificar el fichero para ajustarlos a nuestro sistema linux.

#### Dependencias del Sistema

Además de las dependencias de Python, asegúrate de tener instaladas las siguientes herramientas y bibliotecas en tu sistema:

   1. gtk4: La biblioteca GTK 4.
   2. bluetoothctl: Herramienta para gestionar Bluetooth desde la línea de comandos.
   3. nmcli: Herramienta para gestionar conexiones de red.
   4. pavucontrol: Herramienta para controlar los dispositivos de audio (necesita PulseAudio).
   5. acpi: Herramienta para mostrar información sobre la batería.
   6. grep: Utilidad para buscar texto en archivos.
   7. free: Utilidad para mostrar la cantidad de memoria libre y usada en el sistema.

> Puedes instalar estas herramientas en Debian/Ubuntu con:

```sh
sudo apt update
sudo apt install python3-gi python3-venv bluetoothctl network-manager pavucontrol acpi grep free
```

En Fedora, usa:

```sh
sudo dnf install python3-gobject python3-venv bluetoothctl NetworkManager pavucontrol acpi grep procps-ng
```

En Arch Linux, usa:

```sh
sudo pacman -S python-gobject python-virtualenv bluez-utils networkmanager pavucontrol acpi grep procps-ng
```

### 4. Configuración

Crea un archivo .env en el directorio raíz del proyecto con el siguiente contenido:

```ini
# Launcher commands prefix
SYS_COMMAND=sys:
CON_COMMAND=con:

# System commands
SYS_SHUTDOWN_CMD=shutdown -h now
SYS_REBOOT_CMD=reboot
SYS_LOGOUT_CMD=pkill -KILL -u
SYS_LOCK_CMD=loginctl lock-session

# Connectivity commands
CON_BLUETOOTH_CMD=bluedevil-wizard
CON_WIFI_CMD=nm-connection-editor
CON_AUDIO_CMD=pavucontrol
CON_UPDATE_CMD=kitty -e sudo pacman -Syyu && yay -Syyu 
```

### 5. Ejecutar la aplicación

```sh
python app_launcher.py
```

### 6. Crear un atajo de teclado

Para crear un atajo de teclado que abra la aplicación, puedes usar las herramientas de configuración de tu entorno de escritorio. Por ejemplo, en GNOME:

 1. Abre Configuración.
 2. Ve a Teclado.
 3. Desplázate hacia abajo y haz clic en Atajos personalizados.
 4. Haz clic en el botón +.
 5. Configura el atajo con el comando python /$HOME/.config/Lychapp/main.py.

## Uso

### Filtrado de Aplicaciones

   1. Escribe el nombre de la aplicación en el campo de texto para filtrar las aplicaciones disponibles.
   2. Selecciona la aplicación de la lista y presiona Enter para ejecutarla.

### Comandos del Sistema y Conectividad

   1. Para ejecutar comandos del sistema, escribe ```sys:``` seguido del comando deseado (e.g., sys:shutdown).
   2. Para ejecutar comandos de conectividad, escribe ```con:``` seguido del comando deseado (e.g., con:wifi).
      - En el apartado de con: Solo tendremos disponible el comando de actualizar cuando haya actualizaciones pendientes del sistema.

### Estado del Sistema

   1. El estado de la batería, la carga de la CPU y el uso de la memoria se muestran en la parte inferior de la ventana.

Ventana de Ayuda

   1. Escribe help: en el campo de texto y presiona Enter para mostrar la ventana de ayuda.

Estructura del Proyecto

```plaintext

Lychapp/
├── app_launcher.py         # Archivo principal de la aplicación
├── application_manager.py  # Gestión de aplicaciones
├── command_loader.py       # Carga de comandos desde .env
├── requirements.txt        # Dependencias del proyecto
├── style.css               # Estilos CSS para la interfaz
├── window_manager.py       # Gestión de ventanas
└── README.md               # Documentación del proyecto
```

## Tareas pendientes

   1. Gestión de temas para la interfaz de la aplicación.
   2. Ejecución de comandos de terminal desde el lanzador.

## Contribución

Las contribuciones son bienvenidas. Por favor, abre un issue o un pull request en GitHub para discutir cualquier cambio que te gustaría hacer.
Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.
Contacto

Para cualquier consulta o comentario, puedes abrir un issue en el repositorio o contactar al mantenedor del proyecto a través de GitHub.

### Explicación del Contenido del README.md

- **Características**: Una lista de las características principales de la aplicación.
- **Requisitos**: Información sobre las dependencias necesarias para ejecutar la aplicación.
- **Instalación**: Instrucciones detalladas sobre cómo clonar el repositorio, crear un entorno virtual, instalar las dependencias, configurar la aplicación y ejecutar la aplicación.
- **Uso**: Explicación de cómo usar la aplicación para filtrar aplicaciones, ejecutar comandos y ver el estado del sistema.
- **Estructura del Proyecto**: Una vista general de la estructura del proyecto y los archivos clave.
- **Contribución**: Instrucciones sobre cómo contribuir al proyecto.
- **Licencia**: Información sobre la licencia del proyecto.
- **Contacto**: Información de contacto para consultas o comentarios.

> Este archivo README.md proporciona una documentación completa y detallada del proyecto, facilitando a los usuarios y desarrolladores entender y contribuir al proyecto.
