Cadmus
======================
 [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
 
Cadmus is a graphical application which allows you to remove background noise from audio in real-time in any communication app. Cadmus adds a notification icon to your shell which allows you to easily select a microphone as a source, and subsequently creates a PulseAudio output which removes all recorded background noise (typing, ambient noise, etc). If you find the application useful, leave a :star: — it helps!

<p align="center">
  <img src="https://i.imgur.com/DfhCk0j.png" alt="Cadmus GUI running on Gnome" />
</p>

### About & Usage
Whilst software exists on Windows & MacOS (Krisp, RTX Voice, etc) to remove background noise from recorded audio in real-time, no user-friendly solution seemed to exist on Linux. Cadmus was written to address this shortcoming, allowing users to remove background noise from audio in Discord/Zoom/Skype/Slack/etc calls without having to use the commandline. It is primarily a GUI frontend for @werman's [PulseAudio Noise Supression Plugin](https://github.com/werman/noise-suppression-for-voice).

When you run Cadmus, you'll see a new notification icon showing a microphone in your chosen shell. On click, you'll be able to select the microphone whose noise you wish to supress. Cadmus will then set the default PulseAudio microphone to use the virtual denoised output of the chosen microphone. Note that if you're currently recording audio, you'll have to stop recording and start again in order for changes to occur - streams which are currently being recorded will not be hot-swapped to the new input.      

### Installation

#### For Debian-based distributions:
- Download the latest `cadmus.deb` file on the [releases page]()
- Once downloaded, open the file in your chosen file explorer to install it, or run `sudo dpkg -i cadmus.deb` in a terminal

#### For non-Debian distributions:
- Download the latest `cadmus.AppImage` file on the [releases page]()
- Once downloaded, open the file in your chosen file explorer to run it (requires AppImage Launcher), or run `chmod +x cadmus.AppImage && ./cadmus.AppImage` in a terminal

#### To run from an archive:
- Download the latest `cadmus.zip` file on the [releases page]()
- Once downloaded, run `unzip cadmus.zip && cd cadmus && ./cadmus` in a terminal
 

### Status
Cadmus has been tested on Arch Linux, Debian 10 and Ubuntu 20.04. It should work with all flavors of Linux with PulseAudio installed - but if you find a bug, please do report it on the GitHub issue tracker. It's still relatively early in development & hasn't been tested extensively.

### Development
To get the project up and running, first clone the repository. Next create a virtualenv, and run `pip install -r requirements.txt`. Cadmus is written in Python making use of PyQt5 and the Fman Build System. You can invoke `fbs run` to run Cadmus from source.

### Roadmap
- [ ] Add some tests
- [ ] Gracefully start up & shut down, removing loaded modules on exit
- [ ] Run on startup & use a default microphone?
- [ ] Deploy on AUR