# Converse · Cut Room

A bilingual editing room for the Rafa & Luna experiments. Browse the local scene library, select passages from any generated video, regenerate a particular take, and export one MP4. The original three-film comparison remains available; existing saved edits remain compatible.

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

## Browse and reuse every experiment

**Open media library** lists videos, images and audio found under `creative/`, with collection/model filters and search. Video thumbnails are cached locally. Use **Scan for new media** after adding files to a project folder. QA frame dumps, hidden files and editor exports are excluded. Prompts and references are recovered from existing manifests where available; an absent prompt is explicitly identified.

Open a video, set its source range in seconds, then **Add after selected shot**, **Replace selected shot**, or **Start an edit with this clip**. Starting an edit replaces only the browser recipe and can be undone. Images are references for generation, not still-image timeline clips. Imported videos use their own duration and time origin. Only the original three synchronized films use the three-way comparison.

Audio can use each clip's own sound, the original Veo track for the original three films, or silence. Choose an audio item in the gallery and **Use as soundtrack** to replace the soundtrack across the edit. This does not separate or mix dialogue: music replaces it, and short tracks are padded with silence at export. [Two new Suno proposals](../music-v5/index.html) are available in the `music-v5` collection.

Browser previews are approximate; exports normalize video to 24 fps and use the selected frame ranges. No transitions, color grading, still-image timeline clips or arbitrary external-file uploads are provided.

## Regenerate one scene with FAL

Start the server with a hidden key prompt:

```sh
python3 creative/editor/server.py --fal-key-stdin
```

Alternatively provide `FAL_KEY` in the server environment. Do not put a key in frontend files, saved edits or Git. The UI receives only a configured/not-configured flag. The key remains in server memory; restarting requires it again.

Select **Generate another take** in the inspector or gallery. Edit the prompt, choose a reference image (or extract a frame at the selected source in point), select a model and duration, then submit. This creates a new take guided by a starting image; it is not an in-place edit preserving the original clip's motion. Each submission uses FAL credits. The local queue runs two jobs concurrently, up to eight pending, subject to the provider's own account limits. The available models are Seedance 2.5, Kling 2.5 Turbo Pro and Nano Banana 2 image editing.

Finished media and provenance are saved to `generated/<job-id>/` and appear in the gallery. The old take and the current edit remain untouched until you choose the result. Private queue state is ignored under `.state/`. Known provider requests resume polling after restart. Ambiguous submissions are never automatically retried: check the saved request ID in FAL before starting another paid request.

Official schemas: [Seedance 2.5](https://fal.ai/models/bytedance/seedance-2.5/image-to-video/api), [Kling 2.5 Turbo Pro](https://fal.ai/models/fal-ai/kling-video/v2.5-turbo/pro/image-to-video/api), [Nano Banana 2](https://fal.ai/models/fal-ai/nano-banana-2/edit/api), [FAL queue](https://fal.ai/docs/documentation/model-apis/inference/queue). Verified September 27, 2026. Prices and model access are controlled by FAL.

## Work with the team

The edit is saved automatically in this browser. **Save edit** downloads a small JSON recipe; send that to a teammate, who can load it with **Open edit** after cloning this repository and starting their own server. Media IDs are stable across computers when the repository-relative paths are unchanged. Teammates need the same media files; a JSON recipe does not contain them or a FAL key.

The localhost link opens on the computer running the server; it is not a shared online room. JSON recipes do not include media and there is no live collaboration. Downloaded MP4 files can be shared normally. Rendered files remain in the ignored `creative/editor/exports/` folder and are not pushed to GitHub.

## Development and verification

See [backend documentation](README-backend.md) for the API, validation and export checks, and [open-source research](RESEARCH.md) for existing alternatives and the implementation decision.

```sh
node --test creative/editor/model.test.mjs
python3 creative/editor/test_server.py --smoke
python3 creative/editor/test_media_library.py
python3 creative/editor/test_generation.py
```

The model suite verifies selection, split, trim, reorder and arbitrary-source bounds. Backend tests cover real mixed-source exports, audio replacement, path boundaries, poster caching and generation lifecycle. Generation unit tests use a fake provider and never spend credits.
