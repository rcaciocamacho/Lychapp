import gi
import subprocess
import os
import glob
import configparser
from dotenv import load_dotenv

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Gio

class AppLauncher(Gtk.Window):
    def __init__(self):
        super().__init__(title="App Launcher")

        self.set_border_width(10)
        self.set_default_size(500, 400)
        self.set_size_request(500, 400)
        self.set_resizable(False)
        self.set_decorated(False)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        # Conectar el evento key-press-event para detectar la tecla Escape
        self.connect("key-press-event", self.on_key_press)

        # Crear un box vertical
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        # Crear un Entry para filtrar
        self.filter_entry = Gtk.Entry()
        self.filter_entry.set_placeholder_text("Filtrar aplicaciones...")
        self.filter_entry.connect("changed", self.on_filter_text_changed)
        self.filter_entry.connect("key-press-event", self.on_filter_entry_key_press)
        vbox.pack_start(self.filter_entry, False, False, 0)

        # Crear un ScrolledWindow
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_size_request(480, 320)  # Tamaño fijo del ScrolledWindow
        vbox.pack_start(scrolled_window, True, True, 0)

        # Crear un ListBox y agregarlo al ScrolledWindow
        self.listbox = Gtk.ListBox()
        self.listbox.connect("row-activated", self.on_row_activated)
        scrolled_window.add(self.listbox)

        # Cargar configuraciones desde el archivo .env
        self.load_env()

        # Obtener lista de aplicaciones y cargar en el ListBox
        self.all_applications = self.get_applications()
        self.load_applications(self.all_applications)

        # Aplicar el estilo CSS
        self.apply_css()

    def load_env(self):
        load_dotenv()
        self.sys_shutdown_cmd = os.getenv("SYS_SHUTDOWN_CMD").split("sys:")[1]
        self.sys_reboot_cmd = os.getenv("SYS_REBOOT_CMD").split("sys:")[1]
        self.sys_logout_cmd = os.getenv("SYS_LOGOUT_CMD").split("sys:")[1]
        self.sys_lock_cmd = os.getenv("SYS_LOCK_CMD").split("sys:")[1]
        self.con_bluetooth_cmd = os.getenv("CON_BLUETOOTH_CMD").split("con:")[1]
        self.con_wifi_cmd = os.getenv("CON_WIFI_CMD").split("con:")[1]
        self.con_audio_cmd = os.getenv("CON_AUDIO_CMD").split("con:")[1]
        self.con_update_cmd = os.getenv("CON_UPDATE_CMD").split("con:")[1]

    def get_applications(self):
        applications = []
        desktop_files = glob.glob('/usr/share/applications/*.desktop') + \
                        glob.glob(os.path.expanduser('~/.local/share/applications/*.desktop'))

        for desktop_file in desktop_files:
            config = configparser.ConfigParser(interpolation=None)
            try:
                config.read(desktop_file)
                if 'Desktop Entry' in config and 'Name' in config['Desktop Entry'] and 'Exec' in config['Desktop Entry']:
                    app_name = config['Desktop Entry']['Name']
                    exec_command = config['Desktop Entry']['Exec']
                    icon_name = config['Desktop Entry'].get('Icon', None)
                    app_command = lambda cmd=exec_command: self.launch_application(cmd)
                    applications.append((app_name, app_command, icon_name))
            except configparser.Error as e:
                print(f"Error leyendo {desktop_file}: {e}")

        return applications

    def load_applications(self, applications):
        # Limpiar el ListBox
        for child in self.listbox.get_children():
            self.listbox.remove(child)

        for app_name, _, icon_name in applications:
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            row.add(hbox)

            # Añadir el icono con tamaño fijo
            if icon_name:
                icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DIALOG)
                icon.set_pixel_size(32)  # Tamaño fijo del icono
            else:
                icon = Gtk.Image.new_from_icon_name("application-x-executable", Gtk.IconSize.DIALOG)
                icon.set_pixel_size(32)  # Tamaño fijo del icono
            hbox.pack_start(icon, False, False, 0)

            # Añadir el nombre de la aplicación con una separación de 10px
            label = Gtk.Label(label=app_name, xalign=0.5)
            label.set_xalign(0.0)
            label.set_margin_start(10)  # Separación de 10px entre el icono y el texto
            hbox.pack_start(label, True, True, 0)

            self.listbox.add(row)

        self.listbox.show_all()

    def load_system_commands(self):
        system_commands = [
            ("Apagar", self.shutdown, "system-shutdown"),
            ("Reiniciar", self.reboot, "system-reboot"),
            ("Cerrar sesión", self.logout, "system-log-out"),
            ("Bloquear sesión", self.lock, "system-lock-screen")
        ]

        self.load_applications(system_commands)

    def load_connectivity_commands(self):
        connectivity_commands = [
            ("Bluetooth", self.open_bluetooth_settings, "preferences-system-bluetooth"),
            ("Wifi", self.open_wifi_settings, "network-wireless"),
            ("Audio", self.open_audio_settings, "audio-card"),
            ("Actualizar", self.update_system, "system-software-update")
        ]

        self.load_applications(connectivity_commands)

    def on_filter_text_changed(self, entry):
        filter_text = entry.get_text().lower()
        if filter_text.startswith("sys:"):
            self.load_system_commands()
        elif filter_text.startswith("con:"):
            self.load_connectivity_commands()
        else:
            filtered_applications = [
                app for app in self.all_applications
                if filter_text in app[0].lower()
            ]
            self.load_applications(filtered_applications)

    def on_filter_entry_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Return or event.keyval == Gdk.KEY_KP_Enter:
            filter_text = self.filter_entry.get_text().lower()
            if filter_text.startswith("sys:") or filter_text.startswith("con:"):
                if len(self.listbox.get_children()) == 1:
                    self.listbox.select_row(self.listbox.get_row_at_index(0))
                    self.on_row_activated(self.listbox, self.listbox.get_row_at_index(0))
            else:
                filtered_applications = [
                    app for app in self.all_applications
                    if self.filter_entry.get_text().lower() in app[0].lower()
                ]
                if len(filtered_applications) == 1:
                    self.listbox.select_row(self.listbox.get_row_at_index(0))
                    self.on_row_activated(self.listbox, self.listbox.get_row_at_index(0))

    def on_row_activated(self, listbox, row):
        index = row.get_index()
        filter_text = self.filter_entry.get_text().lower()
        if filter_text.startswith("sys:") or filter_text.startswith("con:"):
            command_name, command_func, _ = self.listbox.get_children()[index].get_child().get_children()
            print(f"{command_name.get_text()} ejecutado")
            command_func()
        else:
            filtered_applications = [
                app for app in self.all_applications
                if self.filter_entry.get_text().lower() in app[0].lower()
            ]
            app_name, app_command, _ = filtered_applications[index]
            self.filter_entry.set_text(app_name)  # Mostrar el nombre en el Gtk.Entry
            print(f"{app_name} lanzado")
            app_command()
            self.close()  # Cerrar la ventana

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close()  # Cerrar la ventana al pulsar Escape

    def shutdown(self):
        print("Apagar el sistema")
        subprocess.Popen(self.sys_shutdown_cmd.split())

    def reboot(self):
        print("Reiniciar el sistema")
        subprocess.Popen(self.sys_reboot_cmd.split())

    def logout(self):
        print("Cerrar sesión")
        subprocess.Popen([self.sys_logout_cmd, os.getlogin()])

    def lock(self):
        print("Bloquear sesión")
        subprocess.Popen(self.sys_lock_cmd.split())

    def open_bluetooth_settings(self):
        print("Abrir configuración de Bluetooth")
        subprocess.Popen(self.con_bluetooth_cmd.split())

    def open_wifi_settings(self):
        print("Abrir configuración de Wifi")
        subprocess.Popen(self.con_wifi_cmd.split())

    def open_audio_settings(self):
        print("Abrir configuración de Audio")
        subprocess.Popen(self.con_audio_cmd.split())

    def update_system(self):
        print("Actualizar el sistema")
        subprocess.Popen(self.con_update_cmd.split())

    def launch_application(self, exec_command):
        print(f"Lanzando {exec_command}")
        subprocess.Popen(exec_command.split())

    def apply_css(self):
        style_provider = Gtk.CssProvider()

        css_file = "style.css"
        with open(css_file, "rb") as f:
            css_data = f.read()

        style_provider.load_from_data(css_data)

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

if __name__ == "__main__":
    win = AppLauncher()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
