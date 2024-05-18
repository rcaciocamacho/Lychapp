import gi
from gi.repository import Gtk, Gdk, GLib

gi.require_version('Gtk', '4.0')

class WindowManager:
    """
    Clase encargada de la creación y gestión de ventanas.
    """

    def __init__(self, app_launcher):
        """
        Inicializa la clase WindowManager.

        Args:
            app_launcher (AppLauncher): La instancia principal de la aplicación.
        """
        self.app_launcher = app_launcher

    def create_main_window(self):
        """
        Crea y configura la ventana principal de la aplicación.
        """
        self.app_launcher.set_default_size(500, 400)
        self.app_launcher.set_size_request(500, 400)  # Fixed size
        self.app_launcher.set_resizable(False)  # Make window non-resizable
        self.app_launcher.set_decorated(False)  # Remove window decorations
        self.app_launcher.set_modal(True)
        self.app_launcher.set_valign(Gtk.Align.CENTER)
        self.app_launcher.set_halign(Gtk.Align.CENTER)

        # Crear un controlador de eventos para capturar eventos de teclado
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.app_launcher.on_key_press)
        self.app_launcher.add_controller(key_controller)

        # Conectar el evento de cambio de estado de la ventana
        self.app_launcher.connect("notify::is-active", self.app_launcher.on_is_active_notify)

        # Crear un box vertical
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.app_launcher.set_child(vbox)

        # Crear un Entry para filtrar
        filter_entry = Gtk.Entry()
        filter_entry.set_placeholder_text("Filtrar aplicaciones...")
        filter_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, "edit-symbolic")
        filter_entry.connect("changed", self.app_launcher.on_filter_text_changed)

        # Crear un controlador de eventos de teclado para el Entry
        filter_entry_key_controller = Gtk.EventControllerKey()
        filter_entry_key_controller.connect("key-pressed", self.app_launcher.on_filter_entry_key_press)
        filter_entry.add_controller(filter_entry_key_controller)
        vbox.append(filter_entry)

        self.app_launcher.filter_entry = filter_entry

        # Crear un ScrolledWindow
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_min_content_height(384)  # Tamaño mínimo del ScrolledWindow ajustado
        vbox.append(scrolled_window)

        # Crear un ListBox y agregarlo al ScrolledWindow
        listbox = Gtk.ListBox()
        listbox.connect("row-activated", self.app_launcher.on_row_activated)
        scrolled_window.set_child(listbox)

        self.app_launcher.listbox = listbox

        # Cargar las aplicaciones en el ListBox
        self.app_launcher.load_applications(self.app_launcher.application_manager.all_applications)

        # Crear etiquetas para el estado de la batería, la carga de la CPU y la memoria
        battery_image = Gtk.Image.new_from_icon_name("battery")
        battery_image.set_pixel_size(20)
        battery_label = Gtk.Label()

        cpu_image = Gtk.Image.new_from_icon_name("cpu")
        cpu_image.set_pixel_size(20)
        cpu_label = Gtk.Label()

        memory_image = Gtk.Image.new_from_icon_name("memory")
        memory_image.set_pixel_size(20)
        memory_label = Gtk.Label()

        self.app_launcher.battery_image = battery_image
        self.app_launcher.battery_label = battery_label
        self.app_launcher.cpu_image = cpu_image
        self.app_launcher.cpu_label = cpu_label
        self.app_launcher.memory_image = memory_image
        self.app_launcher.memory_label = memory_label

        # Crear un box horizontal para las etiquetas de estado
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        status_box.set_halign(Gtk.Align.CENTER)
        status_box.set_size_request(-1, 20)  # Reducir la altura del status_box

        # Añadir batería
        battery_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        battery_box.append(battery_image)
        battery_box.append(battery_label)
        status_box.append(battery_box)

        # Añadir CPU
        cpu_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        cpu_box.append(cpu_image)
        cpu_box.append(cpu_label)
        status_box.append(cpu_box)

        # Añadir memoria
        memory_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        memory_box.append(memory_image)
        memory_box.append(memory_label)
        status_box.append(memory_box)

        # Añadir icono de arroba (@)
        at_label = Gtk.Label()
        at_label.set_markup('<span size="large"><a href="https://github.com/rcaciocamacho/Lychapp">@_Lychapp</a></span>')
        at_label.set_hexpand(False)
        at_label.set_halign(Gtk.Align.CENTER)
        at_label.set_valign(Gtk.Align.CENTER)
        status_box.append(at_label)

        # Añadir el box de estado al contenedor principal
        vbox.append(status_box)

        # Iniciar el temporizador para actualizar las etiquetas de estado
        GLib.timeout_add_seconds(1, self.app_launcher.update_status_labels)

        # Aplicar el estilo CSS
        self.app_launcher.apply_css()

    def show_help_window(self):
        """
        Muestra una ventana con los comandos y atajos de teclado disponibles.
        """
        help_window = Gtk.Window(title="Ayuda")
        help_window.set_default_size(400, 300)
        help_window.set_transient_for(self.app_launcher)
        help_window.set_modal(True)
        help_window.set_decorated(False)
        help_window.set_valign(Gtk.Align.CENTER)
        help_window.set_halign(Gtk.Align.CENTER)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)
        help_window.set_child(vbox)

        help_label = Gtk.Label()
        help_label.set_markup("<b>Comandos Disponibles:</b>")
        help_label.set_xalign(0.0)
        vbox.append(help_label)

        commands = self.app_launcher.command_loader.get_system_commands() + self.app_launcher.command_loader.get_connectivity_commands()
        commands_markup = "\n".join([f"<tt>{cmd[0]}</tt>" for cmd in commands])
        commands_label = Gtk.Label()
        commands_label.set_markup(commands_markup)
        commands_label.set_xalign(0.0)
        vbox.append(commands_label)

        shortcut_label = Gtk.Label()
        shortcut_label.set_markup("<b>Atajos de Teclado:</b>")
        shortcut_label.set_xalign(0.0)
        vbox.append(shortcut_label)

        shortcuts_markup = "<tt>Ctrl+F1:</tt> Mostrar esta ventana de ayuda\n<tt>Escape:</tt> Cerrar la aplicación\n<tt>help:</tt> Mostrar esta ventana de ayuda"
        shortcuts_label = Gtk.Label()
        shortcuts_label.set_markup(shortcuts_markup)
        shortcuts_label.set_xalign(0.0)
        vbox.append(shortcuts_label)

        # Añadir evento de clic para cerrar la ventana de ayuda
        click_controller = Gtk.GestureClick()
        click_controller.connect("pressed", self.on_help_window_clicked, help_window)
        help_window.add_controller(click_controller)

        help_window.show()

    def on_help_window_clicked(self, controller, n_press, x, y, help_window):
        """
        Maneja el evento de clic en la ventana de ayuda.

        Args:
            controller (Gtk.GestureClick): El controlador de gestos de clic.
            n_press (int): El número de clics.
            x (float): La coordenada X del clic.
            y (float): La coordenada Y del clic.
            help_window (Gtk.Window): La ventana de ayuda.
        """
        help_window.close()
        self.app_launcher.filter_entry.set_text("")
