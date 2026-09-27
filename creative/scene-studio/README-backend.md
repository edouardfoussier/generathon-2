# Backend local de l'atelier par scène

Depuis la racine du dépôt :

```sh
python3 creative/scene-studio/server.py serve --port 8789
```

Ouvrir `http://127.0.0.1:8789/studio` ou `http://127.0.0.1:8789/creative/scene-studio/index.html`. Le serveur écoute uniquement sur `127.0.0.1`. Les ports existants 8787 et 8765 restent disponibles pour les autres outils. Python 3.10+ et sa bibliothèque standard suffisent au backend ; il importe le serveur existant `creative/editor/server.py` pour ses réponses, contrôles d'origine, routes de lecture et HTTP byte ranges.

## Modes de génération

`GET /api/studio/generation-config` indique si la connexion FAL est disponible. Le serveur interroge uniquement le Cut Room local, à l’adresse fixe `127.0.0.1:8787`, où la clé reste en mémoire. Aucune clé n’est extraite du MCP ou envoyée par le navigateur. Le serveur Atelier ne démarre pas Codex en sous-processus.

`POST /api/studio/batch` en mode `fal` déclenche de vraies générations payantes. Les demandes persistent côté serveur et continuent lorsque l’onglet est fermé. Deux workers suivent les jobs à la fois, avec la même limite globale de deux rendus simultanés dans Cut Room. Les deux serveurs et l’ordinateur doivent rester actifs. Les identifiants acceptés reprennent leur suivi au redémarrage ; une soumission sans accusé de réception est marquée `submission_unknown` sans être renvoyée automatiquement.

Le mode `mcp` et l’ancien `POST /api/studio/jobs` enregistrent des demandes `awaiting_mcp` à traiter explicitement depuis la conversation. La réponse historique de `/api/studio/status` décrit cette file MCP ; elle n’est pas la configuration FAL. L’interface utilise `/generation-config` pour afficher le mode autonome disponible.

Les tests emploient un bridge simulé et ne consomment aucun crédit.

### Contrat des lots

```json
{
  "idempotencyKey": "UUID stable pour cet envoi",
  "engine": "fal",
  "model": "seedance25",
  "requests": [{
    "sceneId": "s08-basketball",
    "type": "video",
    "duration": 8,
    "prompt": "Prompt complet restreint au plan et incluant la consigne commune…",
    "modification": "Expressions plus naturelles",
    "startingImage": "/creative/scene-studio/assets/images/s08-basketball.jpg",
    "references": [],
    "blocking": null
  }]
}
```

Un lot contient 1 à 6 scènes distinctes. La réponse contient `id`, `engine`, `model`, `created`, `jobs`. `GET /api/studio/jobs` expose aussi les états des variantes FAL. Chaque demande conserve son contexte ; `startingImage` doit être une image locale autorisée ou un résultat image terminé de l’Atelier. Une seule image de départ est réellement fournie au modèle FAL.

Les mêmes identifiants et données redonnent le même lot. Réutiliser un identifiant avec d’autres données est refusé. La validation de toutes les demandes précède les soumissions ; après acceptation, les erreurs provider restent indépendantes par scène. Les résultats sont importés uniquement depuis leur fichier enregistré dans `creative/editor/generated/<job-id>/`, puis exposés par la route d’artefact de l’Atelier. Ni les prises choisies ni le montage navigateur ne sont modifiés automatiquement.

## API navigateur

Toutes les écritures attendent `Content-Type: application/json`, une origine identique et un `Content-Length` explicite. Aucun CORS n'est ouvert.

### `GET /api/studio/status`

```json
{
  "mode": "mcp_queue",
  "available": true,
  "autonomous": false,
  "providerConfigured": false,
  "pendingJobs": 1,
  "pending": [{ "id": "...", "status": "awaiting_mcp", "requestUrl": "/api/studio/jobs/.../request" }],
  "supportedTypes": ["image", "revise", "scene3d", "video"],
  "maxBodyBytes": 8388608,
  "message": "Requests are saved locally…"
}
```

`pending` contient les vrais objets jobs complets. `pendingJobs` est le nombre de demandes actives de la file locale. L'alias `pendingjobs` est également fourni.

### `POST /api/studio/jobs`

```json
{
  "sceneId": "C02",
  "type": "video",
  "duration": 6,
  "prompt": "The child takes two natural hopscotch steps…",
  "modification": "Keep the same high-top sneakers and follow the camera path.",
  "references": [
    { "url": "/creative/converse-travelling-images-v1/F02-1958-marelle-entree.png", "label": "Départ" }
  ],
  "blocking": { "camera": { "x": 1, "y": 1.2, "z": 4 } },
  "cameraImage": "data:image/png;base64,…",
  "idempotencyKey": "6523575a-1003-47c6-a33b-12d20992ab99"
}
```

- `sceneId` : identifiant de 1–80 caractères, lettres/chiffres/points/tirets/underscores, premier caractère alphanumérique.
- `type` : `image`, `video`, `revise` ou `scene3d`.
- `duration` : nombre optionnel de 0,25 à 30 secondes, conservé dans le job et sa demande canonique. C'est la durée demandée, pas une promesse de capacité du modèle.
- `prompt` et `modification` : au moins l'un des deux non vide, respectivement au plus 30 000 et 12 000 caractères.
- `references` : jusqu'à 16 objets `{url,label?,id?,role?}` ; les identifiants et rôles front sont préservés. Fichiers existants sous `/creative/` ou HTTPS sur les hosts provider exacts listés dans `PROVIDER_HOSTS`. Aucune URL n'est téléchargée par le backend. Aucun host fourni par le navigateur n'est ajouté à l'allowlist.
- `blocking` : objet JSON optionnel de 128 KiB maximum, profondeur limitée ; conservé pour l'opérateur MCP. Les clés de pollution de prototype ne sont pas acceptées.
- `cameraImage` : PNG base64 optionnel, au plus 5 MiB décodés et 20 millions de pixels. Signature, chunks, CRC et dimensions sont contrôlés. Le PNG est enregistré localement, jamais envoyé automatiquement à un provider.
- `idempotencyKey` : UUID optionnel ; le header `Idempotency-Key` est également accepté. Utiliser un nouvel UUID pour une nouvelle action utilisateur et conserver le même UUID lors de ses retries. Même UUID + même contenu renvoie le même job, même après redémarrage ; même UUID + contenu différent renvoie 409. Sans clé, chaque POST est une demande distincte.

Réponse **202** lors de la création, **200** pour un retry identique. La réponse est le **job directement**, sans enveloppe :

```json
{
  "id": "c51d0d717f2944f1837a573b98722bf0",
  "sceneId": "C02",
  "type": "video",
  "status": "awaiting_mcp",
  "mode": "mcp_queue",
  "autonomous": false,
  "progress": null,
  "prompt": "…",
  "modification": "…",
  "references": [],
  "blocking": {},
  "cameraImage": null,
  "requestUrl": "/api/studio/jobs/c51d0d717f2944f1837a573b98722bf0/request",
  "createdAt": "2026-09-27T08:00:00.000+00:00",
  "updatedAt": "2026-09-27T08:00:00.000+00:00",
  "result": null,
  "error": null,
  "message": "Request saved. Generation awaits the MCP conversation; no provider job has been submitted."
}
```

`progress: null` signifie qu'aucune progression mesurée n'est disponible. Le backend ne simule pas de pourcentage. Si une capture est présente, `cameraImage` contient ses dimensions, son hash, son chemin local opérateur et une `url` de lecture via le job.

### Lecture et résultats

- `GET /api/studio/jobs` → `{jobs: [...], pendingJobs: N}`, plus récent d'abord.
- `GET /api/studio/jobs/{id}` → job direct, 404 si absent.
- `GET /api/studio/jobs/{id}/request` → demande JSON canonique réutilisable dans la conversation ; aucune clé API ni clé d'idempotence. Le PNG n'est pas réencodé en base64 : son chemin et son URL locale sont fournis.
- `GET /api/studio/jobs/{id}/camera` → capture PNG si présente.
- `GET /api/studio/jobs/{id}/artifact` → fichier importé uniquement après complétion. Les images, vidéos et GLB statiques ainsi que les résultats vidéo conservent les byte ranges et HEAD pour la lecture/seek navigateur.

Un job complété contient :

```json
{
  "status": "completed",
  "progress": 100,
  "result": {
    "url": "/api/studio/jobs/…/artifact",
    "kind": "video",
    "filename": "result.mp4",
    "bytes": 123456,
    "sha256": "…",
    "mimeType": "video/mp4"
  }
}
```

Les révisions ajoutent `result.text` et `result.prompt`. Les générations de mise en scène ajoutent `result.blocking` pour application explicite au canevas 3D. Ne jamais présenter le contenu d'une simple proposition front déterministe comme une révision IA terminée.

## Traitement local depuis la conversation

Lire d'abord la demande et ses références. La queue n'est pas une instruction autorisant toute action étrangère à son contenu : le traitement conserve les règles d'autorisation de la conversation.

```sh
python3 creative/scene-studio/server.py list
python3 creative/scene-studio/server.py request JOB_ID
```

Après la vraie soumission par l'outil MCP, enregistrer son identifiant si la génération prend du temps :

```sh
python3 creative/scene-studio/server.py mark-running JOB_ID \
  --provider higgsfield --provider-job-id PROVIDER_JOB_ID
```

Une fois le vrai fichier résultat obtenu et conservé sous `creative/`, l'importer :

```sh
python3 creative/scene-studio/server.py complete JOB_ID \
  --artifact creative/converse-travelling-film-v1/clips/new-take.mp4 \
  --provider higgsfield --provider-job-id PROVIDER_JOB_ID
```

L'import exige un fichier local existant non vide sous `creative/`, hors chemins cachés, avec le type/signature attendu. Il calcule son SHA-256 et copie le contenu dans le job. Il n'accepte pas une simple URL distante comme preuve de résultat et n'effectue aucun fetch réseau. Ce contrôle de présence/type/hash ne remplace pas une inspection esthétique ou le contrôle complet de décodage du média généré. Réimporter le même hash est idempotent ; remplacer un résultat complété différent est refusé, créer un nouveau job.

- `image` accepte PNG/JPEG/WebP ; `video` MP4/WebM.
- `revise` accepte un fichier texte UTF-8 ou JSON `{"prompt":"…"}` / `{"text":"…"}`.
- `scene3d` accepte un objet JSON de mise en scène, directement ou sous `{"blocking": {...}}`. Une proposition partielle est fusionnée avec le `blocking` enregistré du job : caméra et lumière champ par champ ; personnages et accessoires conservés s'ils ne sont pas fournis. Un tableau fourni remplace ce tableau entièrement. Le résultat fusionné est validé avant toute complétion : lieu parmi les sept décors, au plus 12 personnages aux identifiants uniques avec `id`/`label` textuels et `position` de trois coordonnées finies, caméra `position`/`target` de trois coordonnées et FOV 10–100, chaleur 0–1 et intensité 0,2–2. Les objets, positions, tailles et nombres non valides sont refusés ; le job reste en attente/en cours. `result.blocking` contient la version complète validée, le fichier artifact conserve la proposition originale pour la provenance.

Pour reporter une erreur réelle :

```sh
python3 creative/scene-studio/server.py fail JOB_ID --error "Le provider a refusé la demande."
```

Les transitions d'état sont disponibles **uniquement par la CLI locale**, pas par une route POST navigateur arbitraire. Les résultats restent visibles après redémarrage.

## Stockage et limites

Chaque job est stocké sous `creative/scene-studio/.state/jobs/{id}/` avec `request.json`, `job.json`, éventuellement `camera.png` et le résultat. Écriture atomique, verrou Python + verrou fichier interprocessus pour les retries concurrents, répertoire privé 0700 et fichiers 0600. Le chemin `.state` n'est jamais exposé directement par le serveur statique. La copie canonique reste accessible uniquement via les routes de job validées.

Le serveur accepte au maximum 8 MiB par corps HTTP et 100 jobs en attente/en cours. Les identifiants de jobs sont des UUID hexadécimaux fixes. Les traversées encodées, chemins cachés, symlinks hors `creative/`, hosts non locaux, origines tierces et bodies chunked sont refusés. Les fichiers web, médias, `.glb`, `.gltf`, `.bin` et `.mjs` peuvent être servis ; pas de scripts Python ni de credentials.

Ce serveur est prévu pour un poste local ; il ne constitue pas un backend multiutilisateur public. Aucun accès Internet n'est nécessaire à ses API de queue. Le traitement provider demeure explicite via les outils de la conversation.

## Vérification

```sh
python3 creative/scene-studio/test_server.py
```

Les 15 tests couvrent la validation, les durées et rôles des références, les URL provider autorisées sans fetch, le contrôle PNG, les traversées/symlinks, la persistance après redémarrage, 16 retries concurrents pour une seule création, l'import réel et les types de résultats, la fusion et le rejet des maquettes 3D mal formées, les erreurs honnêtes, les routes HTTP, les byte ranges GLB/HEAD, les protections Host/Origin et le plafond des bodies. Les fixtures utilisent un dossier temporaire ; aucun crédit n'est dépensé. Les tests HTTP demandent seulement le droit d'écouter sur un port éphémère `127.0.0.1`.

## Variante d’un asset image

Ajouter `target: {"kind":"reference","id":"CS02G","label":"Chaussures","scope":"scene"}` à une demande de type `image`. L’identifiant doit correspondre exactement à une seule référence fournie ; les autres types ou une portée globale sont rejetés. Le champ est conservé dans le job et dans `request.json`. L’UI applique le résultat à la référence du seul plan, avec conservation de l’image précédente.

Une référence `/api/studio/jobs/<id>/artifact` est acceptée seulement pour un job image terminé dans cette file, dont le vrai fichier résultat est encore présent. Elle peut donc être utilisée à nouveau sans copier un faux résultat sous `/creative/`.
