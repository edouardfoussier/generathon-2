# Converse — audit du scénario et du rythme

27 September 2026 · Working proposal, not a replacement for approved FG01

## Ce que nous avons retrouvé / What we found

**Le script v2 existe et a été exploité.** Il décrit 26 plans sur 76 secondes : action, cadre, focale indicative, mouvement, son, raccord, références et priorité de production. L’animatique v1 l’a effectivement utilisé : 21 plans issus de vidéos générées et cinq inserts fixes. Sources : [script v2](../converse-cinematic-script-v2.md), [26-plan source map](../animatic-v1/edit/timeline.json), [animatic production record](../animatic-v1/README.md).

Le [script v3](../converse-cinematic-script-v3.md) est ensuite une **réécriture demandée par l’équipe**, et pas un simple résumé du v2. Il introduit l’appel pour les vêtements d’hiver, l’agacement de Luna, le téléphone, le panier, le mariage et le bébé. La dernière vidéo [FG01](../gpt-full-film-v1/renders/converse-gpt-seedance25-full-76s.mp4) suit ce récit v3, avec son ouverture de 30 secondes conservée puis six nouvelles générations. Sept fichiers vidéo ne signifient pas sept plans : chaque génération contient déjà plusieurs coupes internes.

**EN.** V2 was produced as the first 26-shot animatic. V3 deliberately changed the story at the team’s request. FG01 follows v3. What became less explicit was v2’s shot-by-shot craft: precise reaction coverage, sound bridges, object inserts and matched eyelines. Restore that craft inside the current attic story; do not restore the superseded story automatically.

## Les écarts utiles à corriger / Useful gaps

| Intention | État documenté dans FG01 | Action proposée |
|---|---|---|
| Téléphone intégré au récit | Insert graphique plein écran de 15 à 22 s, composé dans `continuity-video-v1/prepare_edit.py`. | Conserver Luna, la photo et le coffre dans l’image. La voir photographier, interroger, puis revenir à l’objet. |
| Voix de Maman avant le retour | Le retour visuel commence à 61 s ; la voix actuelle commence à 62,9 s. Le pont sonore prévu en v3 n’est donc pas réalisé à cette jonction. | Faire commencer « Luna? Are you coming down? » vers 60,2 s, encore sur le souvenir. Ajuster au débit réel de la prise. |
| Reconnaissance mère adolescente / adulte | V2 S19→S20 prescrivait même taille de visage, même place des yeux, même sourire. FG01 revient d’abord à Luna, puis à la photo, puis à Maman. | Tester un bref raccord du sourire de la fille de Rafa à celui de Maman aujourd’hui. Il faut deux cadres compatibles ; un recadrage ne suffit pas toujours. |
| Rythme matière / corps / visage | Ces éléments sont dans les prompts, mais groupés dans des générations de 4–11 s et dans une ouverture de 30 s. | Choisir les meilleurs gestes au montage, puis couvrir seulement les détails manquants : photo, œillet/lacet, contact de main, réaction. |
| Son de matière comme moteur | Le montage reprend la musique et les voix v3. Les pistes natives sont retirées ; pas de Foley dédié documenté dans ce mix. | Ajouter un petit vocabulaire sonore : carton, déclencheur, lacet, appui, rebond, semelle, souffle. Éviter de remplir chaque image. |
| Peinture uniforme | Le prompt commun demande notamment « detailed painted faces » et une identité précise à partir des planches. | Comparer une consigne de matière plus précise, puis une référence réellement repeinte. Les visages doivent partager la même simplification, les mêmes pigments et les mêmes contours que les vêtements et le décor. |

Attention aux axes : v2 plaçait Maman à gauche de Luna, tandis que le prompt de retour FG01 la situe à la porte à droite. Récupérer le principe de raccord de regard, pas ces coordonnées contradictoires. Ne pas retourner l’image, ce qui inverserait aussi la réparation de la chaussure.

## Référence Converse réellement examinée

Source : [MAKE. MOVE. REPEAT. — chaîne officielle Converse](https://www.youtube.com/watch?v=TYwrNRF9u-M). La page affiche la chaîne vérifiée et une vidéo de 30 secondes ; le lecteur indique environ 30,34 s. Description observée : campagne pour les Chuck Taylor et Double Stack Chucks.

**Méthode et limite :** page ouverte dans le navigateur, lecture lancée puis examen visuel d’images réparties de 0 à 27 s, avec contrôles du lecteur. Cette analyse porte sur les images et les effets visibles. Le son n’a pas été écouté de façon fiable ; aucun BPM, morceau ou raccord exact sur une percussion n’est affirmé. Les temps ci-dessous sont approximatifs, pas un relevé de toutes les coupes.

| Temps observé | Ce qui est visible | Traduction possible pour notre film |
|---|---|---|
| Début | Contre-plongée très basse, corps et chaussures dominants, ciel en arrière-plan. | Un point de vue au ras du parquet pour l’appui décisif de Luna. |
| ~3 s | Gros plan mobile d’une passante avec casque ; rue étirée autour d’elle. | Garder le visage lisible, laisser la couleur du décor s’étirer pendant le passage au souvenir. |
| ~6 s | Gros plan de Converse sur une planche de skate ; caméra inclinée et matière en mouvement. | Le produit agit : lacet tendu, semelle qui prend appui, pivot. Éviter la chaussure uniquement montrée comme objet immobile. |
| ~8–9 s | Décomposition / répétition du mouvement d’un corps dans le déplacement urbain. | Deux ou trois contours dessinés retardés autour d’un pied, pendant quelques images seulement. |
| ~12 s | Café projeté au premier plan, perspective très proche, angle incliné. | Une poussière ou un coup de pinceau passe devant l’objectif et motive une coupe. Ne pas importer le gag du café dans notre récit. |
| ~18 s | Skateur en contre-plongée au-dessus d’une barrière, oiseaux au premier plan. | Une courte ponctuation d’énergie au saut de Rafa, puis retour immédiat à une image lisible. |
| ~21 s | Trois trajectoires urbaines réunies avec étirements, superpositions et traînées de mouvement. | Faire du mouvement commun des chaussures le lien entre les époques. Limiter les traînées au raccord, pas aux visages pendant l’émotion. |
| ~24 s | Le groupe se retrouve dans un bus ; angle vivant et proximité. | Passer de l’énergie individuelle au lien entre personnages, avec un cadre à deux au bal. |
| ~27 s | Flash bleu/blanc très contrasté et grand mot « MAKE. ». | Une seule ponctuation de gouache à l’entrée du souvenir ; garder notre signature finale calme et lisible. |

**Notre interprétation :** le ton est joueur, physique et assuré. Le produit participe au mouvement. Pour la transmission familiale, reprendre cette précision des appuis et ces contrastes d’échelle ; réserver le calme aux regards et au geste du père. L’accélération permanente ferait perdre l’émotion.

## Trois effets, avec une fonction narrative

1. **Parquet → terrain :** un appui et un rebond anticipé, coupe sur la même position de chaussure ; 4–6 images de traînée de pigment peuvent accompagner le changement de sol. Le pied reste anatomiquement stable.
2. **Terrain → bal :** même pivot et même sens d’écran ; l’arc du mouvement devient une courte trace de gouache, puis révèle la chaussure rouge d’Elena. Garder une image stable avant et après.
3. **Souvenir → présent :** la voix de Maman commence avant la coupe ; raccord du sourire adolescent au sourire adulte si les deux cadres fonctionnent. Aucun morphing facial nécessaire.

Ces nombres d’images sont des intentions pour un montage à 24 i/s, pas une promesse de précision d’un générateur.

## Priorités de fabrication

- **P0 :** deux comparaisons de visages (Luna ; Rafa et Elena), nouvelle scène téléphone, deux musiques originales, J-cut de Maman. Garder FG01 intact pour comparer.
- **P1 :** insert main au bal et paire de gros plans mère adolescente/adulte. Ce sont les nouvelles couvertures qui donnent le plus de sens au montage.
- **P2 :** trois ponctuations de texture aux transitions. Les ajouter après le choix des visages et du rythme, car elles ne réparent pas une identité ou une action incohérente.

**English production rule:** one readable action per short generated take, plus a quiet handle before and after it. Build timing and transitions in the edit. More coverage should create contrast, not obscure the story.

Le découpage proposé est dans [v4-shot-plan.md](v4-shot-plan.md). C’est une proposition éditoriale de 76 s ; seuls les fichiers déclarés prêts dans la planche de comparaison représentent des essais effectivement générés.
