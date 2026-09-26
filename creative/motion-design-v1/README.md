# Converse — The things we keep

An original 76-second motion-design interpretation of script v3, built from all 18 **Nano Banana 2** continuity sheets. It uses moving illustrated postcards, paper layers, readable native typography, a recurring lace line, and a basketball-to-footwork transition. It is a composed 2D scrapbook film, not a new generative performance of the characters.

The visual reference was the actual 60-second film on slide 11 of [ohmo.ai's Instagram carousel](https://www.instagram.com/p/DdrmutrkgGy/?img_index=11). See `reference-analysis.md` for directly observed details and the limits of that inspection. This film borrows the broad craft of paper collage; its family story, assets, layout and motion are original.

## Story and timing

| Time | Narrative | Motion |
|---|---|---|
| 0–3 | Mum calls Luna | Individually settling magazine-letter tiles |
| 3–9 | Luna enters the attic, annoyed | Layered scenic panel, teenage portrait and a drawn lace |
| 9–13 | Old shoes and Grandpa's photograph | Overlapping tilted paper cards |
| 13–18 | AI has too little data | Legible illustrated phone; response appears in red |
| 18–25 | The shoes open a memory | Shoe push-in; lace becomes an animated path and ball |
| 25–32 | Rafa in the Bronx, 1970 | Court layer, moving basketball and paper jump |
| 32–41 | Meeting Elena, 1977 | Black/red shoes rock together; dancing paper portraits |
| 41–46 | Their wedding, 1978 | Paired wedding portraits, door setting and ring motif |
| 46–52 | Their daughter (Luna’s mum) is born, 1979 | Newborn card expands between parents |
| 52–58 | Passing the shoes on, 1995 | Shoe card travels from father to daughter |
| 58–63 | A life is more than data | A small family archive including older Rafa and Elena |
| 63–68 | Mum calls from downstairs | Return to the attic and Luna's face |
| 68–72 | Luna asks her mum about Grandpa | Daughter, mother and inherited pair connect |
| 72–76 | Converse. Conserve what matters. | Native brand typography and lace underline |

## Production

- Source images: 18 existing Nano Banana 2 sheets, enumerated with IDs in `sources.json`.
- Native composition: `edit.js`, rendered by Higgsedit at 1280 × 720, 24 fps.
- Sound: the existing original score and four English character voice files from `creative/model-comparison-v3/shared/audio`, remixed with the same timing as v3.
- Early black shoes: CS01N, 1970–79. Inherited worn/repaired shoes: CS02N, 1995–2026. Elena's red pair: CS03N, 1977.
- Older grandparents appear as family archive images, not a new funeral or family branch.
- No new paid image or video generation is required for this version. Rendering/hosting has no per-generation debit returned by the tool.

## Edit / reproduce

Stage the 18 source PNGs as `input/<code>.png`. Create the native project once with `higgsedit new /absolute/staging/path/native --size 1280x720 --fps 24`, then register `Caveat:700`, `Anton:400`, `DM Sans:400` and `DM Sans:700` with `higgsedit fonts add /absolute/staging/path/native`. Then run `MOTION_ROOT=/absolute/staging/path MOTION_RENDER=1 higgsedit build edit.js`. The script writes the native project into `native/` and sampled frame proofs into `native/renders/`. `mix_audio.sh` takes the picture-only export, the existing audio directory, and the desired final MP4 path. No signed upload URL is required or stored in this repository.

The motion is native, deterministic and editable. It intentionally animates paper and photographs; it does not claim articulated 3D acting or photoreal movement. Choosing final character/product masters remains a separate production decision.
