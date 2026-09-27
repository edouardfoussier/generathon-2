# Selection CapCut — 27 septembre 2026

`selection.json` fixe les 20 prises et l’ordre demandé dans les 19 captures
de l’équipe. La capture avec S13 et S15 ajoute deux prises, de gauche à droite.
Les deux B07B sont conservés ; la dernière prise est V25, pas V25R1.

Recréer le ZIP depuis la racine du dépôt :

```sh
python3 creative/capcut-handoff/prepare.py
```

Le script conserve les fichiers originaux octet pour octet, vérifie leurs
SHA-256 après archivage et produit une page de téléchargement, un récapitulatif
FR/EN et une liste CSV. Les vidéos sont numérotées de 01 à 20 dans `clips/`.
L’archive générée (~167 Mo) est ignorée par Git ; les sources restent suivies
dans leurs collections d’origine. Aucun crédit de génération n’est utilisé.

Page locale : `http://127.0.0.1:8789/creative/capcut-handoff/index.html`.
Dézipper, importer les MP4 et trier par nom croissant avant de les placer sur
la piste. Les prises complètes totalisent 114,625 secondes et restent à monter.
