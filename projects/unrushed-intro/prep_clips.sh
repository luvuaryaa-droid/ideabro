#!/usr/bin/env bash
# Cuts the clean (text-free) pieces of the artist's videos into work/clips/. Originals in raw/ are untouched.
# vid1: old captions sit in a band ~65-80 % down the frame, so prints use the clean top area only.
# vid3: kinetic text sits low and the @handle mid-right, so the rain print is the clean top-left square.
# vid2: sketchbook pages shown whole (only the artist's own small @handle in the corner).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p work/clips
C="-an -c:v libx264 -crf 14 -preset fast -pix_fmt yuv420p -r 24"
cut(){ ffmpeg -v error -y -ss "$2" -t "$3" -i "raw/$1.mp4" -vf "$4" $C "work/clips/$5.mp4"; }
cut vid1 3.0  2.6 "crop=740:370:0:0,scale=1240:620:flags=lanczos"   sun
cut vid1 10.0 3.0 "crop=920:460:360:0,scale=1240:620:flags=lanczos" trail
cut vid1 26.0 2.4 "crop=920:460:180:0,scale=1240:620:flags=lanczos" bridge
cut vid1 21.0 3.0 "crop=740:370:0:90,scale=1240:620:flags=lanczos"  sign
cut vid1 40.0 2.8 "crop=920:460:180:0,scale=1240:620:flags=lanczos" seeds
cut vid3 4.0  3.5 "crop=540:540:0:0,scale=620:620:flags=lanczos"    rain
cut vid2 1.55 1.4  "crop=1080:1070:0:370,scale=700:694:flags=lanczos" page_glasses
cut vid2 4.55 1.4  "crop=1080:1060:0:360,scale=700:688:flags=lanczos" page_tulips
cut vid2 6.05 1.4  "crop=1080:1060:0:360,scale=700:688:flags=lanczos" page_figs
cut vid2 7.55 1.15 "crop=1080:1100:0:330,scale=700:712:flags=lanczos" page_hat     # ends before the "Bye" title
cut vid2 9.55 0.9  "crop=1080:1300:0:230,scale=600:722:flags=lanczos" page_mosaic
mkdir -p assets
python3 -c "
from PIL import Image
Image.open('raw/sketch_cat.webp').convert('RGB').save('assets/sketch_cat.png')
im = Image.open('raw/sketch_portrait.jpg').convert('RGB'); im.thumbnail((900, 1000)); im.save('assets/sketch_portrait.png')"
echo "clips ready"
