# Converse · Cut Room

A bilingual editing room for the three 76-second Converse films. Compare Veo 3.1, Kling 3 Pro and Seedance 2.5 at the same story time, keep the best passages, and export one MP4. Veo is selected throughout when you start.

## Open it

From the repository root:

```sh
python3 creative/editor/server.py
```

Open **http://127.0.0.1:8787/** and keep the terminal running. Requires Python 3.10+, FFmpeg and FFprobe. There is no npm or Python package install. Existing Homebrew FFmpeg on macOS is detected automatically.

## Make your cut

1. Click a shot on the timeline or drag the time ruler. The three previews show the same source moment.
2. Click a model’s take to use it for that passage. The fourth track shows your assembled film.
3. To keep only part of a take, move the playhead and press **S** to split. Select a different model for either side. Alternatively, adjust the source in/out timecodes in the inspector.
4. Use **Your film** to see only the selected take. **Compare** restores all three previews.
5. Choose **Export film → Render MP4**, then download the result. Export is 1920×1080, 24 fps, H.264/AAC, with a maximum duration of 80 seconds.

**Undo/redo:** Cmd/Ctrl Z, Cmd/Ctrl Shift Z. **Play/pause:** Space. **Choose models:** 1 / 2 / 3. **Step frames:** arrow keys; Shift + arrow steps one second. **Mark source in/out:** I / O. Source out points exclude that frame.

Source changes preserve a common music/dialogue track from the Veo master. Trimming, deleting or reordering passages also edits the corresponding soundtrack intervals. This first version does not provide separate music/dialogue mixing, transitions, color grading, or arbitrary media imports. Browser previews are approximate; exported cuts use exact frame ranges.

## Work with the team

The edit is saved automatically in this browser. **Save edit** downloads a small JSON recipe; send that to a teammate, who can load it with **Open edit** after cloning this repository and starting their own server. The source video files must remain in `creative/model-comparison-v3/renders/`.

The localhost link opens on the computer running the server; it is not a shared online room. JSON recipes do not include media and there is no live collaboration. Downloaded MP4 files can be shared normally. Rendered files remain in the ignored `creative/editor/exports/` folder and are not pushed to GitHub.

## Development and verification

See [backend documentation](README-backend.md) for the API, validation and export checks, and [open-source research](RESEARCH.md) for existing alternatives and the implementation decision.

```sh
node --test creative/editor/model.test.mjs
python3 creative/editor/test_server.py --smoke
```

The model suite verifies source-to-timeline mapping after selection, split, trim and reorder operations. The backend smoke test renders real intervals from all three films, checking frames at splice boundaries and the shared audio.
