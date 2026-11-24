#!/usr/bin/env bash
# Lance Meshroom (installé par installer.sh).
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ ! -x "$here/Meshroom/Meshroom" ]; then
    echo "Meshroom n'est pas encore installé : lancez d'abord ./installer.sh"
    exit 1
fi
exec "$here/Meshroom/Meshroom" "$@"
