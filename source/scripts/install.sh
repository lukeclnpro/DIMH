#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
command -v python3 >/dev/null || { echo "Python 3 est requis."; exit 1; }
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
chmod +x scripts/*.sh
echo
echo "Installation terminée."
echo "Mot de passe par défaut: change-me"
echo "Lance: ./scripts/start.sh"
