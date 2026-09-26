# Verification — 26 September 2026

- **16 model tests passed:** mixed-source mapping, split/trim/reorder, immutability, invalid imports, duration limits and 120 successive splits with bounded unique IDs.
- **10 backend tests passed**, including the real three-source export smoke test. The 3-second test contains 72 frames; sampled splice frames match their selected originals and the soundtrack correlates 0.99933 with the Veo master intervals.
- **Full export through the browser UI passed:** 18 passages, Veo base with a Seedance basketball passage and Kling gift passage. The output contains exactly 1,824 H.264 frames, 1920×1080 at 24 fps; both video and AAC audio are 76.000 seconds. The test render is in the ignored `exports/` directory, not part of the source repository.
- **Browser interactions checked:** three loaded previews, take selection, shared playback, frame stepping, split and undo, saved edit restoration after reload, FR/EN switching, export progress and finished download links. The browser was restored to all-Veo after testing.
- **Review fixes:** split now selects the new right-hand segment; undo retains selection at the visible passage; replay resets selection to the opening; contiguous passages no longer force audio/video seeks; split identifiers stay within backend limits.

Preview playback is approximate and can drift while the browser seeks or decodes. Export uses exact integer-frame ranges. Illustrated clips are separate exploratory deliverables on the board; this editor currently compares the three existing photographic films.
