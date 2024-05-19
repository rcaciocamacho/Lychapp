import gi
import subprocess
import os
import configparser
from gi.repository import Gtk, Gdk, GLib

from command_loader import CommandLoader
from application_manager import ApplicationManager
from window_manager import WindowManager

gi.require_version('Gtk', '4.0')

def load_default_theme(self):
    """
    Carga y aplica el tema predeterminado desde el archivo de configuración.
    """
    config = configparser.ConfigParser()
    if config.read('themes/config.ini'):
        theme_name = config.get('Settings', 'theme', fallback=None)
        if theme_name:
            self.apply_theme(theme_name)

class AppLauncher(Gtk.Window):
    """
    Maneja la lógica principal de la aplicación.

    Métodos:
        __init__: Inicializa la aplicación y sus componentes.
        load_applications: Carga las aplicaciones en el ListBox.
        load_system_commands: Carga los comandos del sistema en el ListBox.
        load_connectivity_commands: Carga los comandos de conectividad en el ListBox.
        update_bluetooth_status: Actualiza el estado de la conexión Bluetooth.
        update_wifi_status: Actualiza el estado de la conexión WiFi.
        update_audio_status: Actualiza el estado de la salida de audio.
        get_pending_updates: Obtiene el número de paquetes pendientes de actualización.
        update_battery_status: Actualiza el estado de la batería.
        update_cpu_load: Actualiza la carga de la CPU.
        update_memory_status: Actualiza el estado de la memoria.
        update_status_labels: Actualiza las etiquetas de estado (batería, CPU y memoria).
        on_filter_text_changed: Filtra las aplicaciones o comandos basados en el texto de entrada.
        on_filter_entry_key_press: Maneja el evento de pulsación de teclas en el campo de filtro.
        on_row_activated: Ejecuta la aplicación o comando seleccionado.
        on_key_press: Maneja el evento de pulsación de teclas en la ventana.
        on_is_active_notify: Maneja el evento de cambio de estado de la ventana.
        launch_application: Lanza una aplicación.
        apply_css: Aplica el estilo CSS a la ventana.
    """

    def __init__(self):
        """
        Inicializa la aplicación y sus componentes.
        """
        super().__init__(title="App Launcher")

        self.command_loader = CommandLoader()
        self.application_manager = ApplicationManager(self)
        self.window_manager = WindowManager(self)

        # Crear la ventana principal
        self.window_manager.create_main_window()

    def on_is_active_notify(self, widget, param_spec):
        """
        Maneja el evento de cambio de estado de la ventana.
        """
        if not self.is_active:
            self.close()

    def load_icon(self, icon_name, size):
        """
        Carga un icono desde el tema con un tamaño especificado.

        Args:
            icon_name (str): Nombre del icono.
            size (int): Tamaño del icono en píxeles.

        Returns:
            Gtk.IconPaintable: El icono cargado.
        """
        theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        icon_info = theme.lookup_icon(icon_name, size, 0)
        if icon_info is not None:
            return icon_info.load_icon()
        return None

    def load_applications(self, applications):
        """
        Carga las aplicaciones en el ListBox.

        Args:
            applications (list): Lista de aplicaciones a cargar.
        """
        # Limpiar el ListBox
        while (child := self.listbox.get_first_child()) is not None:
            self.listbox.remove(child)

        for app_name, app_command, icon_name in applications:
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            row.set_child(hbox)

            # Añadir el icono con tamaño fijo
            if icon_name:
                icon = Gtk.Image.new_from_icon_name(icon_name)
                icon.set_pixel_size(32)  # Tamaño fijo del icono
            else:
                icon = Gtk.Image.new_from_icon_name("application-x-executable")
                icon.set_pixel_size(32)  # Tamaño fijo del icono
            hbox.append(icon)

            # Añadir el nombre de la aplicación con una separación de 10px
            label = Gtk.Label(label=app_name)
            label.set_xalign(0.0)
            hbox.append(label)

            # Añadir el comando de la aplicación como atributo
            row.app_command = app_command

            self.listbox.append(row)

        self.listbox.show()

    def load_system_commands(self):
        """
        Carga los comandos del sistema en el ListBox.
        """
        system_commands = self.command_loader.get_system_commands()
        self.load_applications([(cmd[0], lambda cmd=cmd[1]: self.launch_application(cmd), cmd[2]) for cmd in system_commands])

    def load_connectivity_commands(self):
        """
        Carga los comandos de conectividad en el ListBox y actualiza el estado del Bluetooth, WiFi y Audio.
        """
        connectivity_commands = self.command_loader.get_connectivity_commands()
        
        # Verificar actualizaciones pendientes
        pending_updates = self.get_pending_updates()
        if pending_updates > 0:
            # Modificar el comando de actualización para mostrar el número de paquetes pendientes
            update_command = ("Actualizar ({} paquetes)".format(pending_updates), self.launch_application(self.command_loader.update_command), "system-software-update")
            connectivity_commands.append(update_command)
        else:
            # Filtrar el comando de actualización si no hay paquetes pendientes
            connectivity_commands = [cmd for cmd in connectivity_commands if "Actualizar" not in cmd[0]]
        
        self.load_applications([(cmd[0], lambda cmd=cmd[1]: self.launch_application(cmd), cmd[2]) for cmd in connectivity_commands])
        self.update_bluetooth_status()
        self.update_wifi_status()
        self.update_audio_status()

    def get_pending_updates(self):
        """
        Obtiene el número de paquetes pendientes de actualización.

        Returns:
            int: Número de paquetes pendientes de actualización.
        """
        try:
            result = subprocess.run(['pacman', '-Qu', '|', 'wc', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                output = result.stdout.strip().split('\n')
                # Restamos la primera línea que es un encabezado
                pending_updates = len(output)
                return pending_updates
            return 0
        except Exception as e:
            print(f"Error obteniendo las actualizaciones pendientes: {e}")
            return 0

    def update_bluetooth_status(self):
        """
        Actualiza el estado de la conexión Bluetooth en el ListBox.
        """
        for row in self.listbox:
            hbox = row.get_child()
            label = hbox.get_first_child().get_next_sibling()
            if isinstance(label, Gtk.Label) and "Bluetooth" in label.get_text():
                bluetooth_status = self.get_bluetooth_status()
                label.set_text(f"Bluetooth ({bluetooth_status})")
                break

    def update_wifi_status(self):
        """
        Actualiza el estado de la conexión WiFi en el ListBox.
        """
        for row in self.listbox:
            hbox = row.get_child()
            label = hbox.get_first_child().get_next_sibling()
            if isinstance(label, Gtk.Label) and "Wifi" in label.get_text():
                wifi_status = self.get_wifi_status()
                label.set_text(f"Wifi ({wifi_status})")
                break

    def update_audio_status(self):
        """
        Actualiza el estado de la salida de audio en el ListBox.
        """
        for row in self.listbox:
            hbox = row.get_child()
            label = hbox.get_first_child().get_next_sibling()
            if isinstance(label, Gtk.Label) and "Audio" in label.get_text():
                audio_status = self.get_audio_status()
                label.set_text(f"Audio ({audio_status})")
                break

    def get_bluetooth_status(self):
        """
        Obtiene el estado actual de la conexión Bluetooth y el nombre del dispositivo conectado.

        Returns:
            str: Nombre del dispositivo Bluetooth conectado o 'Desconectado'.
        """
        try:
            result = subprocess.run(['bluetoothctl', 'info'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if "Connected: yes" in result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.strip().startswith("Name:"):
                        return line.strip().split("Name:")[1].strip()
            return "Desconectado"
        except Exception as e:
            print(f"Error obteniendo el estado de Bluetooth: {e}")
            return "Desconocido"

    def get_wifi_status(self):
        """
        Obtiene el estado actual de la conexión WiFi y el nombre de la red conectada.

        Returns:
            str: Nombre de la red WiFi conectada o 'Desconectado'.
        """
        try:
            result = subprocess.run(['nmcli', '-t', '-f', 'active,ssid', 'dev', 'wifi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if line.startswith("sí:"):
                    return line.split(":")[1]
            return "Desconectado"
        except Exception as e:
            print(f"Error obteniendo el estado de WiFi: {e}")
            return "Desconocido"

    def get_audio_status(self):
        """
        Obtiene el estado actual de la salida de audio.

        Returns:
            str: Nombre de la salida de audio activa o 'Desconocido'.
        """
        try:
            # Obtener el nombre del sink por defecto
            default_sink = subprocess.check_output(['pactl', 'get-default-sink'], text=True).strip()

            # Listar todos los sinks y filtrar por el nombre del sink por defecto
            sinks_output = subprocess.check_output(['pactl', 'list', 'sinks'], text=True)
            
            # Dividir la salida en bloques por cada sink
            sinks = sinks_output.split('\n\n')
            
            # Buscar el bloque correspondiente al sink por defecto
            for sink in sinks:
                if default_sink in sink:
                    # Buscar la línea de descripción en el bloque correspondiente
                    for line in sink.split('\n'):
                        if 'Description:' in line:
                            description = line.split('Description:')[1].strip()
                            return description
            
            return "Descripción no encontrada"
        
        except subprocess.CalledProcessError as e:
            return f"Error al ejecutar el comando: {e}"
        except Exception as e:
            return f"Error: {e}"

    def update_battery_status(self):
        """
        Obtiene el estado actual de la batería y devuelve el porcentaje de batería.

        Returns:
            str: Porcentaje de batería.
        """
        try:
            result = subprocess.run(['acpi', '-b'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                output = result.stdout.strip()
                if "Battery" in output:
                    # Extraer el porcentaje de batería
                    percentage = output.split(", ")[1].split("%")[0] + "%"
                    return percentage
            return "N/D"
        except Exception as e:
            print(f"Error obteniendo el estado de la batería: {e}")
            return "N/D"

    def update_cpu_load(self):
        """
        Obtiene la carga actual de la CPU.

        Returns:
            str: Carga de la CPU.
        """
        try:
            result = subprocess.run(['grep', 'cpu ', '/proc/stat'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                cpu_times = result.stdout.strip().split()[1:5]
                cpu_times = list(map(int, cpu_times))
                total_time = sum(cpu_times)
                idle_time = cpu_times[3]
                load = 100 * (total_time - idle_time) / total_time
                return f"{load:.2f}%"
            return "N/D"
        except Exception as e:
            print(f"Error obteniendo la carga de la CPU: {e}")
            return "N/D"

    def update_memory_status(self):
        """
        Obtiene el estado actual de la memoria.

        Returns:
            str: Porcentaje de memoria ocupada.
        """
        try:
            result = subprocess.run(['free', '-m'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                memory_line = lines[1].split()
                used_memory = int(memory_line[2])
                total_memory = int(memory_line[1])
                memory_usage_percentage = (used_memory / total_memory) * 100
                return f"{memory_usage_percentage:.2f}%"
            return "N/D"
        except Exception as e:
            print(f"Error obteniendo el estado de la memoria: {e}")
            return "N/D"

    def update_status_labels(self):
        """
        Actualiza las etiquetas de estado (batería, CPU y memoria).
        """
        battery_status = self.update_battery_status()
        cpu_load = self.update_cpu_load()
        memory_status = self.update_memory_status()
        pending_updates = self.get_pending_updates()

        self.battery_label.set_text(battery_status)
        self.cpu_label.set_text(cpu_load)
        self.memory_label.set_text(memory_status)
        self.updates_label.set_text(f"{pending_updates}")

        return True  # Return True to keep the timeout active

    def on_filter_text_changed(self, entry):
        """
        Filtra las aplicaciones o comandos basados en el texto de entrada.

        Args:
            entry (Gtk.Entry): Campo de texto de entrada.
        """
        filter_text = entry.get_text().lower()
        if filter_text.startswith(self.command_loader.sys_command_prefix):
            self.load_system_commands()
        elif filter_text.startswith(self.command_loader.con_command_prefix):
            self.load_connectivity_commands()
        elif filter_text == "help:":
            self.window_manager.show_help_window()
        elif filter_text.startswith("theme:"):
            self.load_theme_files()
        else:
            filtered_applications = self.application_manager.filter_applications(filter_text)
            self.load_applications(filtered_applications)

    def on_filter_entry_key_press(self, controller, keyval, keycode, state):
        """
        Maneja el evento de pulsación de teclas en el campo de filtro.

        Args:
            controller (Gtk.EventControllerKey): El controlador de eventos de teclado.
            keyval (int): El valor de la tecla presionada.
            keycode (int): El código de la tecla presionada.
            state (Gdk.ModifierType): El estado del modificador.
        """
        if keyval in [Gdk.KEY_Return, Gdk.KEY_KP_Enter]:
            filter_text = self.filter_entry.get_text().lower()
            if filter_text.startswith(self.command_loader.sys_command_prefix) or filter_text.startswith(self.command_loader.con_command_prefix):
                if self.listbox.get_first_child() is not None and self.listbox.get_first_child().get_next_sibling() is None:
                    self.on_row_activated(self.listbox, self.listbox.get_first_child())
            else:
                filtered_applications = self.application_manager.filter_applications(filter_text)
                if len(filtered_applications) == 1:
                    self.on_row_activated(self.listbox, self.listbox.get_first_child())
        elif keyval == Gdk.KEY_F1 and (state & Gdk.ModifierType.CONTROL_MASK):
            self.window_manager.show_help_window()

    def on_row_activated(self, listbox, row):
        """
        Ejecuta la aplicación o comando seleccionado.

        Args:
            listbox (Gtk.ListBox): El ListBox donde ocurrió el evento.
            row (Gtk.ListBoxRow): La fila seleccionada.
        """
        index = row.get_index()
        filter_text = self.filter_entry.get_text().lower()
        if filter_text.startswith(self.command_loader.sys_command_prefix) or filter_text.startswith(self.command_loader.con_command_prefix):
            hbox = row.get_child()
            command_name = hbox.get_first_child().get_next_sibling()
            if isinstance(command_name, Gtk.Label):
                command_func = row.app_command
                if command_func:
                    print(f"{command_name.get_text()} ejecutado")
                    command_func()
        elif filter_text.startswith("theme:"):
            hbox = row.get_child()
            theme_name = hbox.get_first_child().get_next_sibling()
            if isinstance(theme_name, Gtk.Label):
                self.apply_theme(theme_name.get_text())
        else:
            filtered_applications = self.application_manager.filter_applications(filter_text)
            app_name, app_command, _ = filtered_applications[index]
            self.filter_entry.set_text(app_name)  # Mostrar el nombre en el Gtk.Entry
            print(f"{app_name} lanzado")
            app_command()
            self.close()  # Cerrar la ventana

    def apply_theme(self, theme_name):
        """
        Aplica un nuevo tema CSS a la interfaz gráfica y guarda el tema seleccionado.

        Args:
            theme_name (str): Nombre del archivo de tema sin la extensión.
        """
        css_file = os.path.join('themes', f"{theme_name}.css")
        if os.path.exists(css_file):
            css_provider = Gtk.CssProvider()
            with open(css_file, "rb") as f:
                css_data = f.read()
            css_provider.load_from_data(css_data)

            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
            print(f"Tema '{theme_name}' aplicado")
            self.save_theme(theme_name)
        else:
            print(f"Archivo '{css_file}' no encontrado")

    def on_key_press(self, controller, keyval, keycode, state):
        """
        Maneja el evento de pulsación de teclas en la ventana.

        Args:
            controller (Gtk.EventControllerKey): El controlador de eventos de teclado.
            keyval (int): El valor de la tecla presionada.
            keycode (int): El código de la tecla presionada.
            state (Gdk.ModifierType): El estado del modificador.
        """
        if keyval == Gdk.KEY_Escape:
            self.close()  # Cerrar la ventana al pulsar Escape

    def launch_application(self, exec_command):
        """
        Lanza una aplicación.

        Args:
            exec_command (str): El comando para ejecutar la aplicación.
        """
        print(f"Lanzando {exec_command}")
        subprocess.Popen(exec_command.split())

    def apply_css(self):
        """
        Aplica el estilo CSS a la ventana.
        """
        css_provider = Gtk.CssProvider()
        css_file = "themes/style.css"
        with open(css_file, "rb") as f:
            css_data = f.read()

        css_provider.load_from_data(css_data)

        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def load_theme_files(self):
        """
        Carga los archivos de temas .css disponibles en el ListBox.
        """
        css_files = self.list_css_files()
        theme_commands = [(css_file, lambda css_file=css_file: self.apply_theme(css_file), "preferences-desktop-theme") for css_file in css_files]
        self.load_applications(theme_commands)
        
    def list_css_files(self):
        """
        Lista los archivos .css disponibles en el directorio themes.

        Returns:
            list: Lista de nombres de archivos .css sin la extensión.
        """
        css_files = [f[:-4] for f in os.listdir('themes') if f.endswith('.css')]
        return css_files

    def save_theme(self, theme_name):
        """
        Guarda el tema seleccionado en un archivo de configuración.

        Args:
            theme_name (str): Nombre del tema a guardar.
        """
        config = configparser.ConfigParser()
        config['Settings'] = {'theme': theme_name}
        with open('themes/config.ini', 'w') as configfile:
            config.write(configfile)



if __name__ == "__main__":
    win = AppLauncher()
    win.connect("destroy", Gtk.main_quit)
    win.show()
    Gtk.main()
