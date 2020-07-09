import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from shutil import copyfile
import contextlib
import os
import pulsectl

pulse = pulsectl.Pulse("t")


class AudioMenuItem(QAction):
    def __init__(self, text, parent, disable_menu, mic_name, context, icon_manager):
        super().__init__(text, parent)
        self.mic_name = mic_name
        self.disable_menu = disable_menu
        self.context = context
        self.setStatusTip("Use the %s as an input for noise suppression" % text)
        self.icon_manager = icon_manager
        self.triggered.connect(
            lambda: (
                enable_noise_suppression(self, self.context),
                self.icon_manager.set_enabled_icon(),
            )
        )


class IconManager:
    def __init__(self, disabled_icon, enabled_icon, tray):
        self.disabled_icon = disabled_icon
        self.enabled_icon = enabled_icon
        self.tray = tray
        self.set_disabled_icon()
        self.tray.setVisible(True)

    def set_enabled_icon(self):
        self.tray.setIcon(enabled_icon)

    def set_disabled_icon(self):
        self.tray.setIcon(disabled_icon)


def cli_command(command):
    if not isinstance(command, list):
        command = [command]
    with contextlib.closing(pulsectl.connect_to_cli()) as s:
        for c in command:
            s.write(c)


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
        'update-source-proplist mic_denoised_out.monitor device.description="Denoised Microphone"'
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


def enable_noise_suppression(audio_menu, context):
    load_modules(audio_menu.mic_name, context)
    audio_menu.parent().setEnabled(False)
    audio_menu.disable_menu.setEnabled(True)


def disable_noise_suppression(disable_menu, enable_menu):
    unload_modules()
    disable_menu.setEnabled(False)
    enable_menu.setEnabled(True)


if __name__ == "__main__":
    appctxt = ApplicationContext()

    enabled_ico_file = appctxt.get_resource("icon_enabled.png")
    enabled_icon = QIcon(enabled_ico_file)
    disabled_ico_file = appctxt.get_resource("icon_disabled.png")
    disabled_icon = QIcon(disabled_ico_file)
    tray = QSystemTrayIcon()
    icon_manager = IconManager(enabled_icon, disabled_icon, tray)

    main_menu = QMenu()
    disable_suppression_menu = QAction("Disable Noise Suppression")
    disable_suppression_menu.setEnabled(False)

    enable_suppression_menu = QMenu("Enable Noise Suppression")
    for src in pulse.source_list():
        enable_suppression_menu.addAction(
            AudioMenuItem(
                src.description,
                enable_suppression_menu,
                disable_suppression_menu,
                src.name,
                appctxt,
                icon_manager,
            )
        )

    disable_suppression_menu.triggered.connect(
        lambda: (
            disable_noise_suppression(
                disable_suppression_menu, enable_suppression_menu
            ),
            icon_manager.set_disabled_icon(),
        )
    )

    main_menu.addMenu(enable_suppression_menu)
    main_menu.addAction(disable_suppression_menu)

    exit_menu = QAction("Exit")
    exit_menu.triggered.connect(appctxt.app.quit)
    main_menu.addAction(exit_menu)
    tray.setContextMenu(main_menu)

    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
