# Planche de sélection — Converse

80 références sur la planche au 26 septembre 2026 : **77 images et 3 vidéos**. Les images sont générées avec Nano Banana 2 dans Arcads ; les transitions vidéo avec Kling 3 Pro. Les 67 images des ateliers 01–05 comprennent : 6 enfants, 4 grands-pères, 4 paires, 3 greniers déclinés sous 2 lumières, une scène commune et huit styles graphiques, puis 13 tests issus des pistes de l’équipe et 8 tests de pixel art, matières hybrides et changement de style. L’atelier 05 ajoute 17 références réalistes autour de Luna, G01 et D06.

## Utilisation

Ouvrir `index.html` dans un navigateur en conservant `assets.js`, `i18n.js`, `board.js` et les dossiers `assets` et `references` à côté. La planche fonctionne aussi sur http://127.0.0.1:8765 tant que le serveur local est actif.

Le bouton **FR / EN** en haut à droite traduit toute la planche : filtres, descriptions, aperçus, sélection et exports. La langue est mémorisée. Ajouter `?lang=en` à l’URL ouvre directement la version anglaise. Les favoris existants sont conservés lors du changement de langue. Ils restent propres à l’adresse et au navigateur utilisés : la version fichier et la version localhost ont des sauvegardes distinctes.

Cliquer sur une image pour l’agrandir. Utiliser « Choisir » sur autant de propositions que souhaité, puis « Copier les codes » pour transmettre la sélection dans la conversation. Les favoris sont conservés dans ce navigateur ; ils ne sont pas envoyés automatiquement à Codex. L’export JSON permet aussi de conserver une sélection.

- E01–E06 : trois garçons et trois filles de 12–14 ans, casting fictif diversifié.
- G01–G04 : quatre grands-pères de 68–76 ans. Leur version jeune sera créée après le choix.
- P01–P04 : noir réparé, écru dessiné, rouge fané, marine délavé.
- D01/D02 : même grenier de campagne, lumière douce puis dorée.
- D03/D04 : même mansarde urbaine, ciel couvert puis fin de jour.
- D05/D06 : même grenier d’atelier, lumière latérale puis plus diffuse. La différence de température de couleur est modérée dans ce dernier couple.

## Styles graphiques

Le bouton « Explorer les nouveaux styles » ou le filtre « Styles graphiques » affiche la nouvelle série. S00 réunit provisoirement E04, P01 et D02. Cette combinaison et la photo de famille sont des supports de comparaison, pas des choix définitifs de casting. Chaque variante utilise exactement S00 comme référence et le même modèle ; les compositions restent proches, sans être garanties pixel pour pixel.

| Code | Style | Possibilité narrative à tester en animation |
|---|---|---|
| S00 | Scène photographique commune | Point de comparaison |
| S01 | Peinture à l’huile | Des touches de peinture révèlent progressivement le souvenir |
| S02 | BD / animation 2,5D inspirée de Spider-Verse | Les décalages d’encre accompagnent le passage d’une époque à l’autre |
| S03 | Toile tissée et broderie | Un fil sort de la réparation de la chaussure et tisse le passé |
| S04 | Album familial en papier découpé | Une couche de papier se soulève et révèle une autre époque |
| S05 | Risographie en trois encres | Les couches colorées se séparent puis se recomposent avec le mouvement |
| S06 | Fusain et aquarelle | La couleur se propage depuis les chaussures dans le présent monochrome |
| S07 | Cyanotype et lumière dorée | Le souvenir apparaît comme une photographie qui se développe |
| S08 | Miniature artisanale / stop-motion | Des gestes simples et des matières tangibles donnent vie aux objets |

S03 lie directement le style à la toile et aux coutures de Converse. S06 rend le retour de l’émotion très lisible. Ce sont deux pistes prioritaires pour un essai animé court après votre sélection. Les images seules ne valident ni la stabilité du style en vidéo, ni la qualité des transitions.

## Fichiers

`assets` contient les images originales, sans recadrage. `manifest.json` conserve les prompts, les références de génération, les identifiants et les coûts déclarés par Arcads. `style-generation-log.json` documente la série des styles. `assets.js` contient les informations bilingues des cartes ; `i18n.js` les traductions de l’interface ; `board.js` les interactions.

`team-generation-log.json` documente les 13 références du nouvel onglet et les essais remplacés. Le dossier créatif `../converse-team-directions-v3.md` propose un déroulé de 70 secondes et rassemble les points de cohérence ainsi que les sources historiques.

Arcads a déclaré 0 crédit facturé pour chacune des 20 images et l’utilisation du quota quotidien. Le solde affiché avant/après cette série est de 49 814 crédits. Cela ne préjuge pas du coût d’autres modèles ou générations futures.

La série de styles est également documentée à 0 crédit facturé dans son journal de génération : 10 générations pour 9 images retenues. S08 a été refait pour rendre l’argile et la feutrine plus lisibles ; le premier essai est conservé dans `assets/archive/S08-v1.png`, avec son historique dans `style-audit/S08.json`.

## Pistes de l’équipe / Team directions

Le sixième onglet contient 13 nouveaux tests, tous accompagnés de descriptions FR / EN :

- T01 : Luna découvre la boîte dans le grenier, image de référence pour les nouveaux styles.
- T02 / T05 : Rafa au basket en 1970 et Luna en skate en 2026, sur le même terrain. Les deux images sont placées côte à côte pour lire ce miroir.
- T03 : Rafa et Elena au bal en 1977.
- T04 : sa fille adolescente emprunte les Chucks en 1995.
- T06 : ouverture alternative au cimetière, Luna consultant son propre téléphone avant la découverte.
- T08 : fin autour des initiales R.M. et L.M.
- U01–U05 : noir et blanc graphique, 3D expressive, cinématique de jeu peinte, fable de bois peint et archives lumineuses de 2050. Tous utilisent T01 comme référence.
- T07 : concept alternatif en 2050, transmission humaine avec un robot utilitaire.

Pour arriver directement sur cet onglet, ajouter `?category=equipe` à l’URL, ou `?category=equipe&lang=en` pour l’anglais. Les mêmes fonctions d’agrandissement, de sélection et d’export sont disponibles.

Cette série a nécessité 16 générations pour 13 images retenues : T06 a été corrigée pour rendre le téléphone à Luna ; U03 et U05 ont été renforcées après un premier essai. Arcads indique 0 crédit facturé pour ces 16 générations. Le solde déclaré pour la série est de 49 814 crédits. Les images sont des tests de récit et de style : mains, initiales, usure de la paire, vieillissement et continuité en vidéo restent à verrouiller après votre sélection. Les observations propres à chaque image sont visibles dans ses notes.

## Pixel & hybrides / Pixel & hybrids

Le septième onglet ajoute huit images : **H01** pixel art, **H02** pixels et profondeur, **H03** visage sculpté et vêtements réalistes, **H04** ce mélange appliqué au skate, **H05** chaussures réalistes / Luna dessinée / charpente en carton, puis **X01–X03** trois étapes du passage du réel au dessin.

Accès direct : `?category=hybrides`, ou `?category=hybrides&lang=en` pour l’anglais. Les huit cartes sont bilingues, agrandissables, sélectionnables et exportables. Le passage FR/EN conserve les favoris déjà choisis.

La capture fournie et le lien Instagram sont conservés dans la section « Références à garder » et documentés dans `references/index.json`. Le Reel a été examiné sur des passages ; les observations sont distinguées des adaptations proposées. Il n’a pas été téléchargé et aucune action de sauvegarde n’a été faite sur le compte Instagram.

**X01–X03 sont des images fixes**, pas une vidéo. Le mouvement du pied, la fluidité et la stabilité du changement de matière restent à tester. Le dossier `../converse-style-switch-v4.md` propose une règle narrative et un essai de cinq secondes.

Cette série a nécessité 12 générations terminées pour 8 images retenues, plus deux appels rejetés à la validation des références. Les quatre versions remplacées sont conservées dans `assets/archive`. Arcads déclare **0 crédit facturé** pour les générations terminées. `hybrid-generation-log.json` conserve l’historique, les prompts et les coûts déclarés.

## Personnages & décors / Characters & locations

L’atelier 05 reprend les choix de l’équipe : **Luna conservée, visage G01 pour le grand-père, grenier D06 et style réaliste**. Accès direct : `?category=production` ou `?category=production&lang=en`.

- **L01–L05** : fiche de Luna face/dos/portrait, six expressions, transposition réaliste du dessin orange, fiche de cette tenue et intégration dans D06.
- **G11–G15** : grand-père dérivé de G01, à 72, 16, 23 et 41 ans environ, plus six expressions. Les jeunes versions restent des propositions ; G14 paraît un peu plus âgé.
- **R01–R07** : deux angles du grenier, terrain 1970 et son équivalent 2026, salle de salsa, salon familial et cimetière optionnel. Le tabouret renversé dans R01 et le petit fil dans R06 sont signalés pour correction avant les plans finaux.

La fiche de Luna comprend des repères d’identité, les deux tenues et une palette. La tenue aux accessoires orange et la personnalisation orange des chaussures restent des variantes à choisir. Les exemples de fiches fournis servent à organiser les vues, sans remplacer le visage de Luna.

`../luna-character-bible-v1.md` rassemble les références et points de continuité. `creative-choices.json` consigne les choix explicites. `character-location-generation-log.json` documente **21 générations, 17 images retenues, quatre premiers essais archivés et 0 crédit facturé déclaré**. Cet atelier contient uniquement des images fixes ; les premiers essais vidéo figurent dans l’atelier 06 ci-dessous.

## Dossier consolidé / Consolidated script

Le [découpage cinéma v2](../converse-cinematic-script-v2.md) est la proposition actuelle : 26 plans en 76 secondes, avec vocabulaire expliqué, gestes, cadrages, son et raccords détaillés. La [liste v2](../converse-shot-list-v2.csv) est la base de montage correspondante.

Le [dossier de production bilingue v1](../converse-production-bible-v1.md) conserve les choix, les alternatives, un script proposé de 75 secondes et les briefs des six images clés. La [liste CSV](../converse-shot-list-v1.csv) détaille les unités d’action et leurs dépendances. Il distingue les éléments choisis des propositions et présente désormais les six images clés générées et les trois essais de transition. Le film complet reste à produire. La nouvelle référence de chaussure ancienne est enregistrée dans `references/index.json` pour sa matière et sa patine, sans remplacer automatiquement la paire noire.

The [bilingual production bible](../converse-production-bible-v1.md) preserves the earlier working synthesis: a proposed 75-second script, selected and open choices, six generated keyframe candidates, three transition tests, and a production sequence. The [CSV shot list](../converse-shot-list-v1.csv) makes timing and dependencies editable. The old-shoe reference is for wear and materials, not an approved product replacement.

## Scènes & transitions / Scenes & transitions

L’atelier 06 (`?category=scenes`, ou `?category=scenes&lang=en`) contient **K01–K06**, les six premières images de scène, et **TR01–TR03**, les essais vidéo de passage du grenier au souvenir. Les lecteurs vidéo et leurs liens de téléchargement sont intégrés à la planche ; un seul clip joue à la fois. Les images et vidéos peuvent être choisies et exportées ensemble. Les favoris existants sont conservés.

Le montage libre est désormais confirmé pour Converse : l’équipe est exemptée de la contrainte de plan-séquence. Les six images sont des candidats réalistes, pas des références finales approuvées. Les écarts de produit, de props et de côté du geste sont indiqués sous chaque rendu. Les journaux `keyframes-luna-log.json`, `keyframes-memories-log.json` et `transition-generation-log.json` conservent les références exactes, tentatives, coûts et observations.

Workshop 06 contains six first scene candidates and three playable transition tests. Free editing is confirmed for Converse. Videos can be selected and exported like images; the existing favorites storage is preserved. Image zoom navigation excludes video entries, which have native inline players. Read the [transition comparison](../converse-transition-tests-v1.md) before choosing a technique.

## Grand-mère & maman / Grandma & Mom

L’atelier 07 ajoute **EL01–EL02 et M01–M02**, dans « Personnages & décors », section « Grand-mère & maman ». Les portraits de 2026 et les comparaisons entre âges développent les visages déjà présents dans K04 et K05. Ces quatre références sont des propositions de casting ; elles ne remplacent aucun choix validé de Luna ou du grand-père.

Le [dossier famille](../converse-family-casting-v1.md) explique la généalogie, les âges, les costumes et les intentions de jeu. Les journaux `grandma-generation-log.json` et `mom-generation-log.json` conservent les prompts, références, coûts et observations. Le [script v2](../converse-cinematic-script-v2.md) donne aux deux femmes une présence dans le présent, en complément de leurs souvenirs.

Workshop 07 adds four proposed family references under **Characters & locations → Grandma & Mom**. EL01/EL02 develop Elena at 71 and 22 from K04; M01/M02 develop the mother at 47 and 16 from K05. The [family notes](../converse-family-casting-v1.md) and [cinematic script v2](../converse-cinematic-script-v2.md) explain the relationships and proposed performance.

## Après le choix

1. Partir de Luna, G01 et D06 désormais retenus ; choisir la tenue et les versions jeunes du grand-père.
2. Fixer les identités, le vêtement du protagoniste et la version jeune du grand-père choisi.
3. Comparer les modèles sur une même scène, avec les mêmes références, cadrage et consigne. Commencer par un plan de découverte réunissant personnage, chaussures et grenier.
4. Juger le naturel des visages, la fidélité à la paire, la conservation du décor et la qualité de la lumière.
5. Harmoniser les six images clés K01–K06, choisir le raccord parmi TR01–TR03, puis animer les scènes retenues.

Ces images sont des études de casting, de patine et d’ambiance. Avant le film, corriger les détails de construction de la paire sélectionnée à partir d’une référence produit précise : notamment la réparation stylisée de P01 et les détails du patch/semelle. Les cadrages des portraits varient légèrement malgré une base commune ; la prochaine étape harmonisera les références retenues.

## English quick start

Open `index.html` with all its companion files. Click **EN** in the top-right corner, then **Scenes & transitions** for the six scene keyframes and three playable transition tests, **Characters & locations** for the character and location tests, including the four new Grandma & Mom references, **Pixel & hybrids** for the eight pixel, clay and style-switch tests, **Team directions** for the 13 story tests, or **Visual styles** for the earlier eight directions. The earlier X01–X03 style switch remains a still-image study. The new TR01–TR03 clips compare realistic present-to-memory transitions; the full ad has not been assembled. The supplied screenshot and Instagram reference are saved in Pixel & hybrids. Click any image to enlarge it, choose your favorites, then use **Copy the codes** to share your choices. Language changes preserve your selection. Favorites are stored locally in your browser; they are not automatically shared with teammates or Codex. The JSON download preserves a portable copy of your choices.
