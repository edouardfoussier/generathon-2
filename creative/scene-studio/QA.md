# Vérification — Atelier de scènes

27 septembre 2026.

## Données

- 20 plans du montage `refinement-v4` A, durée cumulée 76 s / 1 824 images.
- 20 miniatures 480×270 et 20 images 1280×720 prises aux mêmes frames.
- 20 extraits MP4 1280×720 / 24 fps / AAC 48 kHz stéréo, coupés aux images du montage ; les trois inserts recadrés et le carton restent présents.
- Les chemins des références et sources ont été vérifiés. Les prompts hérités sont conservés ; le carton éditorial n’a pas de prompt de génération inventé.

## Vérifications automatisées

- 7 tests du modèle frontend : insertion sans altérer l’original, ordre et intervalles sources, historique de direction, cadrage et déplacement reconnus, limitation au plan sélectionné, URLs/imports malformés et fusion de propositions 3D partielles.
- 15 tests backend : requêtes locales, Origin/Host, chemins, byte ranges, captures PNG, limites, fichiers de résultat réels, persistance/reprise, idempotence concurrente, schémas 3D et préservation du casting.
- Tous les imports JavaScript de Three.js et des contrôles/exporteur sont locaux et résolus. Syntaxe ESM vérifiée.

## Parcours dans le navigateur

Contrôlés dans le navigateur Codex avec les API CUA :

- Chargement des vingt plans et lecture des références.
- Maquettes grenier, basket, salsa, mariage, naissance, transmission et produit ; réglages et cadrages de caméra. Silhouette des chaussures affinée après inspection du dernier plan.
- Consigne « Rapproche la caméra de Luna, décale Luna à gauche et donne une lumière plus chaude » : trois changements reconnus, prompt augmenté, ancienne version conservée.
- Insertion d’un plan entre 1 et 2 : 21 plans, absence de faux rendu dans sa vue vidéo, puis retour aux vingt plans sources.
- Vue vidéo du basket : le vrai extrait local de sept secondes est chargé, à partir de zéro, au lieu du film complet.
- Enregistrement d’une demande image de test avec six références, durée et capture PNG réelle. Le statut reste `awaiting_mcp`, sans appel payant. Test clôturé explicitement ; aucun travail de génération ne reste en attente.
- Export GLB déclenché par l’interface et téléchargement démarré.
- Version bureau 1440×1000 et petit écran 390×844 : débordement de la fenêtre 3D corrigé ; largeur de document et viewport toutes deux 390 px.
- Aucune erreur JavaScript pendant les parcours. Le premier export GLB a signalé une orientation de lumière potentiellement perdue ; le correctif des cibles de lumière sur la copie exportée a été appliqué, puis l’export relancé sans nouvel avertissement.

Les scènes 3D sont des maquettes procédurales. Ce contrôle ne valide pas une reconstruction fidèle des visages ni la fidélité d’un futur rendu IA conditionné sur leur cadrage. Aucun nouveau rendu IA payant n’a été lancé pour ces tests.

## Extension lecture continue et assets

- 8 tests du modèle de piste : les 20 plans / 76 secondes, priorité des versions, plages sources, durées mesurées, cartons manquants, limites de recherche et changements d’ordre.
- 8 tests du modèle d’édition, dont l’isolation/restauration d’une référence ; 17 tests backend, dont ciblage d’asset et réutilisation du résultat image terminé. Tests HTTP exécutés avec ouverture de ports temporaires locaux autorisée.
- Navigation CUA : lecture du plan 3 jusqu’au plan 8 sans intervention, pause et recherche au plan 11 ; affichage 390×844 sans débordement horizontal (390 px / 390 px).
- Préparation via l’interface d’une variante de CS02G pour s01 uniquement : une référence, aucun cadrage 3D, statut awaiting_mcp. Test clôturé explicitement en failed, sans appel payant.
- Au lancement du dernier plan avec son : un seul élément vidéo actif et audible, le lecteur préchargé étant arrêté et muet.

## Atelier sans 3D par défaut et génération par lot

- 22 tests JavaScript du modèle, du montage et de la préparation des lots réussis. 29 tests Python backend réussis, avec bridge simulé : validations, deux workers, échecs partiels, idempotence, reprise des IDs connus et absence de resoumission en cas d’incertitude.
- Parcours navigateur sur un serveur isolé (8791), avec état temporaire et transport simulé : deux scènes cochées, consigne commune, durée 10s conservée et insert 2,5s annoncé à 4s, lot accepté puis navigation vers le basket pendant le traitement. Les deux jobs ont terminé avec le message explicite de simulation, sans appel fournisseur.
- Les demandes sauvegardées conservent le prompt de chaque scène et la note commune ; aucun cadrage 3D n’est joint par défaut. Le montage réel et les demandes de production ne sont pas touchés par le test.
- Au démarrage : onglet Vidéo sélectionné, lecteur chargé, zéro canvas 3D. L’option permet ensuite de charger le plateau 3D ; retour aux médias vérifié. Aucune erreur console détectée.
- La connexion réelle FAL est vérifiée en lecture seule ; ce contrôle de la fonctionnalité n’a lancé aucune génération payante supplémentaire.
