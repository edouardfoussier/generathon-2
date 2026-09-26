# Three continuity treatments — Seedance 2.5 opening comparison

**Delivered: three 30-second opening comparisons, Seedance 2.5 at 720p.** Each export has the same English voices, music, readable phone interface and story timing. The Nano ending received one targeted four-second correction after the original transition placed a miniature Rafa inside a giant sock. Its initial comparative version remains in `archive/`; the selected Nano version cuts directly from shoe lacing to a normal-scale court shot.

**Actual total: 3,948 credits** — three original clips at 1,260 credits each, plus one four-second correction at 168 credits. Charges come from each returned asset, not unrelated workspace balance changes. No Seedream or GPT quality reroll was made. The initial connector failure did not return a job ID and is logged separately.

The ready production plan is in `plan.json`. The three films use identical prompts, 30-second duration, 16:9 and 720p, with a different image-model lineage in each film:

| Version | Continuity images |
|---|---|
| N | Nano Banana 2: CC01N, CC02N, CL01N, CL02N, CS02N, CS01N |
| S | Seedream 5 Pro: CC01S, CC02S, CL01S, CL02S, CS02S, CS01S |
| G | GPT Image 2.5 Sunburst: CC01G, CC02G, CL01G, CL02G, CS02G, CS01G |

Each reference has an explicit role: Luna, teenage Rafa, attic, basketball court, inherited shoes in 2026, same shoes before wear in 1970. Multi-view sheets are design references only; the output is a full-frame animated narrative. No source sheet from another image-model family is mixed into a treatment.

## Story and edit

The opening follows script v3: Mom calls Luna to the attic (0–6 s), irritation and discovery (6–15 s), brief AI exchange (15–22 s), putting on the shoes (22–26 s), then a shoe match cut and reveal of young Rafa on the court (26–30 s). No funeral is added. Animation remains hand-painted gouache/watercolor.

`prepare_edit.py` prepares exact, readable 7-second phone inserts and the common 30-second soundtrack. The phone attachment is the corresponding treatment's Rafa portrait from the continuity sheet; it is an editorial crop of an existing asset, not a fourth image-generation source. The opening and annoyed voices and score are reused from the v3 comparison. All three native sequences and the corrected Nano ending are retained alongside the final exports.

`render.py` requires real completed native clips in `videos/opening-{n,s,g}.mp4`; it deliberately fails if a source is absent or too short. It replaces seconds 15–22 with the corresponding phone insert, adds the common audio, exports a 30-second MP4, verifies full decode, and creates sampled review frames. Timing and identity were reviewed through sampled native and edited frames; the limitations below remain visible. The single-clip timing is approximate, while the authored 15–22-second phone insert is exact.

```sh
python3 creative/continuity-video-v1/prepare_edit.py
# Only after real videos have returned and been downloaded:
python3 creative/continuity-video-v1/render.py s
python3 creative/continuity-video-v1/render.py g
python3 creative/continuity-video-v1/render.py n --ending-fix videos/opening-n-ending-fix.mp4
```

The earlier request failed before returning an ID. After service recovery, one request per treatment was accepted and completed. One targeted Nano ending correction was then accepted and completed. Preserve asset IDs and actual credit charges in `jobs/`, never signed download URLs. Approved batch ceiling: 5,000 credits. Final spend: 3,948 credits; no further generations are pending.

## Visual review

The first native clips were inspected through 16 sampled frames each plus the final frame; edited exports through nine sampled frames each. Full decode, 30-second duration, 720-frame count, 1280×720 dimensions and audio presence were verified. This is sampled visual review, not frame-by-frame playback.

- **Nano:** coherent Luna, attic and box discovery. The initial final transition failed with a miniature figure superposed in an oversized sock; see the archived first-pass film and contact sheet. The selected four-second replacement uses one normal-scale Rafa and a direct editorial cut. Its camera push is stronger than requested and crops his feet late; the face, ball and body remain coherent in sampled frames. The initial lettering is not as clearly emphasized as in the other treatments.
- **Seedream:** clear R.M. inside the tongue, convincing box discovery and shoe lacing. An oversized foreground shoe briefly remains during the court transition, then Rafa returns to normal full-body scale. Keep that limitation visible for comparison.
- **GPT:** clear photo/initials and a coherent change to the court. The upward camera move reaches Rafa's face only in the last moments, so a later edit should give the reveal more breathing room.
- Seedance smooths the three painted source families toward a cinematic illustrated appearance. These results do not preserve every brush edge of the stills or prove production-ready footwear consistency.

## Exports

- [Nano Banana assets → Seedance, corrected ending](renders/converse-continuity-n-seedance25-30s.mp4)
- [Seedream assets → Seedance](renders/converse-continuity-s-seedance25-30s.mp4)
- [GPT Image assets → Seedance](renders/converse-continuity-g-seedance25-30s.mp4)
- [Nano original before ending correction](archive/first-pass-converse-continuity-n-seedance25-30s.mp4)

All selected exports are 1280×720, 24 fps, exactly 720 frames / 30.000 seconds, H.264 with stereo AAC audio. The common WAV peaks at −1.5 dBFS and the AAC exports at −1.4 dBFS in the measured check, with no clipping. `manifest.json` supplies the board integration contract; `credits.json` contains final per-asset charges; `qa/` contains technical metadata and sampled review sheets.
