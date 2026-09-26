# Converse — Refinements v4

A comparison workshop for improving the approved 76-second FG01 film. Open [Raffinements / Refinements](index.html?lang=en), or use the new link in the selection board. It works from the local server and from a file URL. The 157 existing board cards and FG01 remain unchanged.

## What to compare

- **Faces:** original Luna and salsa footage, new Seedance 2.5 takes using a more explicit painting prompt and the original GPT references, then the same action/prompt with genuinely repainted scene references. These are stochastic creative comparisons, not identical-motion scientific controls. Framing, gesture and sometimes identity also change.
- **Phone:** original flat graphic, first in-world attempt, and a second attempt conditioned on the physical landscape photograph from FG01. Review the physical print, camera preview, hand positions and expression together.
- **Music and rhythm:** two complete 76-second alternative edits, with identical picture and different original ElevenLabs scores via Arcads. FG01 faces remain in these edits so the experimental casting changes can be chosen separately. The new phone scene, three editorial crop inserts and earlier Mom call are shared by both alternatives.

The script v2 was produced in animatic v1. V3 deliberately changed the story. The [audit](script-audit.md) recovers the detailed craft without undoing that rewrite. The [38-beat v4 shot proposal](v4-shot-plan.md) is a proposed production plan, not a claim that 38 new shots have already been generated.

## Provenance and current limits

Video model: Seedance 2.5 through Arcads, 720p/24 fps, silent source takes. Final dialogue and music are mixed separately. Original GPT-reference shots are copied from existing source media, with all three crop inserts explicitly identified in `qa/render-report.json`.

Repainted references: Nano Banana Pro was requested and accepted by Higgsfield, but completed-job metadata reports Nano Banana 2. The execution model is therefore unverified and the UI calls them **repainted references**, with the discrepancy disclosed. See [reference manifest](faces/references/manifest.json) and [visual review](faces/references/README.md). Three image generations include one costume/hair correction; no cast change is automatically approved.

Audio: two original 76-second music requests, plus two short phone lines. The first musical source arrived longer than requested; its ending is preserved in a reproducible 76-second edit. Luna uses the same Lauren voice as the earlier film; the device reply uses Ryan. The two dialogues are offscreen, with the question timed to finish before the frontal phone shot. [Music provenance, transcripts and technical limits](music/README.md).

The comparison page saves selections only in this browser, and can export them as JSON for teammates. It does not change the master edit or perform automatic shot selection.

## Reproduce

From the repository root, after reviewing all required source clips:

```sh
python3 creative/refinement-v4/render.py \
  --luna luna-original.mp4 --salsa salsa-original.mp4 \
  --phone phone-attic-v2.mp4 \
  --music-a creative/refinement-v4/music/organic-latin-breakbeat-76s.wav \
  --music-b creative/refinement-v4/music/tactile-percussion-piano-76s.wav \
  --ask creative/refinement-v4/music/luna-phone-question-paced.wav \
  --reply creative/refinement-v4/music/device-phone-reply-paced.wav
python3 creative/refinement-v4/qa_frames.py
python3 creative/refinement-v4/build_comparisons.py
```

`build_comparisons.py` publishes only local media that FFprobe can read. The render refuses missing/short clips and requires 1,824 output frames (76 seconds at 24 fps), followed by a full decode check. Editorial face comparisons remain muted so rhythm and identity can be judged independently.

## Delivered review

Both complete exports are 76.000 seconds, 1,824 frames, with matching decoded picture across music A/B and a successful full decode. RF06 is used for the phone passage. Its landscape photo matches the source composition; fine details are not pixel-identical. The question ends just before the frontal cut. Luna's repainted-reference trial offers the clearest skin-texture improvement; the repainted salsa trial becomes a bolder cartoon treatment. Neither is automatically substituted into the full soundtrack edits.

New spend: **1,576 Arcads credits** (1,512 for six video takes, 48 for music, 16 for dialogue) and **6 Higgsfield credits** for three image generations. Observed Arcads balance after this batch: **3,048**. See [ledger](credits.json).

Visual QA is based on sampled frames, including full-resolution details and a final contact sheet; technical decoding covers each complete file. Music checks cover duration, levels, transcripts and timing. Perceptual audition by the team remains the basis for choosing a score.
