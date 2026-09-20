#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
. .venv/bin/activate
export HOMEDRIVE_HOST="${HOMEDRIVE_HOST:-0.0.0.0}"
python launch.py
