#!/usr/bin/env bash
# Convertit une archive Nenuscanner en dossier pour Meshroom : ./convertir.sh [archive.zip ou dossier]
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
uv="$here/Meshroom/bin/uv"
if [ ! -x "$uv" ]; then
    echo "Meshroom n'est pas encore installé : lancez d'abord ./installer.sh"
    exit 1
fi
exec "$uv" run --no-project --python 3.11 "$here/scripts/nenuscan2mr.py" "$@"
