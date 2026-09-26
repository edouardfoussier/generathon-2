# Converse — Animatic v1

26 September 2026 · Cinematic script v2 · Exploratory first cut / Premier montage de travail

**76 seconds · 26 shots · 1920 × 1080 · 24 fps · English voice and original instrumental music.**

[Watch / download MP4](renders/converse-animatic-v1.mp4) · [Visual board](../selection/index.html?category=animatic) · [Cinematic script FR / EN](../converse-cinematic-script-v2.md) · [Higgsfield methods](../converse-higgsfield-workflow-notes.md)

## Ce que nous regardons / What we are watching

**FR.** Une première lecture complète du scénario, pour juger le rythme, la compréhension des liens familiaux et l'émotion. Les trois lots — ouverture, souvenirs, famille — ont été fabriqués en parallèle. Les 26 plans couvrent toute la durée : 21 utilisent une source vidéo générée, cinq sont des inserts fixes mis en scène au montage. Cela représente 62 secondes de source animée et 14 secondes d'inserts. Ce n'est pas encore une publicité finalisée.

**EN.** A complete first reading of the script to assess pacing, family relationships and emotion. Opening, memories and family passages were produced in parallel. All 26 shots are covered: 21 use generated video and five are still inserts staged in the edit, totaling 62 seconds of animated source and 14 seconds of inserts. This is not yet a finished commercial.

## Edit decisions

| Time | Chapter | Main editorial choice |
|---|---|---|
| 0–18 s | Discovery | Maternal voice starts before her face; photos identify the grandfather; a brief whip-pan introduces memory. |
| 18–26 s | Basketball, around 1970 | Young Rafa's face, stance and shoe-level pivot. |
| 26–41 s | Meeting Elena, around 1977 | Pivot into dance, invitation, hand contact and two reactions. |
| 41–53 s | Care, around 1995 | The shoes are on teenage Mom; her father attends to the lace; her reaction leads back to today. |
| 53–66 s | The living family, 2026 | Adult Mom, Luna's recognition, Elena's offered hand, three-generation contact. |
| 66–76 s | Her next chapter | Initials, skateboard, one calm step; signature held for four seconds. |

The final title uses editable type, not the official vector Converse wordmark. Initials are also composed in the edit. S24 has no generated writing hand. S25 uses the clean still after two video variants invented markings on the skateboard.

Five still inserts: **S01, S04, S16, S24, S25**. A restrained digital push is used except on the flat initials insert. They are explicitly identified in the source map.

## Audio

- Original 76-second instrumental score generated through Arcads / ElevenLabs.
- Mom's off-screen English line: **“They were his. I used to borrow them.”** Voice: Judy, `0MZvYbRLO42EDBtYDHZX`.
- The original short take was transcribed successfully. In the edit, its two phrases are separated, slowed to 80% with pitch-preserving `atempo`, and placed at 5.0 and 7.5 seconds. Music ducks underneath them.
- Generated clip audio is removed from the delivery. This avoids mismatched music or accidental speech between shots.
- The sound mix is temporary: dedicated room tone, lace friction, shoe squeaks and other production foley remain to be designed. No claim is made that sampled visual QA constitutes a full listening review.

## Production and cost

20 reference-image generations, including corrections; 20 video generations, including two rejected skateboard variants; one previously generated transition reused. The selected cut uses 18 new video masters plus that transition, with two reaction masters each used twice.

| Arcads production unit | Actual credits |
|---|---:|
| Opening and ending | 1,680 |
| Basketball and dance memories | 1,968 |
| Mother and grandmother | 1,776 |
| Original score and voice | 32 |
| **Total for this batch** | **5,456** |

Balance: **48,454 → 42,998**. The first images were covered by the daily allowance; subsequent Nano Banana 2 images cost 16 credits. Rejected takes are included in the cost. Native assembly does not create additional Arcads generation jobs. See [credits.json](credits.json) and unit logs for asset IDs and actual charges.

Independent jobs were submitted in parallel through three production agents. This demonstrates accepted overlapping jobs for this run; it does not establish Arcads' contractual or technical maximum concurrency.

## Sources and reproducibility

- [Full 26-shot source map](edit/timeline.json): local paths, asset IDs, source in-points, durations and QA notes.
- [Opening](opening/shot-map.json), [memories](memories/shot-map.json), [family](family/shot-map.json): unit-level decisions.
- [Native edit script](edit/edit.js): Higgsedit picture assembly, crop, initials and closing title.
- [Audio mix command](edit/mix_audio.sh): repeatable final mix and MP4 mux.
- [Review priorities](review-priorities.md): five ranked improvements before the final commercial.

To rebuild with a compatible Higgsedit runtime and FFmpeg, run from the repository root:

```sh
python3 creative/animatic-v1/edit/collect_timeline.py
higgsedit build creative/animatic-v1/edit/edit.js
sh creative/animatic-v1/edit/mix_audio.sh
```

Higgsedit was run in the connected Higgsfield sandbox; it is not installed on the author's Mac. The local sources and scripts are retained. The exported recipe archive contains scripts and render evidence, **not** a self-contained media archive or a hosted editable project.

## Remaining limitations / Limites connues

**FR.** Le passage présent → souvenir réutilise TR02 et présente un changement d'orientation de la chaussure. Le raccord basket → danse reste approximatif. Coutures, ourlets, accessoires du grenier et échelle des visages varient entre certains plans. Le recadrage d'Elena en S14 retire une épaule de mauvaise couleur. La priorité suivante est une séance de visionnage collectif, puis des reprises ciblées des raccords et du produit.

**EN.** Present → memory reuses TR02 with a change in shoe orientation. Basketball → dance is still an approximate match. Repairs, cuffs, attic props and face scale differ between some shots. S14 is cropped to remove an incorrect foreground shirt. The next step is a team viewing, then targeted continuity and product corrections.

Visual source checks used sampled frames and selected full-resolution frames, not uninterrupted perceptual playback. Final export checks are recorded separately in `renders/qa-report.json`.
