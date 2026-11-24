"""Convertit une archive Nenuscanner (zip ou dossier avec descriptor.yaml) en dossier pour Meshroom.

Sortie :
    <sortie>/PS/PS_XX/led_YY.<ext>              une image par pose et par LED
    <sortie>/PS/PS_XX/ambient_all_leds.<ext>    toutes les LED allumées : sert à retrouver les positions (SfM)

Aucune dépendance : Python 3.9+ suffit. convertir.bat / convertir.sh le lancent avec le uv fourni par Meshroom.
Sans option de résolution, la question est posée (NEF si le script n'est pas lancé dans un terminal).
"""
import argparse
import shutil
import sys
import zipfile
from collections import defaultdict
from pathlib import Path, PurePosixPath

ALL_LEDS = "ALL_LEDS"
NO_LED = "NO_LED"


class ConversionError(Exception):
    pass


# --- lecture de descriptor.yaml -------------------------------------------------------------------------------------

def _scalar(text):
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "'\"":
        return text[1:-1]
    if text in ("{}", "null", "~", ""):
        return {} if text == "{}" else None
    if text in ("true", "false"):
        return text == "true"
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return text


def parse_descriptor(text):
    """Lit le sous-ensemble de YAML écrit par le Nenuscanner : dictionnaires imbriqués de valeurs simples."""
    try:
        import yaml  # utilisé s'il est disponible
        return yaml.safe_load(text)
    except ImportError:
        pass
    root = {}
    stack = [(-1, root)]
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        key, separator, value = line.strip().partition(":")
        if not separator:
            raise ConversionError(f"descriptor.yaml, ligne {number} : format inattendu.")
        while stack[-1][0] >= indent:
            stack.pop()
        key = _scalar(key)
        if value.strip() == "":
            child = {}
            stack[-1][1][key] = child
            stack.append((indent, child))
        else:
            stack[-1][1][key] = _scalar(value)
    return root


# --- source : dossier ou zip ----------------------------------------------------------------------------------------

class FolderSource:
    def __init__(self, folder):
        found = [folder / "descriptor.yaml"] if (folder / "descriptor.yaml").is_file() else sorted(
            folder.glob("*/descriptor.yaml"))
        if not found:
            raise ConversionError(f"descriptor.yaml introuvable dans {folder}")
        self.root = found[0].parent

    def read_descriptor(self):
        return (self.root / "descriptor.yaml").read_text(encoding="utf-8")

    def exists(self, parts):
        return self.root.joinpath(*parts).is_file()

    def copy(self, parts, target):
        shutil.copyfile(self.root.joinpath(*parts), target)

    def close(self):
        pass


class ZipSource:
    def __init__(self, path):
        self.zip = zipfile.ZipFile(path)
        self.names = set(self.zip.namelist())
        found = sorted((n for n in self.names if PurePosixPath(n).name == "descriptor.yaml"), key=len)
        if not found:
            raise ConversionError(f"descriptor.yaml introuvable dans {path}")
        self.prefix = PurePosixPath(found[0]).parent

    def _name(self, parts):
        return str(self.prefix.joinpath(*parts))

    def read_descriptor(self):
        return self.zip.read(self._name(["descriptor.yaml"])).decode("utf-8")

    def exists(self, parts):
        return self._name(parts) in self.names

    def copy(self, parts, target):
        with self.zip.open(self._name(parts)) as src, open(target, "wb") as dst:
            shutil.copyfileobj(src, dst, 4 * 1024 * 1024)

    def close(self):
        self.zip.close()


def open_source(path):
    if path.is_dir():
        return FolderSource(path)
    if path.is_file() and zipfile.is_zipfile(path):
        return ZipSource(path)
    raise ConversionError(f"Ni un dossier ni une archive zip : {path}")


# --- plan de copie --------------------------------------------------------------------------------------------------

def _parts(raw_path, image_id):
    if not isinstance(raw_path, str):
        raise ConversionError(f"Chemin absent pour l'image {image_id}.")
    parts = [p for p in PurePosixPath(raw_path).parts if p != "/"]
    if not parts or ".." in parts:
        raise ConversionError(f"Chemin invalide pour l'image {image_id} : {raw_path}")
    return parts


def plan(descriptor, source, use_previews):
    """Retourne la liste (chemin source, chemin relatif de destination) et le nombre d'images NO_LED ignorées."""
    try:
        leds = {k: str(v["value"]).strip() for k, v in descriptor["leds"].items()}
        shutters = {k: float(v["value"]) for k, v in descriptor["shutter_speeds"].items()}
        images = descriptor["images"]
        pose_ids = sorted(descriptor["poses"], key=int)
    except (KeyError, TypeError, ValueError) as exc:
        raise ConversionError(f"descriptor.yaml incomplet ou invalide ({exc}).") from exc
    pose_numbers = {pose_id: n for n, pose_id in enumerate(pose_ids, start=1)}
    path_key = "preview_path" if use_previews else "raw_path"

    groups = defaultdict(list)
    for image_id, image in images.items():
        pose_id, led_id = image.get("pose_id"), image.get("led_id")
        if pose_id not in pose_numbers or led_id not in leds:
            raise ConversionError(f"Pose ou LED inconnue pour l'image {image_id}.")
        exposure = shutters.get(image.get("shutter_speed_id"))
        if exposure is None:
            raise ConversionError(f"Temps de pose inconnu pour l'image {image_id}.")
        groups[(pose_id, led_id)].append((exposure, str(image_id), _parts(image.get(path_key), image_id)))

    copies, skipped = [], 0
    for (pose_id, led_id), candidates in sorted(groups.items(), key=lambda g: (pose_numbers[g[0][0]], g[0][1])):
        candidates.sort()
        parts = candidates[len(candidates) // 2][2]  # exposition médiane s'il y en a plusieurs
        if not source.exists(parts):
            raise ConversionError(f"Image introuvable dans l'archive : {'/'.join(parts)}")
        extension = PurePosixPath(parts[-1]).suffix.lower()
        pose, label = pose_numbers[pose_id], leds[led_id]
        if label == ALL_LEDS:
            target = Path("PS") / f"PS_{pose:02d}" / f"ambient_all_leds{extension}"
        elif label.isdigit():
            target = Path("PS") / f"PS_{pose:02d}" / f"led_{int(label):02d}{extension}"
        elif label == NO_LED:
            skipped += 1
            continue
        else:
            raise ConversionError(f"Éclairage inconnu : {label!r}")
        copies.append((parts, target))
    if not copies:
        raise ConversionError("Aucune image à copier.")
    if len({target for _, target in copies}) != len(copies):
        raise ConversionError("Plusieurs images produisent le même nom de destination.")
    return copies, skipped


def convert(input_path, output, use_previews):
    source = open_source(input_path)
    try:
        copies, skipped = plan(parse_descriptor(source.read_descriptor()), source, use_previews)
        if output.exists() and any(output.iterdir()):
            raise ConversionError(f"Le dossier de sortie existe déjà et n'est pas vide : {output}")
        for index, (parts, target) in enumerate(copies, start=1):
            destination = output / target
            destination.parent.mkdir(parents=True, exist_ok=True)
            source.copy(parts, destination)
            print(f"\r  {index}/{len(copies)} images", end="", flush=True)
        print()
    finally:
        source.close()
    poses = len({target.parts[1] for _, target in copies})
    print(f"Terminé : {poses} poses, {len(copies)} images, {skipped} images sans LED ignorées.")
    print(f"Dossier à ouvrir dans Meshroom : {output}")


# --- interface ------------------------------------------------------------------------------------------------------

def ask_path():
    print("Glissez ici l'archive du Nenuscanner (fichier .zip ou dossier), puis appuyez sur Entrée :")
    answer = input("> ").strip()
    if len(answer) >= 2 and answer[0] == answer[-1] and answer[0] in "'\"":
        answer = answer[1:-1]
    return Path(answer.replace("\\ ", " ") if sys.platform != "win32" else answer)


def ask_previews():
    print("Quelle résolution ?")
    print("  1 = rapide : aperçus JPEG réduits (conseillé pour l'atelier)")
    print("  2 = pleine résolution : fichiers NEF")
    return input("> ").strip() != "2"


def main():
    parser = argparse.ArgumentParser(description="Convertit une archive Nenuscanner en dossier pour Meshroom.")
    parser.add_argument("archive", nargs="?", type=Path, help="archive .zip ou dossier contenant descriptor.yaml")
    parser.add_argument("-o", "--output", type=Path, help="dossier de sortie (défaut : à côté de l'archive)")
    resolution = parser.add_mutually_exclusive_group()
    resolution.add_argument("--apercus", action="store_true", help="copier les aperçus JPEG réduits")
    resolution.add_argument("--nef", action="store_true", help="copier les NEF en pleine résolution")
    args = parser.parse_args()

    try:
        archive = (args.archive or ask_path()).expanduser().resolve()
        use_previews = args.apercus or (not args.nef and sys.stdin.isatty() and ask_previews())
        suffix = "_meshroom_rapide" if use_previews else "_meshroom"
        output = args.output or archive.with_name(archive.stem + suffix)
        convert(archive, output, use_previews)
    except (ConversionError, OSError, zipfile.BadZipFile) as exc:
        print(f"\nERREUR : {exc}")
        sys.exit(1)
    except (EOFError, KeyboardInterrupt):
        sys.exit(1)


if __name__ == "__main__":
    main()
