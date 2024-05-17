import os
from dotenv import load_dotenv

class CommandLoader:
    """
    Carga y gestiona los comandos desde el archivo .env.

    Métodos:
        __init__: Inicializa y carga los comandos desde el archivo .env.
        get_system_commands: Devuelve una lista de comandos del sistema.
        get_connectivity_commands: Devuelve una lista de comandos de conectividad.
    """
    
    def __init__(self):
        """
        Inicializa y carga los comandos desde el archivo .env.
        """
        load_dotenv()
        self.sys_command_prefix = os.getenv("SYS_COMMAND")
        self.con_command_prefix = os.getenv("CON_COMMAND")

        self.sys_shutdown_cmd = os.getenv("SYS_SHUTDOWN_CMD")
        self.sys_reboot_cmd = os.getenv("SYS_REBOOT_CMD")
        self.sys_logout_cmd = os.getenv("SYS_LOGOUT_CMD")
        self.sys_lock_cmd = os.getenv("SYS_LOCK_CMD")
        self.con_bluetooth_cmd = os.getenv("CON_BLUETOOTH_CMD")
        self.con_wifi_cmd = os.getenv("CON_WIFI_CMD")
        self.con_audio_cmd = os.getenv("CON_AUDIO_CMD")
        self.con_update_cmd = os.getenv("CON_UPDATE_CMD")

    def get_system_commands(self):
        """
        Devuelve una lista de comandos del sistema.

        Returns:
            list: Lista de tuplas con el nombre del comando, el comando y el icono.
        """
        return [
            ("Apagar", self.sys_shutdown_cmd, "system-shutdown"),
            ("Reiniciar", self.sys_reboot_cmd, "system-reboot"),
            ("Cerrar sesión", self.sys_logout_cmd, "system-log-out"),
            ("Bloquear sesión", self.sys_lock_cmd, "system-lock-screen")
        ]

    def get_connectivity_commands(self):
        """
        Devuelve una lista de comandos de conectividad.

        Returns:
            list: Lista de tuplas con el nombre del comando, el comando y el icono.
        """
        return [
            ("Bluetooth", self.con_bluetooth_cmd, "preferences-system-bluetooth"),
            ("Wifi", self.con_wifi_cmd, "network-wireless"),
            ("Audio", self.con_audio_cmd, "audio-card"),
            ("Actualizar", self.con_update_cmd, "system-software-update")
        ]
