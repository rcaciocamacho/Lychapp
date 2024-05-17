import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib, Gio

from command_loader import CommandLoader
from application_manager import ApplicationManager
import subprocess

class AppLauncher(Gtk.Window):
    """
    Maneja la ventana principal y la lógica de la interfaz.

    Métodos:
        __init__: Inicializa la ventana y los componentes de la interfaz.
        load_applications: Carga las aplicaciones en el ListBox.
        load_system_commands: Carga los comandos del sistema en el ListBox.
        load_connectivity_commands: Carga los comandos de conectividad en el ListBox.
        update_battery_status: Actualiza el estado de la batería.
        update_cpu_load: Actualiza la carga de la CPU.
        update_memory_status: Actualiza el estado de la memoria.
        update_status_labels: Actualiza las etiquetas de estado (batería, CPU y memoria).
        on_filter_text_changed: Filtra las aplicaciones o comandos basados en el texto de entrada.
        on_filter_entry_key_press: Maneja el evento de pulsación de teclas en el campo de filtro.
        on_row_activated: Ejecuta la aplicación o comando seleccionado.
        on_key_press: Maneja el evento de pulsación de teclas en la ventana.
        launch_application: Lanza una aplicación.
        apply_css: Aplica el estilo CSS a la ventana.
    """

    def __init__(self):
        """
        Inicializa la ventana y los componentes de la interfaz.
        """
        super().__init__(title="App Launcher")

        self.command_loader = CommandLoader()
        self.application_manager = ApplicationManager(self)

        self.set_default_size(500, 400)
        self.set_size_request(500, 400)  # Fixed size
        self.set_resizable(False)  # Make window non-resizable
        self.set_decorated(False)  # Remove window decorations
        self.set_modal(True)
        self.set_valign(Gtk.Align.CENTER)
        self.set_halign(Gtk.Align.CENTER)

        # Crear un controlador de eventos para capturar eventos de teclado
        self.key_controller = Gtk.EventControllerKey()
        self.key_controller.connect("key-pressed", self.on_key_press)
        self.add_controller(self.key_controller)

        # Crear un box vertical
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_child(vbox)

        # Crear un Entry para filtrar
        self.filter_entry = Gtk.Entry()
        self.filter_entry.set_placeholder_text("Filtrar aplicaciones...")
        self.filter_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, "edit-symbolic")

        self.filter_entry.connect("changed", self.on_filter_text_changed)

        # Crear un controlador de eventos de teclado para el Entry
        self.filter_entry_key_controller = Gtk.EventControllerKey()
        self.filter_entry_key_controller.connect("key-pressed", self.on_filter_entry_key_press)
        self.filter_entry.add_controller(self.filter_entry_key_controller)
        
        vbox.append(self.filter_entry)

        # Crear un ScrolledWindow
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_min_content_height(320)  # Tamaño mínimo del ScrolledWindow
        vbox.append(scrolled_window)

        # Crear un ListBox y agregarlo al ScrolledWindow
        self.listbox = Gtk.ListBox()
        self.listbox.connect("row-activated", self.on_row_activated)
        scrolled_window.set_child(self.listbox)

        # Cargar las aplicaciones en el ListBox
        self.load_applications(self.application_manager.all_applications)

        # Crear etiquetas para el estado de la batería, la carga de la CPU y la memoria
        self.battery_image = Gtk.Image.new_from_pixbuf(self.load_icon("battery", 16))
        self.battery_label = Gtk.Label()

        self.cpu_image = Gtk.Image.new_from_pixbuf(self.load_icon("cpu", 16))
        self.cpu_label = Gtk.Label()

        self.memory_image = Gtk.Image.new_from_pixbuf(self.load_icon("memory", 16))
        self.memory_label = Gtk.Label()
        
        # Crear un box horizontal para las etiquetas de estado
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        status_box.set_halign(Gtk.Align.CENTER)

        # Añadir batería
        battery_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        battery_box.append(self.battery_image)
        battery_box.append(self.battery_label)
        status_box.append(battery_box)

        # Añadir CPU
        cpu_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        cpu_box.append(self.cpu_image)
        cpu_box.append(self.cpu_label)
        status_box.append(cpu_box)

        # Añadir memoria
        memory_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        memory_box.append(self.memory_image)
        memory_box.append(self.memory_label)
        status_box.append(memory_box)
        
        # Añadir el box de estado al contenedor principal
        vbox.append(status_box)

        # Iniciar el temporizador para actualizar las etiquetas de estado
        GLib.timeout_add_seconds(1, self.update_status_labels)

        # Aplicar el estilo CSS
        self.apply_css()

    def load_icon(self, icon_name, size):
        """
        Carga un icono desde el tema con un tamaño especificado.

        Args:
            icon_name (str): Nombre del icono.
            size (int): Tamaño del icono en píxeles.

        Returns:
            GdkPixbuf.Pixbuf: El icono cargado.
        """
        theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        return theme.load_icon(icon_name, size, 0)

    def load_applications(self, applications):
        """
        Carga las aplicaciones en el ListBox.

        Args:
            applications (list): Lista de aplicaciones a cargar.
        """
        # Limpiar el ListBox
        while (child := self.listbox.get_first_child()) is not None:
            self.listbox.remove(child)

        for app_name, _, icon_name in applications:
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
        self.load_applications([(cmd[0], lambda cmd=cmd[1]: self.launch_application(cmd), cmd[2]) for cmd in connectivity_commands])
        self.update_bluetooth_status()
        self.update_wifi_status()
        self.update_audio_status()

    def update_bluetooth_status(self):
        """
        Actualiza el estado de la conexión Bluetooth en el ListBox.
        """
        for row in self.listbox:
            hbox = row.get_child()
            label = hbox.get_first_child().get_next_sibling()
            if "Bluetooth" in label.get_text():
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
            if "Wifi" in label.get_text():
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
            if "Audio" in label.get_text():
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
                if line.startswith("yes:"):
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
            result = subprocess.run(['pactl', 'list', 'sinks'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if "Name:" in line:
                    return line.split("Name:")[1].strip()
            return "Desconocido"
        except Exception as e:
            print(f"Error obteniendo el estado de Audio: {e}")
            return "Desconocido"

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
            str: Memoria ocupada y disponible.
        """
        try:
            result = subprocess.run(['free', '-m'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                memory_line = lines[1].split()
                used_memory = memory_line[2]
                total_memory = memory_line[1]
                return f"{used_memory}M/{total_memory}M"
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

        self.battery_label.set_text(battery_status)
        self.cpu_label.set_text(cpu_load)
        self.memory_label.set_text(memory_status)

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
            command_name, command_func, _ = hbox.get_first_child(), hbox.get_first_child().get_next_sibling(), hbox.get_first_child().get_next_sibling().get_next_sibling()
            print(f"{command_name.get_text()} ejecutado")
            command_func()
        else:
            filtered_applications = self.application_manager.filter_applications(filter_text)
            app_name, app_command, _ = filtered_applications[index]
            self.filter_entry.set_text(app_name)  # Mostrar el nombre en el Gtk.Entry
            print(f"{app_name} lanzado")
            app_command()
            self.close()  # Cerrar la ventana

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
        css_file = "style.css"
        with open(css_file, "rb") as f:
            css_data = f.read()

        css_provider.load_from_data(css_data)

        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
