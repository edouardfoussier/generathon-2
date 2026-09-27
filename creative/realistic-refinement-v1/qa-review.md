# QA indépendante des nouvelles prises réalistes

Ces observations sont des recommandations de montage, pas une approbation automatique de l’équipe. Les fichiers de génération restent inchangés. Aucun nouveau rendu n’est lancé par cette revue.

## RT01-M — Rafa, appui sur le terrain

Fichier : `videos/RT01-M-rafa-appui.mp4`.

Contrôle technique : fichier complet et entièrement décodable sans erreur FFmpeg ; 4,041667 s, 97 images à 24 i/s, 1928 × 1072 ; piste audio présente. Le contenu sonore n’a pas été évalué à l’écoute.

Méthode visuelle : prélèvement à toutes les 6 images (0,25 s), puis à toutes les 2 images de 1,50 à 2,75 s pour examiner le mouvement. Planches : `qa-review/RT01-M-strip.jpg` et `qa-review/RT01-M-motion-strip.jpg`. Ce n’est pas une validation image par image de tout le fichier.

### Ce qui tient

- La pointe de la chaussure proche dirige constamment le regard vers la **droite écran**.
- Le profil initial est net, avec une semelle lisible, des lacets cohérents et une chaussette blanche à bandes bordeaux. Matière réaliste, pas de texture peinte.
- La face extérieure proche reste sans écusson ; lorsque les pieds se séparent, l’écusson intérieur du pied éloigné devient visible. Ce changement est compatible avec la géométrie des deux pieds.
- Aucun pied supplémentaire ou rupture majeure de la chaussure n’apparaît dans les images contrôlées. Le décor et la lumière restent cohérents.

### Ce qui limite le raccord

| Intervalle source | Mouvement observé | Usage conseillé |
|---|---|---|
| 0,00–1,50 s | Pied presque posé / immobile, légère variation d’appui | **Meilleur intervalle pour un raccord strict** avec le présent, à condition que le nouveau plan de Luna ait la même silhouette et le même axe. |
| 1,50–1,75 s | Amorce de soulèvement / déplacement | À garder seulement si Luna amorce exactement le même mouvement. |
| 1,75–2,75 s | Le pied se soulève, se déplace nettement vers la gauche écran et pivote vers la caméra ; l’autre pied se dégage | Ce n’est pas le simple appui vertical prévu. Éviter pour une substitution parfaite Luna → Rafa. Le mouvement peut fonctionner comme amorce de déplacement de Rafa après le raccord. |
| 2,75–4,04 s | Les deux pieds reposent, dans une nouvelle orientation trois quarts | Exploitable comme fin d’un déplacement, mais ce cadre ne correspond plus au profil initial. Ne pas le raccorder au présent sans un départ de Luna construit sur cette nouvelle géométrie. |

### Proposition de montage provisoire

Commencer le souvenir au **frame 0**, couper vers le plan qui révèle Rafa entre **0,50 et 1,50 s** selon le rythme. Le segment conseillé pour comparaison est donc **[0,000 ; 1,500[**, soit les images **0 à 35 incluses**. Un raccord plus nerveux peut conserver seulement les 12–16 premières images avant la révélation.

Cette suggestion reste **conditionnelle** : la nouvelle image/animation de Luna corrigée doit encore être comparée côte à côte. La première image de Luna avec la pointe inversée a été rejetée par la réalisation et ne doit pas servir à prétendre que le raccord est validé. Ne pas retourner horizontalement tout le plan pour compenser : cela déplacerait aussi réparation, écusson, décor et lumière.

Statut de revue : **prise utilisable en partie, raccord final non validé**. Le mouvement généré après 1,75 s diffère du geste demandé ; ne pas présenter les 4 secondes comme un appui vertical réussi.

## RT01-P corrigée — comparaison présent / souvenir

Fichier : `videos/RT01-P-luna-appui.mp4`. Il dérive de la nouvelle image corrigée, pas de la première image rejetée.

Contrôle : 4,041667 s, 97 images à 24 i/s, 1928 × 1072 ; décodage complet sans erreur. Planche `qa-review/RT01-P-strip.jpg`, échantillonnée toutes les 0,25 s.

La pointe regarde maintenant **à droite écran**, comme Rafa. La réparation crème distingue bien la paire usée du présent et disparaît dans le souvenir. Le début du mouvement conserve une silhouette très proche ; ensuite Luna soulève légèrement le talon et déplace le pied vers la droite. Son atterrissage vers 1,7 s est donc **moins raccord** avec le profil initial de Rafa que le début de prise.

### Coupe proposée, précisément

- **Présent P :** `trim=start_frame=0:end_frame=13` — 13 images, soit 0,541667 s. Dernière image visible : **frame 12, P à 0,500 s**.
- **Souvenir M :** `trim=start_frame=0:end_frame=24` — 24 images, soit 1,000 s. Première image visible : **frame 0, M à 0,000 s**.
- Enchaîner par une **coupe franche**, sans miroir horizontal, puis révéler Rafa dans le plan suivant.

Comparaison à taille et coordonnées identiques : `qa-review/RT01-P-M-cut-comparison.jpg`. Niveau de semelle et taille sont très proches, avec un petit décalage horizontal résiduel. La couture et les lacets restent reconnaissables. C’est un **raccord graphique crédible à comparer au montage**, pas une preuve d’un mouvement vertical parfaitement continu : les premières demi-secondes sont assez calmes.

Statut : **meilleure proposition de coupe parmi P/M, à montrer à l’équipe**. Cette recommandation ne remplace pas leur choix final ni le visionnage du raccord assemblé.

## RT01-C — passage continu avec éclat lumineux

Fichier : `videos/RT01-C-flashback-continu.mp4`. 5,041667 s, 121 images à 24 i/s, 1928 × 1072 ; décodage complet sans erreur. Planche `qa-review/RT01-C-strip.jpg`, toutes les 0,25 s.

- 0–2,5 s : présent, pied qui oscille / petit mouvement de talon. Le basculement ne part pas immédiatement.
- Vers 2,7–3,7 s : éclat lumineux large, presque blanc au centre vers 3,0–3,25 s. Le changement de sol et de vêtement est masqué par cette surexposition.
- Vers 3,75–5,04 s : souvenir lisible, chaussettes à bandes, terrain et paire sans réparation.

**Pas de fonte flagrante du pied exposée dans les images inspectées.** Il serait inexact de qualifier automatiquement ce rendu de morphing raté. En revanche, l’éclat prend près d’une seconde et ressemble davantage à une transition lumineuse appuyée qu’au très bref flash / raccord prévu. Le souvenir arrive tard dans la prise, après beaucoup de petit mouvement.

Recommandation : **conserver comme variante expérimentale**, comparer à la coupe P→M, privilégier cette dernière pour un rythme plus net et sobre. Ne pas annoncer la transition C comme un raccord invisible validé. Le contrôle visuel échantillonné ne garantit pas l’absence de tous les artefacts sur les images masquées par le blanc.

## RL02 — geste orange sur la réparation

Référence examinée : `luna/qa/RL02-contact.jpg`, issue du clip complet `luna/videos/RL02.mp4` (5,041667 s, 121 images à 24 i/s selon sa métadonnée).

Le geste se comprend : Luna dessine sur la réparation avec un outil orange, puis lève la main. Les doigts, le lacet et la chaussure paraissent cohérents dans les échantillons. L’orange devient un **aplat / trait très épais sur une large partie du haut de la réparation crème**, pas une fine ligne discrète.

La personnalisation est donc visuellement lisible et utile à « Made by you », mais la direction exacte a évolué. Nommer honnêtement ce résultat « accent / marque orange ». L’équipe doit choisir si cet aplat convient ; ne pas le valider silencieusement comme la fine ligne demandée. La portion crème demeure visible sous la marque.

## RL03 — départ en skate et continuité de la marque

Référence examinée : `luna/qa/RL03-contact.jpg` et une image pleine résolution du clip à **1,60 s**, `qa-review/RL03-orange-check.png`. Clip : 5,041667 s, 121 images à 24 i/s selon sa métadonnée.

Une poussée puis un départ se lisent clairement. Même silhouette générale : queue-de-cheval, T-shirt sombre ample, cargo olive et chaussures montantes. Le cadrage de dos évite de devoir juger un visage nouveau ; le visage n’est pas assez exposé pour valider son identité par les traits.

**La marque orange n’est pas lisible de façon indépendante** dans ce plan large, y compris sur l’image pleine résolution à 1,60 s. Distance, angle et mouvement empêchent de vérifier sa forme ou son emplacement. Ce manque de lisibilité ne suffit pas non plus à déclarer qu’elle a disparu : les faces observables des chaussures diffèrent du gros plan RL02.

Usage conseillé : RL02 établit le geste personnel, puis RL03 raconte le départ. Ne pas décrire RL03 comme une preuve que l’orange a été parfaitement conservé. Pour un dernier plan produit rapproché après RL02, vérifier séparément que la marque est effectivement présente ; un ancien plan B15 sans orange reviendrait visuellement à l’état antérieur.
