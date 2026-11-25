# Installer les plugins dans Meshroom

Les méthodes de l'atelier sont des **plugins**. Meshroom les télécharge et les installe lui-même, depuis sa fenêtre
**Plugin Manager**. Les captures montrent l'installation de `mrEngravingSeg` ; les autres plugins s'installent de la même façon.

## 1. Ouvrir le Plugin Manager

Lancez Meshroom : **`meshroom.bat`** (Windows) ou `./meshroom.sh` (Linux).

![Page d'accueil de Meshroom](images/ui_accueil.png)

Cliquez sur **New Empty Project**, puis sur le bouton **Manage Plugins** (pièce de puzzle), en haut à droite.

![Bouton Manage Plugins](images/ui_manage_plugins.png)

## 2. Choisir un plugin

La liste montre les plugins déjà présents (`installed`) et ceux que l'on peut ajouter (`available`). Tapez un nom dans
**Search plugins** pour le retrouver, en respectant les majuscules (`Engraving`, pas `engraving`), puis cliquez sur
sa ligne : sa description s'affiche à droite.

![Liste des plugins](images/ui_plugin_list.png)

## 3. Installer

Cliquez sur **Install**, en bas à droite.

![Bouton Install](images/ui_plugin_install.png)

L'installation apparaît dans **Tasks**, avec une barre de progression en bas. Attendez la mention `done` avant de
passer au plugin suivant.

![Installation en cours](images/ui_plugin_running.png)

Installez ainsi les plugins de l'atelier :

| Plugin | Rôle |
| :-- | :-- |
| `mrSegmentation` | détourer l'objet (SAM 3) |
| `mrLedGetter` | stéréophotométrie calibrée |
| `mrLINOUniPS` | stéréophotométrie par apprentissage |
| `mrRNbNeuS2` | reconstruction 3D à partir des normales |
| `mrEngravingSeg` (facultatif) | repérer les gravures sur les cartes de normales |

`mrSegmentation` télécharge environ 16 Go de modèles : comptez une à deux heures selon la connexion.
`mrEngravingSeg` occupe environ 4,5 Go.

## 4. Redémarrer Meshroom

Quand la tâche affiche `done`, un bandeau bleu demande de redémarrer : cliquez sur **Restart Now**.

![Bandeau de redémarrage](images/ui_plugin_restart.png)

Plus tard, le bouton **Update** met un plugin à jour, et **Remove** le supprime.

Revenez ensuite au [guide principal](../README.md#3-installer-les-plugins-dans-meshroom) pour lancer `finaliser`.
