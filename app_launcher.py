import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk

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

        # Aplicar el estilo CSS
        self.apply_css()

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
        Carga los comandos de conectividad en el ListBox y actualiza el estado del Bluetooth y WiFi.
        """
        connectivity_commands = self.command_loader.get_connectivity_commands()
        self.load_applications([(cmd[0], lambda cmd=cmd[1]: self.launch_application(cmd), cmd[2]) for cmd in connectivity_commands])
        self.update_bluetooth_status()
        self.update_wifi_status()

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
