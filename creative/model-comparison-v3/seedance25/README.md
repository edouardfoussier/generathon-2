# Seedance 2.5 — script v3 motion coverage

Fresh motion generated from the same shared opening-frame references used by the comparison models. Native output is requested at 1080p, landscape 16:9, without audio. The final comparison edit adds a common soundtrack and graphics.

The video model accepts a minimum of four seconds, so short inserts are generated at four seconds and trimmed to the approved 76-second timeline. The editorial phone insert and opening black frame are shared across all comparison films.

Generation records are saved immediately in per-shot JSON files and `generation-log.json`. The final `shot-map.json` records selected source ranges and review notes. `qa_frames.py` probes video metadata and produces five-frame contact sheets; this supports visual review but is not a claim of frame-by-frame viewing.

Confirmed price at submission: 416 credits for a four-second silent 1080p clip (104 credits per generated second). The 17 first-pass clips request 78 seconds in total, an estimated 8,112 credits before any correction retry.

## Completed delivery

All 17 requested clips generated successfully with no retries. Actual cost: **8,112 credits**. Every source is 1920×1080, 24 fps, silent. Sources are one frame longer than their requested whole-second durations; selected ranges in `shot-map.json` stay within the source bounds.

The selected motion covers 68 seconds of the 76-second film; opening black and the phone interface are eight seconds of shared editorial inserts assembled by the main comparison edit.

Highlights: quiet facial performances, controlled basketball action, the wedding tilt, securely held newborn, and a readable gift sequence with native cuts from father/daughter to lace detail and back.

First-pass limitations: salsa remains restrained; shoe scuff details drift slightly in the gift sequence; the return shot introduces a second photo on a stool and uses an older portrait rather than the basketball photograph. These are retained and documented as model comparison findings. The final line can remain offscreen because Luna turns away from the camera.

All clips received metadata checks and a five-frame contact-sheet review. Contact sheets are in `qa/`; this is sampled visual QA, not a claim of full frame-by-frame playback.
