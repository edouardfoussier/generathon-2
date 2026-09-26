# GPT continuity — full film

Complete 76-second edition of the selected GPT Image 2.5 Sunburst / Seedance 2.5 opening. All new reference images belong to the GPT continuity family. The 30-second opening is retained, not regenerated.

**Ready:** [Watch the complete 76-second film](renders/converse-gpt-seedance25-full-76s.mp4) · [Contact sheet](qa/contact-sheet.jpg).

Six new Seedance 2.5 clips add 42 seconds of generated action; the editorial end card adds four seconds. The confirmed additional generation charge is **1,764 Arcads credits**. This excludes the already-paid opening and continuity images. No additional generation was needed for the title card or audio.

## Editorial plan

| Time | Content | Source |
| --- | --- | --- |
| 0–30 s | Approved attic / discovery / phone / shoes / Rafa reveal | Existing CV01G |
| 30–37 s | Rafa plays basketball in 1970 | `videos/basketball.mp4` |
| 37–45 s | Rafa and Elena dance salsa in 1977 | `videos/salsa.mp4` |
| 45–49 s | Their wedding | `videos/wedding.mp4` |
| 49–53 s | Their newborn daughter, Luna's future mother | `videos/newborn.mp4` |
| 53–61 s | Rafa hands the shoes to his teenage daughter in 1995 | `videos/handover.mp4` |
| 61–72 s | Luna returns from the memory and answers her mother | `videos/return.mp4` |
| 72–76 s | Converse. Conserve what matters. | Original typesetting and a complete shoe crop from CS02G |

The sound uses the existing v3 score and English voices. The opening mix is preserved for its first 30 seconds; Mum calls at 62.9 s and Luna answers at 67.1 s. Native clip audio is not used. No new audio or end-card generation is charged.

## Rebuild

Requires Python 3, Pillow, FFmpeg and FFprobe. The end card uses the macOS Arial fonts already used by this local project.

```sh
python3 creative/gpt-full-film-v1/render.py --prepare
python3 creative/gpt-full-film-v1/render.py
```

The script refuses missing or short generated clips. It assembles a 46-second continuation, stream-copies the approved 30-second picture opening, and checks that all 720 original decoded frames remain identical. Audio is decoded to PCM for assembly and encoded once into the final AAC soundtrack.

The delivered export is `renders/converse-gpt-seedance25-full-76s.mp4`: **76.000 s, 1,824 frames, 1280 × 720, 24 fps, H.264 / stereo AAC**, approximately 20.5 MB. A full decode passed. All 720 decoded opening picture frames match the approved CV01G exactly; the first 30 seconds of PCM audio also match before final AAC encoding. Final sample peak is −1.4 dBFS.

The 24 sampled final-film frames were visually reviewed for framing, character identity, wardrobe, narrative order and legible end-card text. No major defect was visible in those samples. Separate source-clip reviews are saved by the generation and QA agents. This is sampled visual QA plus a complete technical decode, not a claim of frame-by-frame visual inspection or manually matched dialogue lip sync.

Generation status, job IDs and credit accounting are maintained in the root-owned plan/jobs/manifest files.
