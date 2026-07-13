# ComfyUI (moteur de génération d'images local)

ComfyUI est installé comme outil externe, indépendant du reste du projet
AI VIDEO STUDIO. Cette étape installe uniquement ComfyUI lui-même — aucun
modèle (Flux Dev ou autre) n'est encore installé.

## Emplacement

```
tools/ComfyUI/          # dépôt officiel (clone GitHub, dernier commit)
tools/ComfyUI/venv/     # environnement virtuel Python dédié
```

Rien en dehors de `tools/ComfyUI/` n'est modifié : aucun fichier de
`core/`, `services/`, `providers/` ou `config/` n'a été touché.

## Prérequis vérifiés

* Python 3.11.9
* Git 2.45.2
* Pas de GPU NVIDIA détecté sur cette machine (carte AMD intégrée) →
  ComfyUI a été installé et démarré en **mode CPU** (`--cpu`). Les
  générations d'images réelles (une fois Flux installé) seront donc
  lentes ; un GPU NVIDIA + CUDA accélérerait fortement ComfyUI mais n'est
  pas requis pour cette étape.

## Démarrer ComfyUI

Depuis la racine du projet :

```bash
cd tools/ComfyUI
./venv/Scripts/python.exe main.py --cpu --listen 127.0.0.1 --port 8188
```

Une fois démarré, l'interface est accessible à l'adresse :

```
http://127.0.0.1:8188
```

(Retirer `--cpu` uniquement si un GPU NVIDIA + CUDA est installé sur la
machine.)

## Arrêter ComfyUI

* Dans le terminal où ComfyUI tourne : `Ctrl+C`.
* Ou, si lancé en arrière-plan, arrêter le processus Python correspondant
  (`tools/ComfyUI/venv/Scripts/python.exe main.py ...`) via le
  gestionnaire de tâches ou `Stop-Process`.

## Dépendances installées

Installées dans `tools/ComfyUI/venv/` uniquement (aucun impact sur
l'environnement Python global ni sur AI VIDEO STUDIO) :

* `torch`, `torchvision`, `torchaudio`, `torchsde` (build CPU,
  `--index-url https://download.pytorch.org/whl/cpu`)
* `numpy`, `scipy`, `Pillow`, `einops`
* `transformers`, `tokenizers`, `sentencepiece`, `safetensors`,
  `huggingface-hub`
* `aiohttp`, `yarl`, `requests`, `pyyaml`, `tqdm`, `psutil`
* `alembic`, `SQLAlchemy` (base de données interne des assets ComfyUI)
* `av`, `blake3`, `simpleeval`
* `comfyui-frontend-package`, `comfyui-workflow-templates`,
  `comfyui-embedded-docs`, `comfy-kitchen`, `comfy-aimdo`
* `pydantic`, `pydantic-settings` (requis par `server.py`, alors que
  `requirements.txt` les classe à tort comme "non essentielles")

Volontairement **non installées** (dépendances "non essentielles" du
`requirements.txt` officiel, seulement utilisées par des nœuds optionnels
comme l'upscaling ou le traitement d'image avancé) : `kornia`,
`spandrel`, `PyOpenGL`, `comfy-angle`. Leur absence n'empêche pas
ComfyUI de démarrer ; seuls quelques nœuds optionnels (`nodes_canny`,
`nodes_morphology`, `nodes_upscale_model`, ...) restent désactivés, ce
qui est signalé par des avertissements au démarrage sans bloquer le
serveur.

## Ce qui n'est pas fait à cette étape

* Aucun modèle (checkpoint) n'est installé — pas de Flux Dev, pas de
  workflow préconfiguré.
* Aucune intégration avec `providers/image_provider.py` n'a été faite ;
  `MockImageProvider` reste le seul provider actif tant que Flux n'est
  pas connecté.
