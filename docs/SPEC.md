# AI VIDEO STUDIO — Spécification Technique (SPEC.md)

Ce document est la référence technique officielle du projet **AI Video
Studio**. Il décrit la vision, l'architecture, le pipeline de production et
les composants du système. Il est destiné à être lu et exploité aussi bien
par un développeur humain que par un agent IA travaillant sur le projet.

---

## 1. Vision du projet

AI Video Studio est un système professionnel de génération vidéo assistée
par intelligence artificielle. Son objectif est de transformer une simple
idée, un sujet ou une consigne en une vidéo finalisée — script, visuels,
voix, sous-titres et montage — en automatisant l'intégralité de la chaîne
de production, du brief initial jusqu'au fichier vidéo exporté.

Le projet est conçu comme une infrastructure de studio, pas comme un outil
ponctuel : il doit pouvoir produire un volume important de vidéos de
formats et de styles différents, de façon répétable, traçable et
extensible, en s'appuyant en priorité sur des outils gratuits et open
source.

## 2. Objectifs

AI Video Studio vise à offrir les capacités suivantes :

- Générer un script et un storyboard à partir d'un simple sujet.
- Produire les visuels nécessaires (images, animations) pour chaque scène.
- Générer une voix off synthétique dans plusieurs langues.
- Générer et synchroniser automatiquement les sous-titres.
- Assembler et rendre la vidéo finale via un moteur de rendu
  programmatique (Remotion).
- Supporter plusieurs formats et résolutions de sortie, jusqu'à la 4K.
- Orchestrer l'ensemble du pipeline de façon fiable, avec suivi d'état et
  reprise après erreur.
- Rester modulaire : chaque étape (script, image, voix, sous-titres,
  rendu) doit pouvoir évoluer ou être remplacée indépendamment des autres.
- Privilégier des solutions gratuites et open source à chaque fois que
  c'est possible.

## 3. Types de vidéos supportées

Le système est conçu pour produire les catégories de vidéos suivantes :

- **YouTube** — vidéos longues, format horizontal.
- **TikTok** — vidéos courtes, format vertical.
- **Shorts** — formats courts verticaux (YouTube Shorts, Reels).
- **Ads** — publicités courtes orientées conversion.
- **UGC** — vidéos imitant le contenu généré par les utilisateurs.
- **Product Demo** — démonstrations de produits.
- **Documentary** — documentaires narratifs de type cinématographique.
- **Training** — vidéos de formation et contenus pédagogiques.

Chaque type de vidéo correspond à un **template** (voir `templates/`)
définissant sa structure narrative type (sections, durées, style).

## 4. Formats vidéo

Le système supporte les formats de cadrage suivants :

- **Horizontal 16:9** — YouTube, documentaires, formations.
- **Vertical 9:16** — TikTok, Shorts, Reels.
- **Carré 1:1** — publicités et contenus multi-plateformes.

Résolutions supportées, jusqu'à un maximum de **4K (3840×2160)** :

| Résolution | Dimensions horizontales | Dimensions verticales |
|------------|--------------------------|-------------------------|
| HD         | 1280×720                | 720×1280                |
| Full HD    | 1920×1080               | 1080×1920                |
| 4K         | 3840×2160               | 2160×3840                |

Le format et la résolution d'une vidéo sont définis dans le
`scene_schema.json` du projet (`project.format`, `project.resolution`) et
pilotent directement les dimensions de la composition Remotion.

## 5. Sources média

Les médias utilisés dans une production peuvent provenir de trois sources :

- **Médias utilisateur** — images, vidéos, voix ou musiques fournies
  directement par l'utilisateur dans `assets/`.
- **Génération IA** — visuels, animations, voix et sous-titres produits
  par des providers IA (voir section 9) à partir du storyboard.
- **Assets libres** — ressources libres de droits (images, musiques,
  effets sonores) utilisées en complément, notamment pendant les phases où
  aucun provider IA n'est encore connecté.

Le Scene Engine ne distingue pas la provenance d'un média : chaque scène
référence simplement un chemin de fichier (`media.path`) dans `assets/`,
quelle que soit son origine.

## 6. Architecture générale

L'architecture générale du système suit le flux suivant :

```
User
  ↓
Project
  ↓
Specification
  ↓
Orchestrator
  ↓
Job System
  ↓
Services
  ↓
Providers
  ↓
IA Tools
  ↓
Remotion
  ↓
Export
```

- **User** — exprime une intention (sujet, brief, campagne).
- **Project** — regroupe une ou plusieurs vidéos sous un même contexte
  (voir section 11).
- **Specification** — la description structurée de la vidéo à produire
  (template, format, résolution, contraintes).
- **Orchestrator** — pilote l'exécution du pipeline dans l'ordre officiel
  (`core/orchestrator.py`, `core/pipeline.py`).
- **Job System** — encapsule chaque unité de travail en `Job`, avec
  statut, historique et file d'attente (`core/jobs/`).
- **Services** — couches métier qui exposent une capacité fonctionnelle
  (script, image, animation, voix, sous-titres, rendu) indépendamment du
  provider utilisé (`services/`).
- **Providers** — implémentations concrètes s'appuyant sur des outils ou
  modèles IA spécifiques (`providers/`), interchangeables entre eux.
- **IA Tools** — les modèles/outils réels invoqués par les providers
  (génération d'image, de voix, de sous-titres...).
- **Remotion** — moteur de rendu programmatique qui assemble les scènes en
  vidéo (`remotion/`).
- **Export** — production du fichier final dans `output/`.

## 7. Pipeline

Le pipeline de production d'une vidéo suit les étapes suivantes, dans cet
ordre :

```
Input
  → Analysis
  → Script
  → Storyboard
  → Assets
  → Voice
  → Animation
  → Subtitles
  → Render
  → Export
```

- **Input** — le sujet ou brief fourni par l'utilisateur.
- **Analysis** — interprétation du besoin (type de vidéo, ton, cible,
  contraintes) pour sélectionner le template approprié.
- **Script** — génération du texte narratif (`scripts/generator/`).
- **Storyboard** — découpage du script en scènes, converti au format
  standard du moteur (`scripts/converter/` → `workflow/scene_schema.json`).
- **Assets** — génération ou sélection des visuels associés à chaque
  scène.
- **Voice** — synthèse de la voix off à partir du texte de chaque scène.
- **Animation** — mise en mouvement des visuels (transitions, effets).
- **Subtitles** — génération et synchronisation des sous-titres avec la
  voix.
- **Render** — assemblage complet de la vidéo via Remotion
  (`remotion/src/compositions/DynamicVideo.tsx`).
- **Export** — écriture du fichier vidéo final dans `output/`.

Ce pipeline est déclaré de façon explicite et extensible dans
`core/pipeline.py`, et chaque étape correspond à un module dans
`core/modules.py`.

## 8. Modules

Chaque étape fonctionnelle du pipeline est exposée sous forme de service,
indépendant de l'implémentation IA sous-jacente :

- **Script Service** — génère le texte narratif d'une vidéo à partir d'un
  sujet et d'un template.
- **Image Service** — génère ou sélectionne les visuels de chaque scène.
- **Animation Service** — anime les visuels (mouvement, transitions).
- **Voice Service** — synthétise la voix off à partir du texte des scènes.
- **Subtitle Service** — génère et synchronise les sous-titres avec la
  piste audio.
- **Render Service** — pilote Remotion pour assembler et exporter la
  vidéo finale.

Chaque service définit une interface stable ; son implémentation peut
déléguer à un ou plusieurs providers, sans que l'Orchestrator ou le Job
System n'aient à connaître le détail de cette implémentation.

## 9. Providers

Les providers sont les intégrations concrètes des outils et modèles IA.
Les providers de référence identifiés pour le projet sont :

- **Flux** — génération d'images.
- **Wan** — génération vidéo / animation.
- **Kokoro** — synthèse vocale (voix).
- **Whisper** — transcription et génération de sous-titres.
- **Remotion** — moteur de rendu et d'export vidéo.

Chaque provider implémente l'interface du service qu'il sert (Image,
Animation, Voice, Subtitle, Render). Les providers sont **interchangeables** :
un service peut être reconfiguré pour utiliser un provider différent sans
impacter l'Orchestrator, le Job System ni le reste du pipeline.

## 10. Philosophie Open Source

**Règle du projet : les solutions gratuites et open source sont
prioritaires.**

À capacité équivalente, tout choix de provider, de librairie ou d'outil
doit privilégier une solution gratuite et open source plutôt qu'une
solution propriétaire ou payante. Les services payants ne sont envisagés
que lorsqu'aucune alternative open source ne répond au besoin.

## 11. Projects

Un **Project** regroupe une ou plusieurs vidéos partageant un même
contexte : une campagne publicitaire, une série de vidéos de formation, ou
l'ensemble des publications d'une chaîne. Un Project porte :

- une identité commune (nom, style, ton, charte visuelle) ;
- un ou plusieurs templates de référence (`templates/`) ;
- l'historique des vidéos produites et de leurs statuts ;
- les paramètres par défaut (format, résolution, langue) hérités par
  chaque vidéo du projet, sauf surcharge explicite.

Cette notion permet de gérer des campagnes ou des séries complètes plutôt
que des vidéos isolées, en réutilisant configuration et styles communs.

## 12. Jobs

Chaque unité de travail du pipeline (génération de script, rendu vidéo...)
est représentée par un **Job**, géré par le Job System (`core/jobs/`).

- **États** — un Job transite entre `PENDING`, `RUNNING`, `COMPLETED` et
  `FAILED` (`core/jobs/status.py`).
- **Progression** — chaque changement d'état est publié comme événement
  via l'`EventBus` (`core/jobs/events.py`), permettant un suivi en temps
  réel de l'avancement.
- **Logs** — chaque Job conserve un historique horodaté complet de ses
  transitions (`core/jobs/job.py`), consultable après exécution.
- **Reprise après erreur** — un Job en échec (`FAILED`) conserve son
  contexte (payload, erreur, historique), ce qui permet de le relancer ou
  de le rejouer sans perdre l'information produite par les étapes
  précédentes du pipeline.

## 13. Évolution future

Les axes d'évolution envisagés pour AI Video Studio incluent :

- **SaaS possible** — exposer le système comme un service multi-utilisateur
  hébergé, avec gestion de comptes et de quotas.
- **Interface web** — une interface graphique permettant de créer,
  suivre et éditer des projets et des vidéos sans passer par la ligne de
  commande.
- **Génération multi-vidéos** — production en lot de plusieurs vidéos à
  partir d'un même Project (séries, déclinaisons de formats).
- **Plugins** — mécanisme d'extension permettant d'ajouter de nouveaux
  services ou providers (nouveaux styles, nouveaux modèles IA, nouvelles
  plateformes de publication) sans modifier le cœur du système.
