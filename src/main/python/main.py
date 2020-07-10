import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QWidget
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from shutil import copyfile
import contextlib
import os
import pulsectl

pulse = pulsectl.Pulse("t")


def cli_command(command):
    if not isinstance(command, list):
        command = [command]
    with contextlib.closing(pulsectl.connect_to_cli()) as s:
        for c in command:
            s.write(c + "\n")


def load_modules(mic_name, context):
    cadmus_cache_path = os.path.join(os.environ["HOME"], ".cache", "cadmus")
    if not os.path.exists(cadmus_cache_path):
        os.makedirs(cadmus_cache_path)

    cadmus_lib_path = os.path.join(cadmus_cache_path, "librnnoise_ladspa.so")

    copyfile(context.get_resource("librnnoise_ladspa.so"), cadmus_lib_path)

    pulse.module_load("module-null-sink", "sink_name=%s" % "mic_denoised_out")
    pulse.module_load(
        "module-ladspa-sink",
        "sink_name=mic_raw_in sink_master=mic_denoised_out label=noise_suppressor_mono plugin=%s"
        % cadmus_lib_path,
    )

    pulse.module_load(
        "module-loopback",
        "latency_msec=1 source=%s sink=mic_raw_in channels=1" % mic_name,
    )

    cli_command(
        [
            'update-source-proplist mic_denoised_out.monitor device.description="Cadmus_Denoised_Microphone_Output"',
            'update-sink-proplist mic_raw_in device.description="Cadmus_Raw_Microphone_Redirect"',
            'update-sink-proplist mic_denoised_out device.description="Cadmus_Microphone_Sink"',
        ]
    )

    pulse.source_default_set("mic_denoised_out.monitor")


def unload_modules():
    cli_command(
        [
            "unload-module module-loopback",
            "unload-module module-null-sink",
            "unload-module module-ladspa-sink",
        ]
    )


class AudioMenuItem(QAction):
    def __init__(self, text, parent, mic_name):
        super().__init__(text, parent)
        self.mic_name = mic_name
        self.setStatusTip("Use the %s as an input for noise suppression" % text)


class CadmusApplication(QSystemTrayIcon):
    def __init__(self, app_context, parent=None):
        QSystemTrayIcon.__init__(self, parent)
        self.app_context = app_context
        self.enabled_icon = QIcon(app_context.get_resource("icon_enabled.png"))
        self.disabled_icon = QIcon(app_context.get_resource("icon_disabled.png"))

        self.disable_suppression_menu = QAction("Disable Noise Suppression")
        self.enable_suppression_menu = QMenu("Enable Noise Suppression")
        self.exit_menu = QAction("Exit")

        self.gui_setup()

    def gui_setup(self):
        main_menu = QMenu()

        self.disable_suppression_menu.setEnabled(False)
        self.disable_suppression_menu.triggered.connect(self.disable_noise_suppression)

        for src in pulse.source_list():
            mic_menu_item = AudioMenuItem(
                src.description, self.enable_suppression_menu, src.name,
            )
            self.enable_suppression_menu.addAction(mic_menu_item)
            mic_menu_item.triggered.connect(self.enable_noise_suppression)

        self.exit_menu.triggered.connect(self.app_context.app.quit)

        main_menu.addMenu(self.enable_suppression_menu)
        main_menu.addAction(self.disable_suppression_menu)
        main_menu.addAction(self.exit_menu)

        self.setIcon(self.disabled_icon)
        self.setContextMenu(main_menu)

    def disable_noise_suppression(self):
        unload_modules()
        self.disable_suppression_menu.setEnabled(False)
        self.enable_suppression_menu.setEnabled(True)
        self.setIcon(self.disabled_icon)

    def enable_noise_suppression(self):
        load_modules(self.sender().mic_name, self.app_context)
        self.enable_suppression_menu.setEnabled(False)
        self.disable_suppression_menu.setEnabled(True)


if __name__ == "__main__":
    cadmus_context = ApplicationContext()
    parent_widget = QWidget()

    icon = CadmusApplication(cadmus_context, parent_widget)
    icon.show()

    sys.exit(cadmus_context.app.exec_())
