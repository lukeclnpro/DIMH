#!/usr/bin/env python3
"""Point d'entrée de HomeDrive."""

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

# Permet de lancer `python launch.py` depuis n'importe quel dossier.
ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

import uvicorn


def ask_port() -> int:
    default_port = os.getenv("HOMEDRIVE_PORT", "8000")

    while True:
        entered_port = input(f"Port du serveur [{default_port}] : ").strip()
        port_value = entered_port or default_port

        try:
            port = int(port_value)
        except ValueError:
            print("Le port doit être un nombre entre 1 et 65535.")
            continue

        if 1 <= port <= 65535:
            return port

        print("Le port doit être un nombre entre 1 et 65535.")


def get_lan_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("192.168.1.254", 80))
            return sock.getsockname()[0]
    except OSError:
        return "IP-DU-PC"


def clear_port(port: int) -> None:
    target = f"{port}/tcp"
    subprocess.run(
        ["fuser", "-k", "-TERM", target],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )

    for _ in range(10):
        if subprocess.run(
            ["fuser", "-s", target],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode != 0:
            return
        time.sleep(0.1)

    subprocess.run(
        ["fuser", "-k", "-KILL", target],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


if __name__ == "__main__":
    host = os.getenv("HOMEDRIVE_HOST", "0.0.0.0")
    port = ask_port()
    clear_port(port)
    lan_ip = get_lan_ip()

    print("================================")
    print("        HomeDrive")
    print("================================")
    print(f"Serveur : http://{host}:{port}")
    print(f"Téléphone (même Wi-Fi) : http://{lan_ip}:{port}")
    print("Réseau : accessible sur le LAN")
    print("Arrêt : Ctrl+C")
    print()

    uvicorn.run(
        "server.main:app",
        host=host,
        port=port,
        reload=False,
    )
