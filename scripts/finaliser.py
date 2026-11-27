"""Complète l'installation des plugins faite dans l'interface de Meshroom (Plugin Manager).

Lancé par finaliser.bat / finaliser.sh. Fait ce que le Plugin Manager ne fait pas encore : vérifier que les quatre
plugins de l'atelier sont là, et télécharger le moteur RNb-NeuS2. Peut être relancé : ce qui est fait est sauté.
"""
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

WINDOWS = sys.platform == "win32"
REPO = Path(__file__).resolve().parent.parent
MESHROOM = REPO / "Meshroom"
PLUGINS_DIR = MESHROOM / "plugins"

# mrLedGetter : Linux seulement (JAX n'a pas de version GPU sous Windows).
PLUGINS = ["mrSegmentation", "mrLINOUniPS", "mrRNbNeuS2"] + ([] if WINDOWS else ["mrLedGetter"])
RNB_VERSION = "2.0.3"
RNB_ARCHIVE = f"RNb-NeuS2-{RNB_VERSION}-" + ("windows-x86_64-cu128.zip" if WINDOWS else "linux-x86_64-cu128.tar.gz")
RNB_URL = f"https://github.com/RobinBruneau/RNb-NeuS2/releases/download/v{RNB_VERSION}/{RNB_ARCHIVE}"


def download(url, target):
    """Télécharge url vers target, en reprenant un téléchargement interrompu."""
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_name(target.name + ".part")
    start = partial.stat().st_size if partial.exists() else 0
    request = urllib.request.Request(url, headers={"User-Agent": "demo-dopamin-3dhn", "Range": f"bytes={start}-"})
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 206:
            start = 0
        total = start + int(response.headers.get("Content-Length") or 0)
        with open(partial, "ab" if start else "wb") as output:
            done = start
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
                done += len(chunk)
                if total:
                    print(f"\r  {done / 1e6:.0f} / {total / 1e6:.0f} Mo", end="", flush=True)
    print()
    partial.replace(target)


def step_plugins():
    missing = [name for name in PLUGINS if not (PLUGINS_DIR / name).is_dir()]
    if missing:
        sys.exit("Plugins manquants : " + ", ".join(missing)
                 + "\nInstallez-les dans Meshroom (bouton Manage Plugins), fermez Meshroom, puis relancez.")
    print("Plugins : tous installés (" + ", ".join(PLUGINS) + ").")


def step_rnb_neus2():
    folder = PLUGINS_DIR / "mrRNbNeuS2"
    marker = folder / f".rnb-neus2-{RNB_VERSION}"
    if marker.exists():
        return print("Moteur RNb-NeuS2 : déjà là.")
    print("Moteur RNb-NeuS2...")
    archive = folder / RNB_ARCHIVE
    download(RNB_URL, archive)
    if WINDOWS:
        with zipfile.ZipFile(archive) as content:
            content.extractall(folder)
    else:
        with tarfile.open(archive) as content:
            content.extractall(folder)
    archive.unlink()
    marker.touch()


def main():
    if not MESHROOM.is_dir():
        sys.exit(f"ERREUR : Meshroom introuvable dans {MESHROOM}")
    for step in (step_plugins, step_rnb_neus2):
        try:
            step()
        except (subprocess.CalledProcessError, OSError) as exc:
            sys.exit(f"ERREUR ({step.__name__}) : {exc}")
    print("Tout est prêt.")


if __name__ == "__main__":
    main()
