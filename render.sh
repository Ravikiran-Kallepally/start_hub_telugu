#!/usr/bin/env bash
# Render a post's slides.html into slide-XX.png files (1080x1350) using headless Edge.
# Usage: ./render.sh posts/001-funding-stages [slide_count]
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

COUNT="${2:-$(grep -oE '^  \{ ' "$DIR/slides.html" | wc -l)}"
for i in $(seq 1 "$COUNT"); do
  n=$(printf "%02d" "$i")
  shot 1080,1350 "$ROOT/$DIR/slide-$n.png" "file:///$ROOT/$DIR/slides.html?s=$i"
  echo "rendered $DIR/slide-$n.png"
done
