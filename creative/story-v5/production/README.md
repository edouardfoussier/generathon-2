# Rafa & Luna — atelier visuel v5

La direction v5 a été autorisée pour exploration par l’équipe le 27 septembre 2026. Les images ci-dessous sont des candidats contrôlés, pas une sélection finale. Les films FG01, les rendus v4, leurs musiques et les autres recherches restent intacts.

Ouvrir la [planche FR/EN](http://127.0.0.1:8787/creative/story-v5/production/index.html?lang=fr) avec le serveur habituel du projet (`python3 creative/editor/server.py`). Le filtre, l’agrandissement et les comparaisons facilitent la discussion. Les favoris sont locaux au navigateur ; l’export JSON permet de partager une sélection sans prétendre synchroniser les votes de l’équipe.

## Ce premier lot couvre

- **K01** : Luna suspend le feutre au-dessus de la languette ; sa propre marque est absente.
- **T01A / K02** : appui au grenier, réparation extérieure droite présente.
- **K03** : Rafa se remet en position après un essai manqué ; le panier manqué exige encore un insert ou un mouvement explicite.
- **K04** : Elena lui offre sa main après le premier faux pas. Le détail de la maladresse reste un travail d’animation.
- **K05** : la mère adolescente reçoit la paire. Rafa porte ses mocassins de maison.
- **K06** : Luna retrouve Maman au présent et lui adresse un regard actif.
- **K07** : l’après-geste. L.M. rejoint R.M., le feutre est éloigné de la chaussure.
- **K08** : Luna repart sur sa planche dans le terrain actuel.
- **T01B** : entrée du souvenir en 1970, géométrie proche de T01A et réparation absente.

Cela représente **huit images clés de récit et une seconde extrémité de raccord**. Ce n’est pas encore la couverture intégrale des seize séquences du scénario de 78 secondes. La photo de Rafa, les inserts et la signature restent à décliner après le choix des cadres.

## Itérations conservées

Les premières versions K01 et K07 rendaient le geste ambigu : le feutre paraissait déjà écrire au-dessus de R.M. Une relecture visuelle indépendante a confirmé cette faiblesse. Les versions `luna/images/K01-refined.png` et `K07-refined.png` séparent maintenant clairement la suspension du geste et son résultat. Les premiers fichiers, prompts et identifiants restent présents dans `luna/` et `result-first-pass.json`.

K05 a été corrigé une fois pour retirer la réparation du pied gauche et la replacer du côté droit. `memories/K05.png` est le premier essai ; `K05-corrected.png` est le candidat affiché. Aucun original n’a été écrasé.

## Continuité observée à reprendre dans les plans suivants

- **Luna en skate** : K08 montre le pied droit sur la planche, le gauche poussant. Cette position est plausible et garde la réparation sur le pied droit. Si l’équipe retient ce cadre, les futurs mouvements doivent utiliser cette position, même si le premier prompt demandait l’inverse.
- **Transmission** : dans K05, Rafa ajuste la chaussure gauche. Un insert de la réparation doit établir le pied droit avant de raccorder au doigt de Luna. Ne pas retourner horizontalement le plan.
- **T01** : la chaussure occupe environ 57 % du cadre, plutôt que les 45 % demandés. Les cadres sont proches ; la semelle de B descend d’environ 20 pixels sur 1072 et les lacets varient. C’est un candidat de coupe sur l’appui, pas une base de morphing parfaitement superposable.
- **Produit** : les deux petits œillets latéraux erronés de K01/K07 ont été supprimés dans leurs corrections. Continuer à vérifier la face intérieure de l’étoile et la petite réparation extérieure droite à chaque nouveau plan.
- **Visages** : la génération conserve les identités GPT du film aimé et décrit la peau comme des plans de gouache. Une matière convaincante à l’arrêt ne garantit pas sa stabilité en mouvement.

## Essais de mouvement

Deux prototypes muets de six secondes ont été générés : **VK01**, suspension/retrait du feutre à partir de la première version de K01 ; **VT01**, coupe grenier → terrain à partir de T01A/B. Ils vérifient des problèmes précis. Ils ne constituent ni le montage final ni de nouvelles scènes approuvées. Leurs résultats et limites figurent dans la planche et les fichiers `motion-result.json` après contrôle. Le visage de VK01 reste trop lisse et est signalé à corriger. VT01 produisait un fondu ; une troisième vidéo, **VT01-CUT (5,08 s)**, retire localement ce fondu et restaure une coupe franche entre les portions stables, sans nouvelle génération ni dépense. Le léger saut de semelle reste signalé.

## Provenance et coût

Les images utilisent GPT Image 2.5 Sunburst via Arcads, avec les références existantes de la continuité GPT. Douze générations d’image ont été effectuées : neuf cadres actuellement affichés et trois versions antérieures conservées ; **96 crédits** d’image au total. Les essais vidéo utilisent Seedance 2.5 en 720p, audio désactivé. Les deux générations vidéo coûtent 504 crédits ; la correction locale est gratuite. **Total du lot : 600 crédits**, solde Arcads passé de 3 032 à **2 432**. Le manifeste conserve ce rapprochement et chaque provenance.

La clé FAL proposée n’a pas été utilisée ni enregistrée. Les références étaient déjà présentes dans Arcads ; aucun nouveau casting ou lot externe n’a été introduit.

## Prochaine décision d’équipe

Regarder d’abord K01 → K06 → K07 → K08 sans dialogue, puis les souvenirs. Vérifier que le geste final paraît choisi par Luna et que les souvenirs le préparent. Choisir les cadres avant de multiplier les animations ; conserver les erreurs signalées comme éléments à corriger, pas comme détails à cacher au montage.

**Publicité spéculative non officielle. Converse n’est pas partenaire du projet. Signature prévue : CONVERSE / MADE BY YOU.**
