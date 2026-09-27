#!/usr/bin/env bash
# Render a post's slides.html into slide-XX.png files (1080x1350) using headless Edge.
# Usage: ./render.sh posts/001-funding-stages [slide_count]
#        ./render.sh reels/001-funding-stages  (9:16 frames from frames.html)
#        ./render.sh brand            (renders the profile picture)
set -e
EDGE="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
ROOT="$(cd "$(dirname "$0")" && pwd -W 2>/dev/null || pwd)"
DIR="${1:?usage: ./render.sh <post-folder> [slide_count]}"
DIR="${DIR%/}"

shot() { # size, output, url
  "$EDGE" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
    --virtual-time-budget=4000 --window-size="$1" --screenshot="$2" "$3" 2>/dev/null
}

if [ "$DIR" = "brand" ]; then
  shot 1080,1080 "$ROOT/brand/profile-picture.png" "file:///$ROOT/brand/profile.html"
  echo "rendered brand/profile-picture.png"
  exit
fi

# Posts have slides.html (4:5), reels have frames.html (9:16).
if [ -f "$DIR/frames.html" ]; then SRC=frames; OUT=frame; SIZE=1080,1920
else SRC=slides; OUT=slide; SIZE=1080,1350; fi

COUNT="${2:-$(grep -cE '^  (\{ |stage\()' "$DIR/$SRC.html")}"
for i in $(seq 1 "$COUNT"); do
  n=$(printf "%02d" "$i")
  shot "$SIZE" "$ROOT/$DIR/$OUT-$n.png" "file:///$ROOT/$DIR/$SRC.html?s=$i"
  echo "rendered $DIR/$OUT-$n.png"
done
