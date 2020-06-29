#!/usr/bin/env bash
for size in 16 24 32 48 64; do
    convert icon.png -resize ${size}x${size} base/${size}.png
done

for size in 128 256 512 1024; do
    convert icon.png -resize ${size}x${size} linux/${size}.png
done