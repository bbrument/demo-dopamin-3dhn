#!/usr/bin/env bash
# Complète l'installation des plugins faite dans Meshroom (moteur RNb-NeuS2).
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
uv="$here/Meshroom/bin/uv"
if [ ! -x "$uv" ]; then
    echo "Meshroom n'est pas encore installé : lancez d'abord ./installer.sh"
    exit 1
fi
exec "$uv" run --no-project --python 3.11 "$here/scripts/finaliser.py"
