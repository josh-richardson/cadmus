import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from fbs_runtime.application_context.PyQt5 import ApplicationContext
import contextlib
import os
import pulsectl

pulse = pulsectl.Pulse('t')


class AudioMenuItem(QAction):

    def __init__(self, text, parent, disable_menu, mic_name):
        super().__init__(text, parent)
        self.mic_name = mic_name
        self.disable_menu = disable_menu
        self.setStatusTip('Use the %s as an input for noise suppression' % text)
        self.triggered.connect(lambda: enable_noise_suppression(self))


def cli_command(command):
    with contextlib.closing(pulsectl.connect_to_cli()) as s:
        s.write(command)


def load_modules(mic_name):
    print(mic_name)
    pulse.module_load('module-null-sink', 'sink_name=%s' % 'mic_denoised_out')
    pulse.module_load('module-ladspa-sink',
                      'sink_name=mic_raw_in sink_master=mic_denoised_out label=noise_suppressor_mono plugin=%s' % os.path.abspath(
                          "librnnoise_ladspa.so"))

    pulse.module_load('module-loopback',
                      'latency_msec=1 source=%s sink=mic_raw_in channels=1' % mic_name)

    cli_command("update-source-proplist mic_denoised_out.monitor device.description=\"Denoised Microphone\"")

    pulse.source_default_set("mic_denoised_out.monitor")


def unload_modules():
    cli_command("unload-module module-loopback")
    cli_command("unload-module module-null-sink")
    cli_command("unload-module module-ladspa-sink")


def enable_noise_suppression(audio_menu):
    load_modules(audio_menu.mic_name)
    audio_menu.parent().setEnabled(False)
    audio_menu.disable_menu.setEnabled(True)


def disable_noise_suppression(disable_menu, enable_menu):
    unload_modules()
    disable_menu.setEnabled(False)
    enable_menu.setEnabled(True)


if __name__ == '__main__':
    appctxt = ApplicationContext()

    ico_file = appctxt.get_resource('icon.png')
    icon = QIcon(ico_file)

    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)

    main_menu = QMenu()
    disable_suppression_menu = QAction("Disable Noise Suppression")
    disable_suppression_menu.setEnabled(False)

    enable_suppression_menu = QMenu("Enable Noise Suppression")
    for src in pulse.source_list():
        enable_suppression_menu.addAction(
            AudioMenuItem(src.description, enable_suppression_menu, disable_suppression_menu, src.name))

    disable_suppression_menu.triggered.connect(
        lambda: disable_noise_suppression(disable_suppression_menu, enable_suppression_menu))

    main_menu.addMenu(enable_suppression_menu)
    main_menu.addAction(disable_suppression_menu)

    exit_menu = QAction("Exit")
    exit_menu.triggered.connect(appctxt.app.quit)
    main_menu.addAction(exit_menu)
    tray.setContextMenu(main_menu)

    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
