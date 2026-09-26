# Refinement comparison page

Open `index.html` via the existing server or directly as a local file. The page supports French and English, remembers the board’s language, and saves one optional preference per comparison locally under a separate storage key. Downloading choices exports JSON; choices do not automatically rebuild a film.

After new outputs arrive, run:

```sh
python3 creative/refinement-v4/build_comparisons.py
```

The build only publishes files that exist and pass FFprobe. It generates posters, `comparison-manifest.json` and portable `comparison-data.js`. Unavailable variants display text without a video player. This does not alter any existing board cards or the approved FG01 file.

Expected picture files are listed in `build_comparisons.py`: original extracts, RF01–RF06 video trials, original FG01 and the two 76-second music alternatives. Music-only MP3s are also included when present. Repainted reference PNGs are shown in a collapsible section. The corrected salsa reference is preferred over its rejected first version when the file exists.

The face-reference request named Nano Banana Pro, but the provider’s completed-job metadata reports Nano Banana 2. The page therefore says “Repainted reference” and discloses that discrepancy; it does not assert a verified Pro generation.

The full rhythm/music alternatives keep FG01’s faces. Face rendering trials remain separate choices. The two phone trials stay available because the first changes the physical photograph from landscape to portrait, while RF06 specifically addresses that raccord.

Optional reviewed notes can be added in `comparison-notes.json` with entries such as:

```json
{
  "luna-prompt": {"fr": "Note vérifiée…", "en": "Verified note…"},
  "film-a": {"fr": "Montage de travail…", "en": "Working cut…"}
}
```

Run the build again to publish those notes. The page does not infer an approved winner from an asset’s availability. Group playback is muted, restarts available face takes together, and stops at the duration of the shortest take. Individual players remain available for complete inspection.
