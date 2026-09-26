# Music and phone exchange — v4

Two original instrumental cues were generated with **ElevenLabs through Arcads**. The completed asset metadata confirms both the `elevenlabs` model and provider; this is not a standalone ElevenLabs MCP connection. Each cue cost 24 credits. The two new phone voice takes cost 8 credits each, for **64 credits total** excluding any subsequently completed analysis charge (none charged as of this handoff).

| Choice | Playback copy | Exact edit master | Direction |
| --- | --- | --- | --- |
| MU01 | `organic-latin-breakbeat-76s.mp3` | `organic-latin-breakbeat-76s.wav` | Organic breakbeat, Latin percussion, bass, short brass motif |
| MU02 | `tactile-percussion-piano-76s.mp3` | `tactile-percussion-piano-76s.wav` | Tactile percussion, brushed textures, piano motif, bass |

The descriptive directions above are the prompts, not a claim that every instrument or timing instruction was obeyed. **MU01 is the provisional editorial recommendation**: its measured energy rises around 30 seconds and eases near 62 seconds in the fitted cue, supporting the sport/dance montage and the final conversation. MU02 keeps more energy through the ending and requires a stronger dialogue dip. The actual musical taste comparison remains for the team to audition.

Both PCM edit masters are exactly **76.000 seconds, 48 kHz, stereo** and passed complete decoding. Source originals are preserved. MU01 was returned at 94.040816 seconds despite a 76-second request; the edit removes source 46–64 seconds and uses a 40.816 ms crossfade, preserving original pitch, tempo and the ending. At the automated 120 BPM estimate this removes nine bars. MU02 only loses 42 ms of trailing provider excess. `prepare.py` reproduces these edits and technical checks.

`technical-qa.json` reports measured source loudness for each fitted master: roughly −14.5 LUFS and −0.7 dBTP. The `output_*` fields are a measurement filter's hypothetical normalization results; no loudness normalization was applied to the edit master. Start by attenuating the music about 6 dB under the film, then make deeper, smoothly ramped reductions under speech. Keep the finale audible after the last spoken line. `tempo-estimates.json` contains spectral-flux candidates of 120 BPM for both tracks; these are automated estimates, not a listening certification.

No direct perceptual audition was performed by the agent. The automated audio-analysis service rejected MU01 and its compressed retry because it expands the audio beyond its 15 MB limit. MU02 analysis was still pending at the initial handoff; see `analysis-status.json` for any later result. Full prompt, source IDs, duration discrepancy and cost are in `manifest.json`. No signed download URLs are stored.

## Phone exchange

The new Luna take reuses **Lauren**, exactly the same voice ID as the approved opening/ending. The device voice is the catalog's calm English voice **Ryan**. These are catalog voices, not voice clones.

- `luna-phone-question.wav`: dry source; “Can you tell me about my grandpa?” Exact words confirmed by independent transcription.
- `luna-phone-question-paced.wav`: same take slowed to 0.78×, approximately 2 seconds, matching the existing delivery treatment.
- `device-phone-reply.wav`: dry source; “Sorry. I don't have enough information.” Exact words confirmed by independent transcription.
- `device-phone-reply-paced.wav`: same take at 0.88×, with a restrained 200–5000 Hz phone-speaker band limit, approximately 2 seconds.

For an eight-second picture insert, allow 0–1.3 seconds for the photo action, question at 1.5–3.5, a short wait, reply at 4.1–6.1, then a reaction through 8 seconds. Keep Luna over the shoulder or offscreen during her line. The exact take metadata and transcription status are in `voice-manifest.json`. No lip-sync accuracy is claimed.
