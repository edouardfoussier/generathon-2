# Présent → souvenir / Present → memory

26 September 2026 · First motion comparison · Arcads / Kling 3 Pro

[Open the bilingual board](selection/index.html?category=scenes) · [Production bible](converse-production-bible-v1.md)

## Résultat

**TR02, le panoramique filé, est le meilleur point de départ de ce lot.** Le mouvement rapide masque le changement de décor et de tenue. TR03 propose une alternative plus douce. Pour TR01, une coupe précise réalisée au montage sera plus maîtrisable qu’une demande de coupe à l’intérieur d’une génération.

| Test | Intention | Résultat observé et suite |
|---|---|---|
| [TR01 — Raccord sur l’appui](selection/assets/TR01.mp4) | Le pied se pose dans le présent ; une coupe au même geste ouvre le souvenir. | La reprise retire le pantalon qui persistait sur le terrain. Le raccord reste précédé d’un bref mélange des décors ; ce n’est pas une coupe parfaitement nette. Refaire la coupe exacte au montage. |
| [TR02 — Panoramique filé](selection/assets/TR02.mp4) | Un mouvement horizontal rapide emporte le grenier et révèle le terrain. | Le flou masque assez bien le changement. C’est la technique générée la plus convaincante de la série. Harmoniser les chaussures des deux images d’ancrage avant le plan définitif. |
| [TR03 — Surimpression du souvenir](selection/assets/TR03.mp4) | Le terrain apparaît progressivement à travers le grenier. | La reprise ne montre plus le troisième pied mobile dans les images contrôlées. La superposition dédouble les silhouettes des chaussures : effet de mémoire doux, moins précis pour présenter le produit. |

Les trois clips utilisent les mêmes [image de départ](selection/assets/TRS01.png) et [image d’arrivée](selection/assets/TRS02.png), créées pour cette comparaison au niveau des chaussures. Ces images de raccord sont distinctes des six images de récit K01–K06. Elles diffèrent légèrement par le côté visible et l’écusson de la chaussure ; cette continuité reste à corriger. **Ces tests comparent des techniques, ce ne sont pas des plans finaux.**

Chaque fichier mesure **6,041667 secondes**, **1928 × 1072**, **24 images/s**, avec une piste audio AAC. Le contrôle repose sur les métadonnées et des images extraites localement, dont des échantillons plus rapprochés autour de TR01. Le son n’a pas été écouté intégralement. Une analyse Arcads multi-fichiers a confondu les durées ; ses indications de minutage n’ont pas été retenues.

## Coût et concurrence

- Six images de scène : neuf générations avec trois reprises, **0 crédit déclaré**.
- Deux images d’ancrage et une analyse complémentaire : **0 crédit déclaré**.
- Trois essais vidéo et deux reprises : **5 × 272 = 1 360 crédits**.
- Solde Arcads constaté : **49 814 → 48 454 crédits**. Le compteur agrégé de dépense MCP affiché par l’outil demeure à zéro pour la période qu’il retourne ; les coûts individuels et la variation de solde concordent, et servent ici au bilan du lot.

Trois demandes vidéo indépendantes ont été soumises ensemble et acceptées sans refus, puis deux reprises ensemble. La limite maximale du compte n’est pas exposée par les outils ; **10 variantes par appel n’équivaut pas à 10 rendus simultanés garantis**. La [documentation MCP officielle](https://intercom.help/arcads/en/articles/15655699-arcads-mcp) consultée ne donne pas de plafond chiffré. Les [conditions Arcads](https://www.arcads.ai/terms) évoquent séparément un seuil de 40 requêtes API par seconde ; il ne mesure pas la concurrence des générations.

Le montage libre pour Converse a été confirmé par l’équipe. Les raccords masqués sont donc un choix esthétique, pas une obligation. Pour la prochaine étape, choisir une technique, harmoniser les deux chaussures d’ancrage, puis tester le raccord sur les plans réellement retenus.

## English team notes

**TR02, the whip pan, is the strongest generated starting point in this batch.** The rapid horizontal movement hides the location and wardrobe change. TR03 is softer and more nostalgic. For TR01, make the precise match cut in the edit rather than relying on the generator to produce a perfectly clean cut.

| Test | Observed result |
|---|---|
| TR01 — footfall match cut | The retry removes the trousers persisting in the memory. A faint blend still precedes the cut. Make the exact cut in the edit. |
| TR02 — whip pan | Horizontal blur masks the period change convincingly. Best method to develop further. |
| TR03 — memory double exposure | Progressive photographic dissolve; no extra moving third foot in inspected retry frames. Overlapping shoe silhouettes make it less precise for a product close-up. |

All three use the same dedicated start/end images, TRS01/TRS02. These differ slightly in visible shoe side and badge placement and need correction before final footage. **This is a technique comparison, not final approved footage.** The source plates are separate from story keyframes K01–K06.

Each clip is 6.041667 seconds, 1928 × 1072, 24 fps, with an AAC audio track. QA used metadata and sampled local frames, including closer sampling around TR01’s cut. Full audio was not independently listened to. Supplementary multi-file analysis confused the clip timings, so those timings were discarded.

The batch cost **1,360 credits**: five videos at 272 each; eleven image generations and one analysis were reported at zero. The observed workspace balance changed from 49,814 to 48,454. Three video submissions were accepted together without rate-limit errors; this establishes observed submission behavior, not the service’s maximum concurrency. Tools allow 1–10 variants per call, while the official MCP page provides no numeric concurrent-render limit. The separate API request-rate threshold is not a render-concurrency limit.

Free editing is confirmed for Converse. Choose a technique, align the product references, then apply it to the selected scene footage.

## Files and provenance

- [Transition generation log](selection/transition-generation-log.json): exact prompts, source paths, IDs, attempts, timing, charges and QA. Entries marked `selected:true` identify retained renders, not team-approved final footage.
- [Luna keyframe log](selection/keyframes-luna-log.json), [memory keyframe log](selection/keyframes-memories-log.json): nine completed image generations for the six scene candidates.
- Original TR01/TR03 attempts and replaced keyframes remain in `selection/assets/archive/`.
- Local MP4s and poster JPGs are integrated into the board. No signed download credentials are stored in the repository.
