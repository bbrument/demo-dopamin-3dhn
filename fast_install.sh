#!/usr/bin/env bash
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
install_engraving=false

case "${1:-}" in
    "")
        ;;
    --engraving)
        install_engraving=true
        ;;
    --help|-h)
        echo "Usage: ./fast_install.sh [--engraving]"
        echo "Installe Meshroom, les plugins requis et le moteur RNb-NeuS2."
        echo "--engraving installe aussi le plugin facultatif mrEngravingSeg (environ 4,5 Go)."
        exit 0
        ;;
    *)
        echo "Option inconnue : $1" >&2
        echo "Usage: ./fast_install.sh [--engraving]" >&2
        exit 2
        ;;
esac

echo "Cette installation télécharge plusieurs dizaines de Go et peut durer 1 à 2 heures."
if [ ! -x "$here/Meshroom/Meshroom" ]; then
    "$here/installer.sh"
fi

plugin_cli="$here/Meshroom/meshroom_plugins"
if [ ! -x "$plugin_cli" ]; then
    echo "ERREUR : meshroom_plugins est introuvable dans Meshroom." >&2
    echo "Cette version doit être remplacée par la nightly actuelle ; renommez l'ancien dossier Meshroom puis relancez." >&2
    exit 1
fi

install_plugin() {
    local name="$1"
    local plugin_dir="$here/Meshroom/plugins/$name"

    if [ -d "$plugin_dir/meshroom" ]; then
        echo "$name : déjà installé."
        return
    fi

    echo "Installation de $name..."
    "$plugin_cli" install --force "$name"
    if [ ! -d "$plugin_dir/meshroom" ]; then
        echo "ERREUR : l'installation de $name n'a pas créé le dossier attendu : $plugin_dir/meshroom" >&2
        exit 1
    fi
}

for plugin in mrSegmentation mrLedGetter mrLINOUniPS mrRNbNeuS2; do
    install_plugin "$plugin"
done

if [ "$install_engraving" = true ]; then
    install_plugin mrEngravingSeg
fi

"$here/finaliser.sh"
echo
echo "Installation terminée. Lancez Meshroom avec ./meshroom.sh."
