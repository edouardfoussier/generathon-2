# Luna/Rafa workshop data

`project.json` describes the **20 actual editorial segments** of the latest 76-second refinement-v4 A/B working cut. It does not use the separate 38-beat proposed shot list, the earlier photographic Cut Room selections, or the new travelling Converse ad.

## Contract

- Project ID: `luna-rafa-v4`; version 1; 24 fps.
- `sourceFilm.urlA/urlB` point to the existing complete local v4 exports. Their picture is identical; their original scores differ. No final user preference between them is claimed.
- Every scene has `id`, `title`, `description`, duration in seconds, a media source with integer `inFrame/outFrame`, an exact edited `previewVideo`, a thumbnail `poster`, a full-resolution `image`, the exact recorded source prompt, references, editable spatial blocking and provenance.
- **Use `image` for the Image tab.** It is a native 1280×720 JPEG extracted from the same exact master frame as the 480×270 thumbnail poster; no upscaling or generated replacement image is involved.
- All media/source-document URLs are server-root absolute `/creative/...` URLs. All frame intervals are **half-open**; `outFrame` is excluded.
- `source.inFrame/outFrame` address the referenced clip, not the assembled film. `provenance.timelineInFrame/timelineOutFrame` address the actual v4 master.
- **Use `previewVideo` for the scene result player.** Its local MP4 is extracted directly from the completed v4 A master and starts at frame 0. It includes the actual editorial recrops, phone captions and v4 A soundtrack/dialogue. It is a locally derived H.264/AAC excerpt at the original 1280×720 / 24 fps, not a newly generated take. The untouched historical source and trim remain in `source` for provenance and editing.
- The three recropped inserts retain their original source clips. Apply `provenance.cropFilter` when reproducing the exact historical picture. `editorialReframe: true` identifies them as recrops rather than newly generated angles. Their posters already show the real finished crop.
- `prompt` is an exact string from an existing job log. A short extracted segment may inherit the full 30-second opening or another multi-shot generation prompt; `promptScope` makes this explicit. Baseline excerpt aliases are documented for `luna-original.mp4` and `salsa-original.mp4`.
- The final card has an empty `prompt`: it was created locally from CS02G and typography. Its editorial instructions and source code are recorded separately, so no generative prompt is invented.
- References come from the current G continuity manifest. CC01G and CS02G refer to corrected current PNGs; earlier versions are not silently substituted. RF06 also includes the physical landscape photograph extracted from FG01.

## 3D blocking

This is a manually seeded **previz starting point**, not motion capture, a solved camera or reconstructed 3D source footage. Character identity/costume is guided by reference sheets; primitive placeholder bodies may be used by the UI. Each scene is editable independently.

Coordinates are in approximate metres, **Y up**, floor at Y=0. The initial camera is generally on positive Z looking toward the action. `lighting.warmth` ranges from 0 to 1 and `intensity` from 0 to 2. A newborn is positioned above ground in the father's arms; this is Luna's future mother, not Luna. The elderly grandparent reference sheets are library references, not additional present-day scenes.

Supported location keys: `attic`, `basketball`, `salsa`, `wedding`, `nursery`, `handover`, `product`. Nursery and handover use the same family-room reference CL05G at different dates.

The source generation prompts intentionally retain their historical **2D gouache** instructions, including restrictions against 3D. A later 3D generation must deliberately adapt those style instructions; the old prompt must not be relabeled as a 3D brief.

## Regenerate the baseline data and local thumbnails

From the repository root:

```sh
python3 creative/scene-studio/seed_project.py
```

Requires Python 3 and local FFmpeg. It reads existing JSON and MP4 files, extracts 20 small 480×270 JPEG posters, 20 native 1280×720 JPEG scene images and 20 frame-aligned MP4 scene previews from the **already rendered v4 A film**, and writes `project.json`. Preview encoding uses H.264 CRF20 / fast and AAC 160 kb/s, up to four jobs in parallel. No network, paid media generation, source-film mutation or editor/render-manifest changes occur.

Use `--skip-posters`, `--skip-images` or `--skip-videos` to preserve the respective derived assets; use all three flags to rebuild only JSON. **Running this seed script resets project.json to the baseline**; save any intentional data edits first. It does not modify browser-local user edits.

Authoritative inputs:

- `../refinement-v4/qa/render-report.json`: twenty exact selected segments, trims and crop expressions.
- `../refinement-v4/plan.json`, scene RF06: the phone take actually integrated.
- `../continuity-video-v1/jobs/opening-g.json`: retained opening source prompt.
- `../gpt-full-film-v1/jobs/*.json`: basketball, salsa, wedding, newborn, handover and return prompts.
- `../continuity-study/manifest.json`: selected source reference URLs and labels.
- `../gpt-full-film-v1/graphics/provenance.json`: editorial end-card provenance.

The phone take RF06 and original FG01 Luna/salsa faces are the choices visibly used in both v4 working exports. RF01–RF04 face trials remain separate alternatives. Browser-local refinement preferences are not available in the repository and are not inferred.
