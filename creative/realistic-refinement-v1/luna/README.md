# Luna — inserts réalistes

Trois nouvelles propositions pour compléter la publicité réaliste existante. Les originaux et l’identité de Luna sont conservés. Images Nano Banana 2, vidéos Kling 3 Pro de cinq secondes, en 16:9. Ces prises sont des candidates à comparer, pas des choix approuvés par l’équipe.

- **RL01 — La photographie** : visage de Luna lisant la petite photo sortie du coffre ; à placer avant le laçage pour établir son regard et sa curiosité.
- **RL02 — Sa propre trace** : gros plan d’un unique petit trait orange sur la reprise crème de la chaussure. L’image générée place la pointe sur la reprise plutôt que juste à côté ; le prompt vidéo suit cette position réelle et laisse le logo intact.
- **RL03 — Son propre chemin** : une première poussée douce en skateboard dans la cour de la maison, puis une courte glisse. Grip noir uni sur le dessus, aucun dessin de planche inventé.

Références consultées : `creative/selection/assets/L01.png` (identité choisie), `creative/selection/assets/K01.png` (grenier ; accessoires funéraires exclus), `creative/model-comparison-v3/seedance25/videos/B13.mp4` (visage réaliste), `creative/model-comparison-v3/veo31/videos/B14A.mp4` (visage), `creative/model-comparison-v3/veo31/videos/B15.mp4` (chaussure et reprise). Les images extraites utiles sont dans `references/` ; les extractions ne modifient pas les sources.

Les prompts, identifiants de générations et références durables sont conservés dans le manifeste et `jobs/generation-log.json`. Aucun lien temporaire signé ni clé API n’est requis pour utiliser ces fichiers.

Incident d’envoi : la première demande d’image RL03 a été rejetée avant création de génération (`INVALID_REFERENCE_IMAGES`). Les références temporaires avaient été utilisées en parallèle. Un nouvel envoi avec référence fraîche a réussi ; il n’y a qu’une image RL03 générée.

## Résultats et vérification

Les trois vidéos sont générées et disponibles dans `videos/`. Chacune mesure 5,041667 s, 1 928 × 1 072 px, à 24 images/seconde ; une piste audio existe même si les prompts demandaient une performance silencieuse. À garder muette au prémontage si nécessaire ; l’écoute créative du son n’a pas été faite.

Contrôle visuel : planches de 15 images réparties sur chaque clip dans `qa/`, lecture technique complète et métadonnées FFprobe. RL01 garde un visage cohérent et un geste simple avec la photo. RL02 trace puis relève le marqueur ; le trait orange est plus large que prévu, sur environ la moitié supérieure de la reprise crème. RL03 réalise une poussée puis une glisse avec les deux pieds sur le deck. Les sources restent non coupées ; des plages de sélection purement éditoriales sont proposées dans le manifeste.

Coût confirmé dans les réponses Arcads : 16 crédits par image et 240 crédits par vidéo, soit **768 crédits** pour les trois paires image/vidéo.
