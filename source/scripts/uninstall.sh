#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
rm -rf .venv
echo "Environnement Python supprimé. Les fichiers du dossier drive/ sont conservés."
