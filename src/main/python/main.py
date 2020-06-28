import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from fbs_runtime.application_context.PyQt5 import ApplicationContext
import contextlib
import os
import pulsectl

pulse = pulsectl.Pulse('t')


def cli_command(command):
    with contextlib.closing(pulsectl.connect_to_cli()) as s:
        s.write(command)


def load_modules():
    defaults = pulse.server_info()

    pulse.module_load('module-null-sink', 'sink_name=%s' % 'mic_denoised_out')
    pulse.module_load('module-ladspa-sink',
                      'sink_name=mic_raw_in sink_master=mic_denoised_out label=noise_suppressor_mono plugin=%s' % os.path.abspath(
                          "librnnoise_ladspa.so"))

    pulse.module_load('module-loopback',
                      'latency_msec=1 source=%s sink=mic_raw_in channels=1' % defaults.default_source_name)

    cli_command("update-source-proplist mic_denoised_out.monitor device.description=\"Denoised Microphone\"")

    pulse.source_default_set("mic_denoised_out.monitor")


def unload_modules():
    cli_command("unload-module module-loopback")
    cli_command("unload-module module-null-sink")
    cli_command("unload-module module-ladspa-sink")


def load_or_unload(menu_item):
    if menu_item.isChecked():
        load_modules()
        menu_item.setText("Disable Noise Suppression")
    else:
        unload_modules()
        menu_item.setText("Enable Noise Suppression")


if __name__ == '__main__':
    appctxt = ApplicationContext()

    ico_file = appctxt.get_resource('icon.png')
    icon = QIcon(ico_file)

    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)

    menu = QMenu()
    action = QAction("Enable Noise Suppression")
    action.setCheckable(True)
    action.triggered.connect(lambda: load_or_unload(action))
    menu.addAction(action)

    quit = QAction("Quit")
    quit.triggered.connect(appctxt.app.quit)
    menu.addAction(quit)

    tray.setContextMenu(menu)

    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
