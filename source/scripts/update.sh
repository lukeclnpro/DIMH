#!/usr/bin/env bash
set -e
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TEMP_DIR"' EXIT

cd "$BASE_DIR"
. .venv/bin/activate

git clone --depth 1 --branch main https://github.com/LukeCOULON/DIMH.git "$TEMP_DIR/repository"
SOURCE_DIR="$TEMP_DIR/repository/source"

test -d "$SOURCE_DIR/server"
test -d "$SOURCE_DIR/web"
cp -a "$SOURCE_DIR/launch.py" "$SOURCE_DIR/launch.txt" "$SOURCE_DIR/requirements.txt" "$BASE_DIR/"
cp -a "$SOURCE_DIR/server" "$SOURCE_DIR/web" "$BASE_DIR/"
cp -a "$SOURCE_DIR/scripts/start.sh" "$SOURCE_DIR/scripts/install.sh" "$SOURCE_DIR/scripts/uninstall.sh" "$BASE_DIR/scripts/"
cp -a "$SOURCE_DIR/systemd/home-drive.service" "$BASE_DIR/systemd/"

pip install -r requirements.txt --upgrade
echo "HomeDrive mis à jour."
