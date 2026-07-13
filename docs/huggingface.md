# Hugging Face Image Provider

`providers/huggingface_provider.py` génère des images via l'API Inference
officielle et gratuite de Hugging Face (https://api-inference.huggingface.co),
avec le modèle Flux (`black-forest-labs/FLUX.1-schnell`) par défaut — le
modèle de référence pour la génération d'images cité dans docs/SPEC.md
section 9. C'est un pont vers le futur provider "Flux Local" (voir
`tools/ComfyUI`, déjà installé mais sans modèle Flux téléchargé) : le jour où
ComfyUI sert Flux en local, seul `config/providers.yaml` change — aucune
modification d'`ImageService` ni des autres providers.

## Obtenir un token (gratuit)

1. Créer un compte gratuit sur https://huggingface.co (aucune carte
   bancaire requise pour un usage de base).
2. Générer un token en lecture sur https://huggingface.co/settings/tokens.

Le niveau gratuit est soumis à des quotas/limites de débit ; au-delà, ou
pour des modèles hébergés par des providers tiers premium, Hugging Face
peut proposer des offres payantes — ce provider n'utilise que le niveau
gratuit standard et ne configure rien de payant.

## Configurer le token localement (sans l'exposer)

Le token n'est **jamais** écrit dans le code ni dans `config/*.yaml`. Deux
façons de le fournir, par ordre de priorité dans
`HuggingFaceProvider._resolve_token()` :

1. **Variable d'environnement** (recommandé pour CI / production) :

   ```powershell
   $env:HF_TOKEN = "hf_xxx...xxx"
   ```

   (Session courante uniquement. Pour la rendre permanente sur Windows :
   `setx HF_TOKEN "hf_xxx...xxx"`, puis rouvrir le terminal.)

2. **Fichier `.env` local** (recommandé pour le développement) :

   ```bash
   cp .env.example .env
   # puis éditer .env et coller le token après HF_TOKEN=
   ```

   `.env` est listé dans `.gitignore` : il ne sera jamais commité. Seul
   `.env.example` (sans valeur réelle) fait partie du dépôt.

Si aucun token n'est trouvé, le provider lève une erreur explicite au lieu
d'échouer silencieusement, avec le lien pour en créer un.

## Utilisation

`image_provider: huggingface` dans `config/providers.yaml` active ce
provider pour tout le pipeline via `ProviderFactory` — `ImageService` n'a
besoin d'aucune modification (voir `services/image_service.py`).

Paramètres optionnels passés via `metadata` à `generate()` : `model`
(autre modèle HF text-to-image que le défaut Flux), `width`, `height`,
`negative_prompt`, `num_inference_steps`, `guidance_scale`, `timeout`,
`max_wait_for_cold_start` (attente sur un modèle en cold-start, HTTP 503).

## Démo / test

```bash
python core/huggingface_provider_demo.py
```

Génère une image pour le prompt de test, l'enregistre comme Asset, puis
revérifie tout le flux via `ImageService` (provider basculé uniquement via
un `ConfigManager` de démo, sans toucher au `config/providers.yaml`
partagé ni au code d'`ImageService`).
