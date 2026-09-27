# Luna & Rafa — Atelier de scènes

Une nouvelle page du site Converse pour préparer le film scène par scène, avec vingt plans issus du montage `refinement-v4` de 76 secondes. Accès ajouté à la planche de sélection et à la page Raffinements.

```sh
python3 creative/scene-studio/server.py serve --port 8789
```

Ouvrir **http://127.0.0.1:8789/studio**. Le serveur reste local à cet ordinateur. Aucune installation de package n’est nécessaire : Python 3.10+ et Three.js 0.180.0 embarqué dans `vendor/`. Les anciennes pages et médias restent accessibles depuis le même serveur sous `/creative/`.

## Ce qui fonctionne

- Images et vidéos visibles par défaut. Les outils 3D sont masqués, conservés derrière une option et chargés seulement à leur ouverture.
- Vingt maquettes 3D optionnelles de mise en scène : grenier, basket, salsa, mariage, chambre du bébé, transmission et produit. Géométrie procédurale, personnages articulés simplifiés, caméra orbitale et cadrages prédéfinis.
- Références exactes utilisées pour les générations existantes : personnages, lieux et chaussures, avec aperçu agrandi.
- Images du dernier montage en 1280×720 ; vingt extraits vidéo autonomes du montage V4 A, avec son, recadrages et carton final. Leurs 1 824 images totalisent 76 secondes.
- Modification du prompt, conservation de l’historique et restauration. Les consignes courantes de caméra, température, intensité et déplacement gauche/droite sont interprétées localement ; les indications non reconnues restent des notes destinées au rendu IA, sans prétendre modifier la géométrie.
- Insertion entre deux plans, duplication, déplacement dans le récit et réglage de durée. Un nouveau plan n’a aucun faux rendu.
- Sauvegarde locale au navigateur, export/import JSON. La restauration du montage source exporte d’abord le brouillon en cours.
- Capture PNG du cadrage 3D et export GLB de la maquette en pose statique. L’animation interactive sert à la prévisualisation et n’est pas un clip IA généré.
- Demandes image, vidéo ou interprétation 3D avancée enregistrées avec prompt, durée, références et capture de cadrage. Résultats réels importables et consultables séparément de l’original.

## Lecture du montage et variantes d’assets

La piste fixe en bas lit les vidéos dans l’ordre du récit : lecture/pause, précédent/suivant, recherche globale, son et boucle. L’onglet Montage affiche le plan lu ; la sélection de travail dans l’inspecteur reste distincte. La version vidéo choisie est prioritaire, puis l’extrait monté, puis la source. La durée réelle du média prime sur la durée cible d’une future génération. Deux lecteurs alternent et préchargent le plan suivant ; cet aperçu navigateur peut subir des délais de décodage et ne remplace pas un export final à l’image près. Un plan sans rendu conserve un carton à sa durée cible.

Cliquer une référence ouvre son image et un champ pour préparer une variante de cet asset seul. La demande contient `target: {kind: "reference", id, scope: "scene"}`. Après import du résultat réel, « Utiliser cette référence » remplace cette image uniquement dans le plan ; l’original reste restaurable. Les vidéos déjà rendues et les objets 3D ne sont pas modifiés par ce remplacement d’image. Les assets déjà générés peuvent servir de référence à une demande suivante.

## Variantes de plusieurs scènes

Cocher jusqu’à six plans dans la liste de gauche puis ouvrir la génération par lot. Une consigne commune est ajoutée à la demande de chaque plan, avec son propre contexte. Les prompts sources, références et prises choisies ne sont pas remplacés par la préparation du lot.

Le mode **FAL** utilise la connexion déjà configurée du Cut Room (`127.0.0.1:8787`). L’Atelier (`127.0.0.1:8789`) envoie les demandes à ce serveur local ; aucune clé API n’est transmise au navigateur ou copiée dans les projets. Les deux serveurs doivent rester ouverts et l’ordinateur éveillé. Une fois le lot accepté, fermer le dialogue, changer de scène ou fermer l’onglet n’interrompt pas le suivi côté serveur.

Le Cut Room autorise deux traitements simultanés pour l’ensemble de ses demandes ; les autres attendent. Ce réglage local n’est pas la limite annoncée du compte FAL. Le clic de lancement en mode FAL utilise des crédits. Les durées proposées dépendent du modèle et sont présentées avant l’envoi ; une durée de génération différente ne modifie pas automatiquement le montage.

Cette première connexion FAL guide chaque prise avec **une image de départ** du plan. Les autres feuilles de personnage et décor restent conservées dans la demande de travail, mais ne sont pas toutes envoyées au modèle. Pour une composition ou une identité différente, préparer une nouvelle image clé puis l’animer reste préférable.

Les statuts de chaque scène sont indépendants. Les résultats deviennent des variantes consultables dans « Versions & générations » : il faut les choisir pour les intégrer. Un refus ou une soumission incertaine ne relance pas automatiquement une génération payante. Au redémarrage, les demandes dont l’identifiant est connu reprennent leur suivi.

## Génération : mode MCP de conversation

En mode **MCP**, les boutons **préparent une demande persistante** ; ils ne lancent pas un modèle depuis le navigateur. Le statut le dit explicitement. Copier la demande affichée dans cette conversation permet de la traiter avec les outils Higgsfield déjà connectés, puis d’importer le résultat dans l’atelier. Le backend n’extrait pas les identifiants du connecteur et ne démarre pas un agent en arrière-plan.

Le mode Higgsfield MCP reste exécuté depuis la conversation, y compris pour un lot. Il n’est pas la connexion FAL autonome décrite plus haut. L’API Higgsfield dispose de son propre compte et de sa propre facturation : [documentation officielle de l’offre API](https://higgsfield.ai/blog/generate-ai-videos-higgsfield-api).

Aucun crédit de génération n’a été utilisé pour construire ou tester cet atelier. Les tests de file sont distincts de véritables générations et restent signalés comme tels.

Le fichier canonique d’une demande est `creative/scene-studio/.state/jobs/<id>/request.json`. Lire le [contrat backend](README-backend.md) pour enregistrer le démarrage, importer le vrai fichier image/vidéo/JSON et publier le résultat. Le navigateur actualise la file toutes les douze secondes lorsqu’il est visible.

## Rôle de la 3D

La 3D est optionnelle et masquée par défaut. Il s’agit d’une prévisualisation éditable, pas d’une reconstruction fidèle des personnes à partir des références. Elle permet de régler instantanément l’espace, les angles, les distances et l’éclairage sans génération payante. Le rendu IA reçoit son cadrage comme guide de composition et les références pour l’identité, la tenue, le produit et la gouache. Les gains de fidélité du rendu final ne sont pas établis par un benchmark dans ce projet.

## Données et vérification

[README-data.md](README-data.md) décrit le découpage, les générations originales, les trois inserts recadrés, les frames et les extraits montés. Les prompts sources longs sont conservés ; la demande de régénération les restreint explicitement au seul plan sélectionné.

```sh
node --test creative/scene-studio/*test.mjs
python3 -m unittest discover -s creative/scene-studio -p 'test*.py'
```

Les tests couvrent le découpage, l’isolation des variantes, la restauration, la limitation du prompt au plan, les imports malformés, les propositions 3D partielles, les chemins, les captures, les reprises de serveur et les requêtes dupliquées. Les vérifications visuelles et de parcours sont consignées dans `QA.md`.
