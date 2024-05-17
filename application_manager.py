import glob
import os
import configparser

class ApplicationManager:
    """
    Maneja la carga y filtrado de aplicaciones.

    Métodos:
        __init__: Inicializa y carga todas las aplicaciones.
        load_applications: Carga las aplicaciones desde los archivos .desktop.
        filter_applications: Filtra las aplicaciones basadas en el texto de búsqueda.
    """
    
    def __init__(self, launcher):
        """
        Inicializa y carga todas las aplicaciones.

        Args:
            launcher (AppLauncher): Instancia de AppLauncher para lanzar aplicaciones.
        """
        self.launcher = launcher
        self.all_applications = self.load_applications()

    def load_applications(self):
        """
        Carga las aplicaciones desde los archivos .desktop.

        Returns:
            list: Lista de tuplas con el nombre de la aplicación, el comando y el icono.
        """
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
                    app_command = lambda cmd=exec_command: self.launcher.launch_application(cmd)
                    applications.append((app_name, app_command, icon_name))
            except configparser.Error as e:
                print(f"Error leyendo {desktop_file}: {e}")

        return applications

    def filter_applications(self, filter_text):
        """
        Filtra las aplicaciones basadas en el texto de búsqueda.

        Args:
            filter_text (str): Texto para filtrar las aplicaciones.

        Returns:
            list: Lista de aplicaciones filtradas.
        """
        return [
            app for app in self.all_applications
            if filter_text in app[0].lower()
        ]
