"""Termine l'installation de l'atelier : arbre de vocabulaire, plugins Meshroom, moteur RNb-NeuS2.

Lancé par installer.bat / installer.sh, une fois Meshroom extrait dans Meshroom/. Peut être relancé : chaque étape
déjà faite est sautée.
"""
import shutil
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
MESHROOM_PLUGINS = MESHROOM / ("meshroom_plugins.exe" if WINDOWS else "meshroom_plugins")

PLUGINS = ["mrSegmentation", "mrLedGetter", "mrLINOUniPS", "mrRNbNeuS2"]
VOC_TREE_URL = "https://gitlab.com/alicevision/trainedVocabularyTreeData/raw/master/vlfeat_K80L3.SIFT.tree"
VOC_TREE = MESHROOM / "aliceVision" / "share" / "aliceVision" / "vlfeat_K80L3.SIFT.tree"
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


def step_voc_tree():
    if VOC_TREE.exists():
        return print("Arbre de vocabulaire : déjà là.")
    print("Arbre de vocabulaire...")
    download(VOC_TREE_URL, VOC_TREE)


def step_plugins():
    subprocess.run([str(MESHROOM_PLUGINS), "list"], check=True, stdout=subprocess.DEVNULL)  # crée plugins/
    for name in PLUGINS:
        if (PLUGINS_DIR / name).is_dir():
            print(f"Plugin {name} : déjà là.")
            continue
        print(f"Plugin {name}...")
        subprocess.run([str(MESHROOM_PLUGINS), "install", "-f", name], check=True)


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
    if not MESHROOM_PLUGINS.exists():
        sys.exit(f"ERREUR : Meshroom introuvable dans {MESHROOM}")
    free = shutil.disk_usage(REPO).free / 1e9
    if free < 30 and not PLUGINS_DIR.exists():
        sys.exit(f"ERREUR : {free:.0f} Go libres sur ce disque, il en faut 30.")
    for step in (step_voc_tree, step_plugins, step_rnb_neus2):
        try:
            step()
        except (subprocess.CalledProcessError, OSError) as exc:
            sys.exit(f"ERREUR ({step.__name__}) : {exc}")
    print("Plugins installés.")


if __name__ == "__main__":
    main()
