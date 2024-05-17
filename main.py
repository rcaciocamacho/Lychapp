import gi
gi.require_version('Gtk', '4.0')
from app_launcher import AppLauncher

from gi.repository import Gtk

if __name__ == "__main__":
    app = Gtk.Application(application_id="com.warcrinux.AppLauncher")

    def on_activate(app):
        win = AppLauncher()
        win.set_application(app)
        win.present()

    app.connect("activate", on_activate)
    app.run(None)
