# Converse — Generathon 2026

Creative workspace for the **Sell the Feeling — Ads** track: an emotional Gen-AI product ad exploring **“One Sneaker, Every Generation.”** The repository contains a bilingual selection board, original exploratory images, short transition tests, generation records and working story notes.

## Current direction

**Rafa did not say much. His shoes have stories to tell.** Sent to fetch her mother’s winter clothes, fifteen-year-old Luna complains about the old things in the attic. A worn pair of black Converse leads her through her grandfather’s life: basketball, meeting Elena, their wedding, becoming a father and passing the shoes to his daughter. Back in the present, Luna asks her mother to tell her about Grandpa.

Working tagline: **“Converse. Conserve what matters.”** The latest [cinematic script v3](creative/converse-cinematic-script-v3.md) is the **76-second photographic story used for the current three-model comparison**. Its brief phone/AI moment gives way to memories carried by the shoes and a final conversation with Mom. Veo is the preferred photographic rendering. A fresh gouache/ink study now explores an illustrated alternative; pixel art, clay and a photographic-to-animated transition remain earlier explorations. **Current references:** Luna’s existing face and original wardrobe, G01 and its younger derivatives for Rafa, and D06 for the attic. Orange remains a costume alternative.

Deliverables from the supplied brief:

- Main ad: **80 seconds maximum**; the consolidated story proposal targets 76 seconds including four seconds of final text.
- Face-camera explanation: **60 seconds maximum**, covering inspiration, concept, process, challenges, accomplishments, learning, next steps and tools.
- **Cuts are allowed for Converse.** The user clarified that the one-shot rule applies only to teams choosing a brand outside the suggested list; this project is exempt.

**[The current comparison uses Seedance 2.5, Kling 3 Pro and Veo 3.1](creative/model-comparison-v3/README.md).** AV02–AV04 are the three complete 76-second script-v3 comparison cuts. Each model generates fresh motion from shared reference stills; the phone interface, temporary English voices and music are common to all three. These are exploratory cuts for team review, not approved final advertising.

**[Animatic v1 remains available as AV01](creative/animatic-v1/README.md).** Its 76-second, 26-shot script-v2 edit combines 21 video-based shots, five still inserts, a score and an English maternal voice line. K01–K06 and TR01–TR03 remain the source explorations.

## Build your own edit

[Converse Cut Room](creative/editor/README.md) compares the three complete films with synchronized previews, three source tracks, a final cut track, split/trim/reorder controls and MP4 export. **Veo starts selected throughout.**

```sh
python3 creative/editor/server.py
```

Open **http://127.0.0.1:8787/**. This is a local editing room, not a publicly hosted collaborative site. Teammates can clone this repo, run the same command, and exchange edits using **Save edit / Open edit** JSON files. Python 3.10+, FFmpeg and FFprobe are required. Output is 1080p/24 fps, with a shared soundtrack and an 80-second limit. Source videos stay unchanged.

[The illustrated style study](creative/sketch-study/README.md) reinterprets six keyframes in both textured gouache and ink/hatching. Two Veo 3.1 motion tests explore basketball and the father–daughter shoe handover. These are style tests; the photographic version remains available.

## Open the board

Open [`creative/selection/index.html`](creative/selection/index.html) directly in a browser, keeping its companion files and image folders together. There is no build step or package installation.

Alternatively, from the repository root:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Then open [the English animatic board](http://127.0.0.1:8765/creative/selection/?category=animatic&lang=en). Serve the repository root so the sibling animatic media folder is accessible. Use the **FR / EN** switch at any time. Direct tab links also accept `?category=equipe&lang=en` for **Team directions** and `?category=hybrides&lang=en` for **Pixel & hybrids**.

Click an image to enlarge it and **Choose** to favorite it. **Copy the codes** shares a compact selection; **Download JSON** preserves an export. Favorites live in each browser’s local storage, are separate between file and localhost addresses, and are **not synchronized with teammates**.

## The 98-entry board

| Codes | Count | Exploration |
|---|---:|---|
| E01–E06 | 6 | Child casting |
| G01–G04 | 4 | Grandfather casting |
| P01–P04 | 4 | Shoe colors, wear and repair |
| D01–D06 | 6 | Attics and lighting |
| S00–S08 | 9 | Shared baseline and eight visual styles |
| T01–T08, U01–U05 | 13 | Team story scenes, alternate future and style treatments |
| H01–H05, X01–X03 | 8 | Pixels, clay, mixed materials and three stills for a proposed style transition |
| L01–L05, G11–G15, R01–R07 | 17 | Realistic Luna character sheets, grandfather development from G01, and scene locations from D06 |
| K01–K06, TR01–TR03 | 9 | Six scene keyframes and three short transition videos |
| EL01–EL02, M01–M02 | 4 | Grandma Elena and Luna’s mother, with present-day character sheets and comparisons across ages |
| AV01 | 1 | Complete 76-second first animatic with music and English voice |
| AV02–AV04 | 3 | Script v3 comparison: Seedance 2.5, Kling 3 Pro and Veo 3.1, 76 seconds each |
| Illustrated study | 14 | Six gouache keyframes, six ink keyframes and two Veo animated tests |

The latest tab is **Illustrated** (`?category=illustrated&lang=en`). **Animatics** (`?category=animatic&lang=en`) retains the full comparison films and links to Cut Room. The board contains 89 stills, five short clips and four full animatic entries: the three new script-v3 comparisons appear before the preserved AV01 script-v2 cut. **Scenes & transitions** retains the six keyframes and short comparisons; **Characters & locations** retains the Grandma & Mom group. Luna’s original wardrobe is used; orange remains an alternative.

## Where to continue

**Start with [cinematic script v3](creative/converse-cinematic-script-v3.md)** and the [three-model production notes](creative/model-comparison-v3/README.md). The [shared shot plan](creative/model-comparison-v3/plan.json) defines the current timing and prompts. Each model’s folder records its generated clips, source ranges and observed limitations. Editorial shots are not a one-to-one count of generation jobs.

The [bilingual cinematic script v2](creative/converse-cinematic-script-v2.md) and its [26-shot list](creative/converse-shot-list-v2.csv) remain the source of AV01 and cinema vocabulary notes. The [production bible v1](creative/converse-production-bible-v1.md) and its [13-beat list](creative/converse-shot-list-v1.csv) preserve the earlier 75-second version and reference history. Generation of the comparison does not imply approval of its individual shots or the final commercial.

- [`creative/converse-family-casting-v1.md`](creative/converse-family-casting-v1.md): Grandma Elena and Luna’s mother, chronology, acting direction and reference lineage.
- [`creative/luna-character-bible-v1.md`](creative/luna-character-bible-v1.md): latest character references, costume options, chosen attic and continuity notes.
- [`creative/converse-transition-tests-v1.md`](creative/converse-transition-tests-v1.md): transition comparison, observed limits, cost and concurrency notes.
- `creative/selection/creative-choices.json`: explicit team choices, distinct from each browser’s favorites.
- [`creative/converse-team-directions-v3.md`](creative/converse-team-directions-v3.md): earlier 70-second story proposal, family chronology and research sources; retained as development history.
- [`creative/converse-style-switch-v4.md`](creative/converse-style-switch-v4.md): archived material-switch direction and proposed five-second transition test; includes English notes.
- [`creative/converse-direction-v1.md`](creative/converse-direction-v1.md): earlier concept exploration.
- [`creative/selection/README.md`](creative/selection/README.md): detailed board guide and generation notes.
- `creative/selection/index.html`, `board.js`, `i18n.js` and `assets.js`: layout, interactions, interface translations and bilingual card metadata.
- `creative/selection/assets/`: original images; `assets/archive/` contains retained superseded tests.
- `creative/selection/manifest.json` and the `*generation-log.json` files: Arcads asset IDs, prompts, reference lineage, attempts and reported costs. Images use **Nano Banana 2 through Arcads**; the script-v3 comparison uses **Seedance 2.5, Kling 3 Pro and Veo 3.1 through Arcads**.
- `creative/selection/references/`: supplied style reference, saved inspiration links and observations.

Preserve existing asset codes and original images when adding tests. Give alternatives new codes or archive replaced versions, update both language captions, and record prompts, references and actual generation costs. Before producing final shots, agree on the cast, shoe details and visual treatment, then test a short movement sequence for identity, product fidelity and transition stability.
