#!/usr/bin/env bash
# Installe Meshroom et les plugins de l'atelier dans le dossier Meshroom/ à côté de ce fichier.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
if [ ! -x Meshroom/bin/uv ]; then
    echo "[1/2] Téléchargement de Meshroom (600 Mo)..."
    url=$(curl -fsSL https://api.github.com/repos/alicevision/Meshroom/releases/tags/nightly |
        grep -o 'https://[^"]*linux-full\.tar\.gz' | head -1)
    [ -n "$url" ] || { echo "ERREUR : impossible de trouver Meshroom en ligne."; exit 1; }
    curl -fL -C - --retry 5 -o meshroom.tar.gz "$url"
    echo "Extraction..."
    tar xzf meshroom.tar.gz
    mv Meshroom-*-linux Meshroom
    rm meshroom.tar.gz
fi
echo "[2/2] Installation des plugins (1 à 2 heures, 30 Go)..."
Meshroom/bin/uv run --no-project --python 3.11 scripts/install.py
echo
echo "Installation terminée. Lancez Meshroom avec ./meshroom.sh"
