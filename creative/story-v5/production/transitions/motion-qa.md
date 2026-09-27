# VT01 — Essai animé silencieux du raccord présent → souvenir

Un seul essai demandé à Seedance2.5, 6 s,720p, sans audio. Références : T01A puis T01B. Les deux images et leurs résultats initiaux restent intacts.

## Intention de mise en scène

0–2,4s : pied droit de Luna au grenier, pointe à gauche, réparation présente, léger transfert de poids et talon qui termine doucement son appui. Vers2,5s : **coupe franche sur l'appui**, même orientation et taille de chaussure. 2,5–6s : pied de Rafa sur le terrain, chaussette blanche à deux bandes bordeaux, réparation absente, poids qui se stabilise. Caméra fixe, matière gouache constante. Le changement temporel est porté par la coupe ; on ne demande pas au vêtement ni au sol de se métamorphoser.

## Contrôle prévu

- Durée, dimensions, cadence et présence/absence réelle de piste audio via ffprobe ; décodage complet via ffmpeg.
- Images avant, autour et après la coupe : cadrage, unicité du pied, contact sol/semelle, lacets, état du patch, face extérieure sans écusson.
- Coupe franche versus fondu/morphing : documenter le résultat observé plutôt que considérer le prompt comme une preuve.
- Les images sources diffèrent déjà d'environ20px en hauteur de semelle sur1072px. Juger si le léger mouvement d'appui rend ce décalage acceptable, sans prétendre à un raccord au pixel.

## Résultat observé

**Généré et inspecté ; statut : à corriger.** Fichier : `videos/T01-motion.mp4`. Un seul appel Seedance2.5, **252 crédits**, aucun nouvel essai payant.

### Mesures techniques

Durée réelle **6,041667 s**,1280 ×720,24 images/s,145 images, H.264. **Aucune piste audio**. Le décodage complet par ffmpeg finit sans erreur. Métadonnées détaillées dans `qa-motion/ffprobe.json`.

### Ce qui fonctionne

La caméra reste pratiquement fixe, la chaussure demeure unique, pointe à gauche, et aucun faux écusson extérieur n'apparaît. Le pied reste à proximité de son appui ; le talon semble légèrement se soulever puis revenir. La matière peinte tient bien sur la chaussure, le vêtement et le décor. Après le passage, chaussette blanche à deux bandes bordeaux et terrain ancien sont lisibles.

### Ce qui ne respecte pas la consigne

Le modèle a produit un **fondu global d'environ2,0 à2,8s**, au lieu de la coupe franche demandée vers2,5s. Les images intermédiaires montrent simultanément cargo et chaussette, grenier et grille du terrain. La réparation disparaît progressivement pendant ce fondu, ce qui suggère une transformation magique. Les lacets ont aussi été légèrement redessinés et le caoutchouc varie. Il n'y a donc pas de véritable raccord sur l'appui à retenir tel quel.

Le contrôle a porté sur une planche24 images à4 images/s, puis sur des images agrandies au début, vers1,5s,2s,2,25s,2,5s,3s et5,75s. La planche est `qa-motion/contact-sheet.png`. Les temps de prélèvement sont approximatifs ; le défaut de superposition reste manifeste sur plusieurs images consécutives.

### Suite proposée

Conserver ce clip comme **diagnostic**. Pour maîtriser réellement la coupe, produire deux plans courts indépendants utilisant les mêmes repères de chaussure, puis réaliser une coupe franche au montage. Cette production n'a pas été lancée : aucun nouveau crédit, son ou montage final ajouté. Les deux stills restent des candidats utiles et leur fichier `result.json` n'a pas été modifié par l'essai animé.

## Correction locale VT01-CUT — sans nouvelle génération

Une correction plus économique est disponible : les deux portions propres de VT01 permettent déjà un raccord. Après inspection des images sources40,42,44,46,48,50,64,66,68,70 et72, on conserve **0–46 inclus** pour le grenier, puis **70–144 inclus** pour le terrain. Les23 images47–69 du passage indésirable sont retirées. L’original diagnostique reste disponible sans modification.

`videos/T01-clean-cut.mp4` contient **122 images /5,083333 s /1280×720 /24 images/s**, H.264, **sans audio**. La coupe intervient à l'image de sortie47, soit **1,958333 s**. C'est une coupe directe entre deux plans : aucune interpolation, aucun fondu ni correction de géométrie. Réencodage local libx264CRF18. Coût additionnel : **0 crédit** ; le total de ce lot vidéo reste252.

Le décodage complet est vérifié. Les images de sortie45,46,47,48 ont été examinées côte à côte (`qa-motion/clean-cut-boundary.png`) : le patch existe jusqu'à la dernière image du grenier, disparaît seulement au changement de plan, et aucun mélange entre cargo/chaussette ou grenier/terrain ne subsiste. Il reste un petit saut de hauteur de semelle, approximativement10–15px sur720px, ainsi que des différences de lacets et d'usure. La chaussure garde la même échelle générale et sa pointe vers la gauche.

**Statut : candidat**, pas raccord parfaitement enregistré ni sélection finale. Ce petit montage sert uniquement de preuve de transition ; le son et le montage du film complet restent pour la phase suivante.
