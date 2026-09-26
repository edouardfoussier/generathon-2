# Painted face references · v4 trials

These are comparison candidates, not a replacement for the approved film or cast.

## Animation inputs

| Scene | Local reference | Durable Arcads image |
| --- | --- | --- |
| Luna, attic reaction | `luna-nano-banana-pro.png` | `production/videoassets/cdca53d3-0ffc-4a71-8efb-7d20b0a8252a.png` |
| Rafa and Elena, salsa meeting | `salsa-nano-banana-pro-corrected.png` | `production/videoassets/8ebe9f55-1b63-4748-8d81-a6e2a18c4e2a.png` |

The filenames record the requested model. Higgsfield accepted `nano_banana_pro` with no model-fallback adjustment, but its completed-job status reports `nano_banana_2`. Exact execution model is therefore unverified. Display label: **Repainted reference — Nano Banana Pro requested; provider metadata says Nano Banana 2**.

Three generated images used 6 Higgsfield credits in total, confirmed by workspace balance 152.37 → 146.37. Registering the two final references in Arcads cost 0 credits.

## Visual review

- **Luna:** visible angular painted cheek/forehead planes and charcoal contours integrate better with the attic. Dark low ponytail, charcoal T-shirt and olive trousers retained. Face reads slightly older than the source sheet; her starting eyeline points left. Test style persistence in animation before any replacement decision.
- **Salsa:** first candidate changed hair and costume details. The one correction restores black curls, violet short sleeves and brown trousers. Faces are much more graphic and cartoon-like than the source sheets. This is a useful strong style test with some identity drift, not an exact identity match.
- **Product continuity:** these are medium face shots. No footwear details are validated here. Keep existing shoe reference assets for wide or shoe-focused scenes.

The corrected salsa sheet and Luna sheet do not yet form a fully uniform new art direction. Compare each with the existing film and the prompt-only Seedance test before choosing.

## Upload finding

Luna's 10,546,667-byte PNG exceeded Arcads' documented 10 MB upload-media limit; temp upload returned success but registration failed with `INVALID_REFERENCE_IMAGES`. Re-encoding the same frame to a high-quality JPEG (`ffmpeg -q:v 2`, 1,133,090 bytes) allowed registration. Arcads serves the persistent asset as PNG. No creative or geometric change was made. The original PNG is retained here.

Full prompts, source IDs, submitted/completed model metadata, QA limitations and persistent paths are in `manifest.json`. No signed URLs are stored.
