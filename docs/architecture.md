# Architecture — AI Video Studio

## 1. Objectif du projet

AI Video Studio est un pipeline de production vidéo automatisé assisté par
intelligence artificielle. Son objectif est de transformer une simple idée
ou un script textuel en une vidéo finalisée (images animées, voix off,
sous-titres, montage) sans intervention manuelle sur chaque étape technique.

Le projet vise à industrialiser la création de contenu vidéo (formats
verticaux pour les réseaux sociaux, formats horizontaux pour le web) en
combinant plusieurs briques technologiques : génération de texte, génération
d'images, animation, synthèse vocale, sous-titrage automatique et rendu vidéo
via Remotion.

## 2. Organisation des dossiers

```
ai-video-studio/
│
├── prompts/       # Prompts utilisés pour piloter les modèles IA (script, images, voix, etc.)
├── templates/      # Modèles réutilisables (structures de script, formats de scène, etc.)
├── assets/          # Ressources brutes et générées du projet
│   ├── images/       # Images générées ou importées
│   ├── videos/        # Clips vidéo bruts ou générés
│   ├── audio/           # Pistes audio diverses (voix, ambiances)
│   ├── music/             # Musiques de fond
│   └── sfx/                 # Effets sonores
├── scripts/         # Scripts de production (utilitaires, automatisation)
├── workflow/        # Définitions et étapes du pipeline de production
├── remotion/         # Projet Remotion pour le rendu vidéo final
├── output/            # Vidéos finales exportées
├── docs/                # Documentation du projet
├── config/              # Fichiers de configuration (ex. project_config.yaml)
├── logs/                  # Journaux d'exécution du pipeline
└── README.md
```

Chaque dossier correspond à une étape ou une responsabilité distincte du
pipeline, ce qui permet de faire évoluer chaque brique indépendamment sans
impacter les autres.

## 3. Workflow futur

Le pipeline de production suivra les étapes suivantes, dans l'ordre :

1. **Script** — génération ou rédaction du texte narratif de la vidéo.
2. **Storyboard** — découpage du script en scènes et description visuelle
   de chaque scène.
3. **Images** — génération des visuels correspondant à chaque scène du
   storyboard.
4. **Animation** — mise en mouvement des images (transitions, effets,
   animation de scène).
5. **Voix** — génération de la voix off à partir du script (synthèse
   vocale).
6. **Sous-titres** — génération et synchronisation automatique des
   sous-titres avec la voix.
7. **Remotion** — assemblage programmatique de l'ensemble des éléments
   (images animées, voix, sous-titres, musique) pour produire la vidéo.
8. **Export** — rendu final de la vidéo dans les formats définis
   (vertical, horizontal) et dépôt dans le dossier `output/`.

Chaque étape consomme les sorties de l'étape précédente et produit des
artefacts stockés dans les dossiers correspondants (`assets/`, `remotion/`,
`output/`), assurant une traçabilité complète de la production.

## 4. Rôle futur de Claude Code comme orchestrateur

Claude Code est destiné à jouer le rôle d'orchestrateur central du pipeline.
Il aura pour responsabilités :

- **Piloter l'enchaînement des étapes** du workflow (Script → Storyboard →
  Images → Animation → Voix → Sous-titres → Remotion → Export) en
  déclenchant les scripts et outils appropriés à chaque étape.
- **Générer et adapter les prompts** utilisés pour chaque brique IA
  (génération de texte, d'images, de voix) à partir des fichiers stockés
  dans `prompts/` et `templates/`.
- **Vérifier la cohérence des artefacts** produits à chaque étape avant de
  passer à la suivante (par exemple, s'assurer que le nombre d'images
  correspond au nombre de scènes du storyboard).
- **Gérer la configuration du projet** via `config/project_config.yaml`,
  en respectant les paramètres définis (résolution, formats, langue,
  étapes activées du workflow).
- **Journaliser l'exécution** du pipeline dans `logs/` afin de faciliter
  le suivi et le débogage.
- **Assembler le rendu final** avec Remotion et produire la vidéo exportée
  dans `output/`.

À terme, Claude Code agira comme le chef d'orchestre du studio, capable de
lancer une production vidéo de bout en bout à partir d'une simple demande,
en coordonnant les différents outils et modèles IA impliqués dans chaque
étape du workflow.
