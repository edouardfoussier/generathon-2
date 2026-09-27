# Luna & Rafa — Reprises réalistes

Cette page regroupe les nouveaux inserts et raccords à comparer avec le montage CapCut actuel. Elle conserve le style photographique réaliste et ne modifie ni les anciennes prises ni le montage original.

Ouvrir avec le serveur local :

http://127.0.0.1:8789/creative/realistic-refinement-v1/index.html

Le bouton FR / EN change les textes d’interface. Les observations et prompts restent dans leur langue source lorsqu’aucune traduction n’est fournie.

## Contenu

- `manifest.json` : manifeste de production, géré séparément. La page le relit toutes les 15 secondes si aucun média n’est en lecture. Les vidéos restent jouables pendant l’arrivée des autres prises.
- `audit.md` : analyse du montage exporté. Les quelque 33,43 secondes de noir après 58,20 secondes de récit doivent être retirées ; elles ne sont pas des scènes manquantes à produire.
- `reference-pack.json` : références réalistes, prompts exacts des prises sources et propositions de raccord.
- `prepare.py` : archive des seuls nouveaux fichiers présents et utilisables, avec noms numérotés, consignes, prompts et audit. Aucun transcodage, aucune génération ni copie du film CapCut.

Le manifeste utilise `assets`, une liste contenant `id`, `title`, `kind` (`image` ou `video`), `file`, et éventuellement `poster`, `placement`, `note`, `recommendation`, `prompt`, `imagePrompt`, `videoPrompt`, `model`. Les champs éditoriaux acceptent soit une chaîne soit `{ "fr": "…", "en": "…" }`. Les fichiers sont locaux à ce dossier. `usable: false` ou un statut `rejected`, `failed`, `pending`, `queued`, `running`, `generating`, `submission_unknown` exclut l’asset de l’archive.

## Préparer le ZIP pour l’équipe

Depuis la racine du dépôt :

```sh
python3 creative/realistic-refinement-v1/prepare.py
```

Le script crée `downloads/luna-rafa-realistic-inserts.zip` et `package.json`. Il vérifie les CRC de l’archive et conserve une empreinte SHA-256 de chaque média. Le ZIP contient `assets/`, `README.md`, `assets.json`, `prompts.json`, `audit.md`, ainsi que les deux documents de références lorsqu’ils existent. Les anciens films et caches de génération sont exclus.

Relancer la commande après l’arrivée de nouveaux assets. La page propose le dernier paquet disponible et indique quand il faut le reconstruire. Les fichiers du ZIP gardent leur format et leur durée d’origine ; les passages utiles restent à choisir dans CapCut.

Pub non officielle, exercice de hackathon. Signature visée au montage : **CONVERSE — Made by you.**

Les clips générés peuvent contenir des pistes audio non validées créativement : les couper dans CapCut avant le travail sur la bande-son. Les médias sources restent inchangés.
