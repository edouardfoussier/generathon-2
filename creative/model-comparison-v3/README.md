# Three-model comparison — approved script v3

Three complete **76-second experimental cuts** of the team's revised script: Seedance 2.5, Kling 3 Pro and Veo 3.1, generated through Arcads on 26 September 2026. Generation ran in parallel across three model workers. Each cut contains 17 fresh motion shots, a shared seven-second phone insert and one second of black at the opening.

Story and timings follow `../converse-cinematic-script-v3.md`. Shared character references, still anchors, dialogue, score, graphics and edit timings allow practical comparison. These are edited multi-clip films, not single uninterrupted model generations; model APIs and native resolutions differ.

## Watch and compare

The selection board's **Animatic** tab lists the new versions first. AV01 remains the earlier script-v2 film.

| Board card | Model | Film | Motion credits |
|---|---|---|---:|
| AV02 | Seedance 2.5 | [76-second cut](renders/converse-v3-seedance25.mp4) | 8,112 |
| AV03 | Kling 3 Pro | [76-second cut](renders/converse-v3-kling3.mp4) | 3,856 |
| AV04 | Veo 3.1 | [76-second cut](renders/converse-v3-veo31.mp4) | 14,400 |

**Start with Kling** as a working baseline. The sampled footage gives clear continuous staging, especially for the shoe gift. Seedance supplies useful close-up coverage within that gift; Veo brings more active dancing. See [grounded comparison notes](comparison-notes.md) for details and limitations.

All three exports target 1920×1080 at 24 fps, with H.264 video, AAC audio and a duration of 76 seconds. They share the same original score, scratch English dialogue, readable phone exchange and four-second endline. These first complete edits support creative selection; they are not a final approved commercial.

Export checks passed for all three: exactly 76.000 seconds, 1080p/24 fps, AAC audio at 48 kHz, complete decode without warnings, and no black intervals beyond the intentional opening second. Twenty frames per finished film were sampled and reviewed, in addition to source-clip checks. Audio samples peak at −1.4 dBFS after encoding. See [renders/qa-report.json](renders/qa-report.json); these checks do not constitute a full normal-speed viewing or listening pass.

## What remains for a final commercial

- Watch all three at normal speed and choose performances shot by shot. Sampled visual review cannot establish every movement or lip-sync detail.
- Refine product marks, repair shape, photo continuity and shoe-scale matches at the memory cuts. Seedance's return briefly adds another photograph; Veo's first court-shoe take was replaced after it invented a badge.
- The shared voices are scratch casting. Mom's catalog voice is labelled English with a Spanish accent, not verified Puerto Rican delivery. Dialogue was checked by transcription and retimed; exact lip synchronization and full listening review remain.
- Finish location ambience, foley and final music timing. Native generated audio is muted so the comparison uses the same sound bed.
- Replace the typographic **CONVERSE.** treatment with the approved wordmark asset. The current endline is clean editable typography, not a claim to use the official brand font.

## Files and reproduction

Each model folder includes source clips, a generation log, sampled QA, a shot map and a normalized timeline with exact selected ranges. Shared references and audio are under `shared/`.

`edit.js` is the native Higgsedit recipe. It uses only supported native media, shape and text compositions. In an environment with the matching Higgsedit CLI, set `CONVERSE_WORK` to this directory and `CONVERSE_MODEL` to the desired folder name, then run `higgsedit build edit.js`. Run `mix_audio.sh` with the picture-only export, `shared/audio` and the desired output path. The CLI was unavailable on the local desktop, so these edits were rendered in Higgsfield's hosted toolchain.

`render_batch.py` documents the hosted orchestration. Its private input URL manifests and upload credentials are deliberately not committed. The exported recipe/proof archive excludes source media and is not a self-contained editable project; source media is retained in this repository.

The public model names describe the motion-generation tool used. The still anchors use Nano Banana 2. Shared phone graphics, text, music and voices belong to the edit. APIs, source durations and selected trims differ; this is a practical creative comparison rather than a controlled model benchmark.

Total actual cost: **26,648 credits**: 26,368 for motion, 224 for shared images and 56 for audio. The balance went from 42,998 to 16,350 credits. This includes 52 motion jobs (51 selected clips plus one Veo correction) and 14 shared image jobs (12 selected anchors plus two corrections). Transcription cost 0 credits. See [credits.json](credits.json).

The official Arcads concurrency limit was not exposed by the connected tool catalog. Three independent model workers submitted in parallel without observed rate-limit failures; this does not establish a service-wide maximum.
