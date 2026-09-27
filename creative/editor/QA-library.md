# Cut Room library and regeneration — 27 September 2026

## Verified

- Initial full inventory: 520 media (159 videos, 326 images, 35 audio); four Suno master/preview files were added afterward. Inventory is refreshed from disk, not hard-coded.
- Gallery filters, localized FR/EN titles, real cached video thumbnails and source preview checked in the in-app browser.
- Replaced a six-second initial shot with the 122-frame v5 match cut. Source in point reset to zero; project became 75 seconds and 2 frames.
- Inserted a two-second Luna extract after the selected shot: 19 shots, 77 seconds and 2 frames.
- Started a new two-second edit from the chosen Luna clip. Source mode, trim and selection remained valid.
- Selected Suno take 1 as soundtrack and reloaded the browser: selected track and edit restored correctly.
- Exported this real two-second edit through the UI. The MP4 completed successfully at 1080p/24 fps. Browser console had no reported errors.
- Generation form retrieves server model availability, prefills available prompts, and uses the selected clip's in point or a chosen image.
- Verification used a separate localhost storage origin, leaving the user's saved `127.0.0.1` edit untouched.

## Gallery hover previews

- Pointer hover plays one muted, looping video after a short delay; leaving the card releases the video and restores its poster. No video files are loaded for idle cards.
- Keyboard focus also previews videos. Touch taps keep the existing click-to-open behavior; reduced-motion preferences disable automatic previews.
- Browser verification: hovered shoe clip played (`readyState: 4`, muted, looping, advancing time); pointer exit removed it. Keyboard navigation switched the single player to the next clip. Opening the full preview removed the hover player and preserved the normal modal. Filters cleared previews; no browser console errors were reported.
- Previews are also cleared on gallery re-render, close, scroll, tab hiding and window blur.

## Automated checks

- `node --test creative/editor/model.test.mjs`: 20 passing tests, including variable source bounds, insertion, replacement, new edit and audio recipe settings.
- `python3 creative/editor/test_generation.py`: 11 passing tests, with a fake provider; no charges.
- Existing server suite: real three-film smoke passed (72 exact frames, Veo audio correlation 0.99933).
- Library suite: mixed-rate/silent source export, soundtrack replacement, stable IDs, manifest provenance, path containment, poster cache/concurrency and malformed video checks passed.
- `git diff --check`: clean.

## Provider integration

A four-second Seedance 2.5 test using K06 (Luna–mother) reached the provider and was refused by its people/privacy filter (`content_policy_violation`, `partner_validation_failed`). Job `5f1d7d41a2844b4eb598419cc48fc6c5` is explicitly failed; its original is intact and it was not retried. The UI preserves the reason. Do not treat face-heavy Seedance generation as verified on this FAL account.

A separate four-second product-only shoe test using T01A completed successfully: job `4e10441161c6419eb04f6c70725244cc`. Output: `generated/4e10441161c6419eb04f6c70725244cc/media.mp4`, 1284 × 716, 24 fps, 97 frames, 4.041667 seconds, no audio. The midpoint frame was visually inspected: the painted black shoe and planted toe are retained, with the requested heel lift. This is a candidate for team review, not a full motion-quality approval.

The finished take appeared automatically in the browser gallery (160 videos / 525 total media at verification). “Voir le résultat” opened its local preview, which loaded with `readyState: 4`, the measured duration and no media error. The existing 18-shot edit was preserved. No faces or upper body are part of this separate shot; the earlier face-filter refusal remains unresolved.

No credential is stored in source, browser storage, saved project recipes or manifests. Runtime state and generated thumbnails are ignored by Git. The local generator runs two requests at once; this is an application setting, not a claim about the account's maximum FAL concurrency.

## Limits

- Browser preview is approximate; export normalizes to integer 24 fps frame intervals.
- An image reference creates a new take; it does not guarantee the old video motion or exact character continuity.
- Images can guide generation but cannot yet be inserted as static timeline clips.
- Music currently replaces audio. Separate dialogue/music mixing is not implemented.
- The app is local; teammates need the repository/media and their own local server. Credentials are not shared in JSON recipes.
