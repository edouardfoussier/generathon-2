# Converse — Generathon 2026

Creative workspace for the **Sell the Feeling — Ads** track: an emotional Gen-AI product ad exploring **“One Sneaker, Every Generation.”** The repository contains a bilingual selection board, original exploratory images, generation records and working story notes.

## Current direction

**Rafa did not say much. His shoes have stories to tell.** Fifteen-year-old Luna discovers her grandfather through his worn black Converse: basketball, meeting Elena at a salsa dance, and quietly caring for his daughter. Luna carries that story forward on her skateboard.

Working tagline: **“Converse. Conserve what matters.”** One proposed visual rule is a photographic present that changes into animated memories when Luna first steps into the shoes. Pixel art, clay, illustration and mixed-media treatments remain options to compare. The story, casting, style and six final key images are **not locked**.

Deliverables from the supplied brief:

- Main ad: **80 seconds maximum**; the current story proposal targets 70 seconds.
- Face-camera explanation: **60 seconds maximum**, covering inspiration, concept, process, challenges, accomplishments, learning, next steps and tools.
- The track slide also calls for a **complete one-shot sequence**. Resolve this in the final staging and transitions; the exploratory stills do not establish compliance.

**There is no generated final film in this repository.** All generated media currently included are exploratory still images; motion and temporal consistency remain untested.

## Open the board

Open [`creative/selection/index.html`](creative/selection/index.html) directly in a browser, keeping its companion files and image folders together. There is no build step or package installation.

Alternatively, from the repository root:

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory creative/selection
```

Then open [the English board](http://127.0.0.1:8765/?lang=en). Use the **FR / EN** switch at any time. Direct tab links accept `?category=equipe&lang=en` for **Team directions** and `?category=hybrides&lang=en` for **Pixel & hybrids**.

Click an image to enlarge it and **Choose** to favorite it. **Copy the codes** shares a compact selection; **Download JSON** preserves an export. Favorites live in each browser’s local storage, are separate between file and localhost addresses, and are **not synchronized with teammates**.

## The 50-image board

| Codes | Count | Exploration |
|---|---:|---|
| E01–E06 | 6 | Child casting |
| G01–G04 | 4 | Grandfather casting |
| P01–P04 | 4 | Shoe colors, wear and repair |
| D01–D06 | 6 | Attics and lighting |
| S00–S08 | 9 | Shared baseline and eight visual styles |
| T01–T08, U01–U05 | 13 | Team story scenes, alternate future and style treatments |
| H01–H05, X01–X03 | 8 | Pixels, clay, mixed materials and three stills for a proposed style transition |

## Where to continue

- [`creative/converse-team-directions-v3.md`](creative/converse-team-directions-v3.md): current story, proposed 70-second structure, family chronology and sources; includes an English synopsis.
- [`creative/converse-style-switch-v4.md`](creative/converse-style-switch-v4.md): latest visual direction and proposed five-second transition test; includes English notes.
- [`creative/converse-direction-v1.md`](creative/converse-direction-v1.md): earlier concept exploration.
- [`creative/selection/README.md`](creative/selection/README.md): detailed board guide and generation notes.
- `creative/selection/index.html`, `board.js`, `i18n.js` and `assets.js`: layout, interactions, interface translations and bilingual card metadata.
- `creative/selection/assets/`: original images; `assets/archive/` contains retained superseded tests.
- `creative/selection/manifest.json` and the `*generation-log.json` files: Arcads asset IDs, prompts, reference lineage, attempts and reported costs. Current images were generated with **Nano Banana 2 through Arcads**.
- `creative/selection/references/`: supplied style reference, saved inspiration links and observations.

Preserve existing asset codes and original images when adding tests. Give alternatives new codes or archive replaced versions, update both language captions, and record prompts, references and actual generation costs. Before producing final shots, agree on the cast, shoe details and visual treatment, then test a short movement sequence for identity, product fidelity and transition stability.
