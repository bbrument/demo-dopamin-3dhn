#!/usr/bin/env bash
# Installe Meshroom dans le dossier Meshroom/ à côté de ce fichier. Les plugins s'installent ensuite dans Meshroom.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
if [ ! -x Meshroom/Meshroom ]; then
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
tree=Meshroom/aliceVision/share/aliceVision/vlfeat_K80L3.SIFT.tree
if [ ! -f "$tree" ]; then
    echo "[2/2] Téléchargement de l'arbre de vocabulaire..."
    curl -fL --retry 5 -o "$tree.part" https://gitlab.com/alicevision/trainedVocabularyTreeData/raw/master/vlfeat_K80L3.SIFT.tree
    mv "$tree.part" "$tree"
fi
echo
echo "Meshroom est installé. Lancez-le avec ./meshroom.sh, puis installez les plugins (étape 3 du README)."
