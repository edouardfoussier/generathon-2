# Audit éditorial indépendant — montage CapCut réaliste

Source : `/Users/edouardfoussier/Movies/CapCut/0927(1).mov`. Original laissé intact. Référence de sélection : `creative/capcut-handoff/selection.json` (20 prises sources, dont deux B07B de modèles différents).

Analyse effectuée le 27 septembre 2026. Direction actuelle : **réaliste / cinéma en prise de vues réelle exclusivement**. Aucun retour au rendu peinture, sketch ou animation.

## Ce qui est réellement dans l’export

- Image : 1942 × 1080, 30 i/s, 2 749 images, **91,633 s**.
- Conteneur / audio : **91,696 s**.
- La dernière image de récit finit à **58,20 s**. L’image est ensuite noire jusqu’à la fin : **environ 33,43 s de noir**. Ce n’est pas une section narrative à remplir artificiellement ; il faut d’abord retirer cette queue à l’export.
- Environ 58 s de récit sont donc déjà montées. Il reste de la place pour quelques plans essentiels tout en restant sous 80 s.
- L’analyse repose sur des images à chaque changement détecté et des échantillons supplémentaires. Les mouvements n’ont pas tous été visionnés continûment. Le son a été vérifié techniquement (piste présente, détection du silence), **pas évalué par une écoute créative indépendante**. On ne peut donc pas conclure ici que toutes les répliques ou musiques sont présentes/absentes.

Images de contrôle : `qa-agent/cuts-1.jpg` et `qa-agent/cuts-2.jpg`. Chaque vignette indique le changement détecté ; l’image montrée est prélevée 0,20 s après. La première planche `every4s.jpg` sert seulement au survol : son échantillonnage est approximatif et ne doit pas servir au calage précis.

## Diagnostic central

Le milieu du film raconte déjà une vie avec clarté : basket, rencontre, mariage, transmission. Ce qui manque visuellement est surtout **Luna avant le voyage, le déclencheur du souvenir, puis ce qu’elle décide de faire de cet héritage**. Sans ces trois points, le montage risque de se lire comme une biographie du grand-père encadrée par quelques inserts de chaussures.

Le retour fille adolescente → Luna à 46,73 s est un bon raccord émotionnel. Le passage de la chaussure jeune sans réparation à la vieille chaussure réparée raconte aussi quelque chose : conserver cette différence cohérente, sans faire apparaître la réparation dès le basket.

## Déroulé et raccords à améliorer

Les limites ci-dessous sont approximatives à une image près et issues de la détection des changements, recoupée visuellement. Certains changements peuvent être internes à une génération plutôt que des coupes posées dans CapCut.

| Temps export | Image observée | Diagnostic / action |
|---|---|---|
| 00,00–05,07 | Avancée dans le grenier vide (B01 Kling) | Le lieu est clair, mais 5 s avant toute présence humaine ralentissent l’accroche. Garder 1,5–2,5 s puis introduire Luna et son attention vers la boîte. |
| 05,07–10,13 | Boîte, vieille paire, photo ; main qui prend la photo (B03 Seedance) | Bonne matière et produit lisible. **Pas encore de visage de Luna**. Ajouter son regard entre la découverte et les lacets ; rendre évident que le jeune homme de la photo devient Rafa au basket. Ne pas dépendre d’un texte minuscule généré dans la photo. |
| 10,13–14,20 | Luna serre les lacets (B05 Seedance) | Action compréhensible, mais le choix de les porter est elliptique. Un plan bref de réaction avant suffit ; pas besoin de montrer intégralement tout l’enfilage. Choisir un dernier geste précis pour le raccord. |
| 14,20–18,27 | Chaussures et jambes de Rafa sur le terrain (B06 Kling) | Le changement d’époque fonctionne comme une coupe mais le lien magique/émotionnel est encore faible. **Plan manquant prioritaire : appui du pied de Luna au présent, cadré pour correspondre à ce pied de Rafa.** Même pied, orientation, taille dans le cadre et trajectoire ; coupe à l’impact. Un raccord franc réaliste suffit. |
| 18,27–20,80 | Sourire du jeune Rafa (S09) | Beau portrait. Placé avant le tir, il présente Rafa mais ne peut pas servir de réaction au panier. Pour un arc d’action plus lisible, essayer de le déplacer après le panier, sans régénérer. |
| 20,80–22,20 | Préparation / tir de Rafa (B07A Veo) | Cadre ample utile. Le montage actuel a bien remis le tir avant le panier ; conserver cet ordre causal. Ne pas réintroduire les deux variantes B07B uniquement parce qu’elles figurent dans le ZIP source. |
| 22,20–24,60 | Ballon / panier (B07B, variante à identifier dans le projet CapCut) | Peut être plus court : impact/filet puis sortie immédiate. Une seule conclusion du tir. La distinction exacte Veo/Seedance ne peut être affirmée uniquement avec ces vignettes. |
| 24,60–27,70 | Chaussures dans la salle de danse (B08) | Bon point de raccord produit. Il manque l’amorce physique qui relie le terrain au parquet. Option : un court atterrissage/pivot de Rafa au basket suivi du même pivot en pantalon de danse. Le raccord peut aussi se construire avec les prises existantes si leurs phases de mouvement coïncident. |
| 27,70–28,87 | Visage de Rafa adulte (S15) | Bon changement d’âge. Préserver cheveux, teint et traits de Rafa dans toute nouvelle prise ; ne pas chercher un nouvel acteur. |
| 28,87–29,87 | Mains qui se rencontrent (S13) | Très utile : contact concret et point d’entrée émotionnel. Ce plan peut préparer le mariage par un raccord de mains. |
| 29,87–36,20 | Rafa et Elena en plan large dansent (B09 Veo) | Plus de 6 s sur le même large : principal endroit où récupérer du temps. Garder le pas le plus expressif sur 2–3 s, éventuellement alterner avec les mains et le regard déjà présents. Pas besoin de multiplier les nouveaux décors. |
| 36,20–39,30 | Couple marié, plan large (B10 Veo) | L’ellipse est lisible grâce au costume et à la robe. Pour la fluidité : raccord de leurs mains dans la danse vers les mains mariées, plutôt qu’un effet arbitraire. Nouveau gros plan seulement si les sources ne permettent pas le raccord. |
| 39,30–41,00 | Couple marié rapproché | Tendresse lisible. Éviter de prolonger les deux tailles de plan si le sourire raconte déjà tout. |
| 41,00–44,83 | Rafa plus âgé présente les chaussures à sa fille (B12 Kling) | **Transmission déjà présente**, ne pas la compter comme manquante. Les chaussures sont encore tenues par lui dans l’image échantillonnée ; vérifier le mouvement complet. Si elle ne les reçoit jamais vraiment, ajouter un insert de mains qui prennent la paire, 1–1,5 s utile. |
| 44,83–46,73 | Sourire de la fille adolescente (S19) | Bon miroir avec Luna. Le lien « cette fille deviendra sa mère » reste implicite : une photo familiale ou une réaction de la mère au présent pourrait le clarifier, mais n’est pas aussi urgente que l’ouverture et la fin. |
| 46,73–47,40 | Retour visage de Luna (B13 Seedance) | Raccord de regard pertinent ; laisser juste assez de temps pour lire le retour au présent. Une inspiration / un clignement et l’appel de la mère hors champ peuvent suffire. Aucun portail visuel nécessaire. |
| 47,40–48,90 | Luna dans le grenier, photo à la main (B14A) | Réancre le décor. Vérifier la continuité : même paire aux pieds, une seule photo et position de la boîte crédible. |
| 48,90–50,67 | Luna regarde vers le bas, sourire rapproché | Bonne résolution intérieure, mais il faut ensuite une décision visible. Une réplique du type « Maman, raconte-moi » peut relier les générations si elle est bien présente dans la version sonore finale. |
| 50,67–52,73 | Luna debout avec le skate (V22) | Prépare son propre chapitre. Le mouvement reste à l’arrêt : compléter par un départ ou un premier mouvement de skate, pas par un deuxième simple portrait. |
| 52,73–54,13 | Main / skateboard (V25) | Bonne texture, mais ancien QA : signes/graphismes inventés sur la planche. N’utiliser que le segment où le plateau reste cohérent, ou remplacer par une prise simple sans inscription. Cette référence ne fixe pas un graphisme de skateboard définitif. |
| 54,13–58,20 | Chaussures usées de Luna, pas calme (B15 Seedance) | Bon dernier plan produit possible, avec espace pour une signature. Il manque le geste « **c’est elle qui les fait** » : trace, personnalisation ou marque ajoutée par Luna. Ajouter ce geste avant le départ, puis garder ce plan produit 1,5–2 s pour signer. |
| 58,20–91,63 | Noir | Retirer. Il n’y a ni signature lisible ni image de conclusion dans cette queue. |

## Générations prioritaires, indépendantes et réalistes

### P1 — nécessaires pour clarifier Luna et l’idée de marque

1. **Luna découvre / reconnaît** — 3 à 4 s brutes, 1,5–2,5 s utiles. Plan rapproché à hauteur de visage dans le grenier existant. Même Luna, queue-de-cheval sombre, T-shirt anthracite, pantalon olive, lumière de la fenêtre à gauche. Son regard quitte les affaires encombrantes et se fixe sur la vieille photo ; irritation légère qui devient curiosité. Une seule action. À monter entre la boîte et les lacets.
2. **Pied au présent → pied au souvenir** — deux images clés compatibles, puis courte animation de l’appui. À partir du vrai dernier cadrage des lacets et du vrai premier cadrage du B06. Pas de transformation anatomique : le sol devient asphalté et les vêtements changent au raccord ; la position du pied reste stable. 4 s brutes permettent de sélectionner une coupe de 6–10 images autour du contact.
3. **Le geste personnel de Luna** — 3 à 4 s brutes, 1,5–2 s utiles. Gros plan réel de sa main qui ajoute une petite marque personnelle sur une zone libre de toile ou près des initiales héritées, sans effacer la patine. Pour des lettres exactes « R.M. / L.M. », prévoir un ajout en postproduction ou une image validée ; ne pas compter sur la typographie vidéo générée. Ce geste rend « Made by you » visible.
4. **Son premier pas à elle** — 4 à 5 s brutes, 2–3 s utiles. Luna commence un mouvement simple de skate sur un terrain de quartier, chaussée de la paire héritée. Une seule poussée contrôlée, caméra basse en trois quarts, pas de figure complexe. Le basket de Rafa devient le skate de Luna. Même chaussure et mêmes accessoires ; aucune nouvelle identité.

### P2 — utiles seulement si les sources existantes ne suffisent pas

5. **Basket → salsa : pivot raccordé.** Même cadrage du pied, vitesse et sens de rotation. Le grand changement d’époque vient des chaussettes/pantalon, du sol et de la lumière. 1 s de raccord utile peut suffire.
6. **Salsa → mariage : mains.** Mains qui se prennent puis mains mariées dans le même sens. Alternative directe au gros zoom sur une chaussure pour chaque ellipse.
7. **Paire reçue par la fille.** Seulement si B12 ne contient pas le transfert complet. Une paire, deux mains de chaque côté, prise sûre et lente ; pas de nouvelle scène longue.
8. **Mère au présent, réaction.** 2–3 s utiles, répond au regard de Luna et confirme la continuité familiale. À condition de verrouiller sa ressemblance avec la fille de 1995 et sa version adulte déjà définie.

### Ne pas ajouter automatiquement

- **Écran / échange avec une IA** : absent de ce montage visuel. Il appartenait à une version précédente du script. Il n’est pas indispensable au brief « Made by you » ; le réintroduire ajouterait une branche narrative. À générer seulement si l’équipe souhaite encore explicitement cette idée.
- **Naissance du bébé** : absente ici, mais le mariage → transmission fonctionne déjà comme une ellipse de vie. Ce n’est pas une lacune obligatoire.
- **Funérailles / tombe** : aucune nécessité de réintroduire l’ancienne ouverture ; elle déplace l’émotion vers le deuil au détriment du propre élan créatif de Luna.
- **Transitions de style peinture / multivers anime** : incompatibles avec la direction réaliste retenue pour cette étape.

## Plan d’édition après réception des nouveaux assets

Viser environ **65–75 s utiles**, pas 80 s par obligation. Retirer les 33,43 s noires, raccourcir le grenier vide et la danse large, puis ajouter les quatre passages P1. Garder le sourire de Rafa après le panier si cela améliore la causalité. Conserver le raccord fille → Luna. Terminer avec l’action personnelle de Luna et une signature sobre, lisible, posée au montage : **CONVERSE — Made by you.** « Conserve what matters » peut rester une accroche de concept, sans remplacer la signature du brief.

Vérifier à la fin : même pied et axe aux raccords ; étoile sur la face intérieure cohérente du modèle ; réparation uniquement dans les périodes où elle existe ; même quantité de chaussures/photos ; coupe du pantalon, coiffure et skate constants ; aucune queue noire involontaire. La mention de pub non officielle appartient à la livraison / présentation et doit rester clairement identifiable.
