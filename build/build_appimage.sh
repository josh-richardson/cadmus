#!/usr/bin/env bash
# This script builds an AppImage of Cadmus for distribution on different OSes
# First release the version with a .deb, then update Cadmus.yml, finally run this script inside a Linux VM
# (the dockerized pkg2appimage is broken in my experience)

git clone https://github.com/AppImage/pkg2appimage.git
cp Cadmus.yml ./pkg2appimage/recipes
cd pkg2appimage
./pkg2appimage recipes/Cadmus.yml
