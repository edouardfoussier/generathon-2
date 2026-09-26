# Converse — Generathon 2026

Creative workspace for the **Sell the Feeling — Ads** track: an emotional Gen-AI product ad exploring **“One Sneaker, Every Generation.”** The repository contains a bilingual selection board, original exploratory images, short transition tests, generation records and working story notes.

## Current direction

**Rafa did not say much. His shoes have stories to tell.** Fifteen-year-old Luna discovers her grandfather through his worn black Converse: basketball, meeting Elena at a salsa dance, and quietly caring for his daughter. Luna carries that story forward on her skateboard.

Working tagline: **“Converse. Conserve what matters.”** The latest [cinematic script v2](creative/converse-cinematic-script-v2.md) proposes a **76-second photographic version with 26 editorial shots**, opening in the attic, moving through three memories, and reconnecting Luna with her mother and grandmother in the present. Pixel art, clay, illustration and a photographic-to-animated transition remain archived alternatives. **Current choices:** Luna’s existing face, G01 for the grandfather, D06 for the attic, and photographic realism for the current tests. The younger grandfather, orange costume alternative, final story and six final key images remain open.

Deliverables from the supplied brief:

- Main ad: **80 seconds maximum**; the consolidated story proposal targets 76 seconds including four seconds of final text.
- Face-camera explanation: **60 seconds maximum**, covering inspiration, concept, process, challenges, accomplishments, learning, next steps and tools.
- **Cuts are allowed for Converse.** The user clarified that the one-shot rule applies only to teams choosing a brand outside the suggested list; this project is exempt.

**There is no assembled final film in this repository.** K01–K06 are the first scene candidates. TR01–TR03 compare short present-to-memory transitions; their individual notes describe observed results and continuity faults. They do not validate the complete ad.

## Open the board

Open [`creative/selection/index.html`](creative/selection/index.html) directly in a browser, keeping its companion files and image folders together. There is no build step or package installation.

Alternatively, from the repository root:

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory creative/selection
```

Then open [the English board](http://127.0.0.1:8765/?lang=en). Use the **FR / EN** switch at any time. Direct tab links accept `?category=equipe&lang=en` for **Team directions** and `?category=hybrides&lang=en` for **Pixel & hybrids**.

Click an image to enlarge it and **Choose** to favorite it. **Copy the codes** shares a compact selection; **Download JSON** preserves an export. Favorites live in each browser’s local storage, are separate between file and localhost addresses, and are **not synchronized with teammates**.

## The 80-reference board

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

The latest tab is **Scenes & transitions** (`?category=scenes&lang=en`): six scene candidates followed by three playable transition comparisons. The board now contains 77 stills and three clips. **Characters & locations** (`?category=production&lang=en`) includes the new Grandma & Mom group alongside character bibles and location studies. The first scenes use Luna’s original wardrobe; orange remains an alternative.

## Where to continue

**Start with the [bilingual cinematic script v2](creative/converse-cinematic-script-v2.md)** and its [editable 26-shot list](creative/converse-shot-list-v2.csv). It specifies framing, movement, actor direction, sound, animated transitions and plain-language cinema vocabulary. A shorter production route reduces the shot count while preserving the 76-second story. Editorial shots are not a one-to-one count of generation jobs.

The [production bible v1](creative/converse-production-bible-v1.md) and its [13-beat list](creative/converse-shot-list-v1.csv) remain the previous 75-second version and source of reference history. The new script is proposed, not automatically approved by the team. K01–K06 remain starter images and will need derived framing and updated supporting cast.

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
- `creative/selection/manifest.json` and the `*generation-log.json` files: Arcads asset IDs, prompts, reference lineage, attempts and reported costs. Images were generated with **Nano Banana 2 through Arcads**; the current motion tests use **Kling 3 Pro through Arcads**.
- `creative/selection/references/`: supplied style reference, saved inspiration links and observations.

Preserve existing asset codes and original images when adding tests. Give alternatives new codes or archive replaced versions, update both language captions, and record prompts, references and actual generation costs. Before producing final shots, agree on the cast, shoe details and visual treatment, then test a short movement sequence for identity, product fidelity and transition stability.
