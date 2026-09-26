# Local video editor backend

Run from the repository root:

```sh
python3 creative/editor/server.py
```

Open **http://127.0.0.1:8787/**. Keep the terminal open. Use `--port 8788` if the default port is occupied. Python 3.10+ and FFmpeg/FFprobe are required; there are no Python packages to install. On macOS, an existing Homebrew FFmpeg installation is detected automatically.

The site and its three source videos are served locally. Video HTTP byte ranges support browser seeking without downloading each complete source first. The server listens only on `127.0.0.1`, validates the local hostname and origin, and accepts fixed source IDs rather than file paths or FFmpeg arguments.

## Export behavior

- An edit is an ordered list of source intervals, expressed as whole frames at **24 fps**. Out points are exclusive.
- Source IDs are `seedance25`, `kling3`, and `veo31`; each source contains 1,824 frames (76 seconds).
- Clips may be trimmed, reordered, omitted, or reused. An export allows 1–200 clips with a combined maximum of **1,920 frames / 80 seconds**.
- Each chosen video interval is re-encoded as H.264, 1920×1080, 24 fps. The finished MP4 uses AAC audio and fast-start metadata.
- **Audio always uses the Veo master at the matching source times.** Choosing a different image model does not change the dialogue, score, or volume. Reordering/deleting intervals also reorders/deletes the corresponding soundtrack; this is a picture-selection editor, not a separate dialogue/music mixer.
- Exported frame count, dimensions, frame rate, and duration are verified before the download becomes available. Each export includes a JSON recipe that can be re-imported.
- One export runs at a time. Temporary clips are removed when the job finishes or fails. Finished files are kept in `creative/editor/exports/` until deleted manually; this directory should be ignored by Git.

## API

`GET /api/project` returns the sources, frame rate, boundaries, soundtrack source, and duration limits.

`POST /api/export` accepts `Content-Type: application/json`:

```json
{
  "version": 1,
  "fps": 24,
  "segments": [
    {"id": "first", "sourceId": "veo31", "inFrame": 0, "outFrame": 144},
    {"id": "second", "sourceId": "kling3", "inFrame": 144, "outFrame": 240}
  ]
}
```

Returns HTTP 202 with `{id, status, progress}`. `progress` is an integer from 0 to 100. Poll `GET /api/export/{id}` for `queued`, `running`, `completed`, or `failed`. A completed job has `downloadUrl`, `recipeUrl`, `durationFrames`, and `audioSourceId`; a failed job has `error`. Another submission while busy returns HTTP 409. Job status is held in memory; completed files remain downloadable after a restart if their URLs are retained.

Static routes: `/` for the editor, `/media/{sourceId}.mp4` for source media, `/exports/{id}.mp4` and `/exports/{id}.json` for downloads, `/board` for the visual-selection board. Files under `/creative/` with allowed media/web extensions can be read for board compatibility. Source files are never changed.

## Verification

```sh
python3 creative/editor/test_server.py
python3 creative/editor/test_server.py --smoke
```

The first command checks input validation, duration limits, byte ranges and HEAD requests, traversal protection, same-origin checks, and export locking. `--smoke` additionally renders a three-second edit with one interval from each real model. It verifies all 72 frames, checks the first and last frames on both sides of each model splice against the selected originals, and compares the soundtrack waveform with the matching Veo intervals. Its MP4 and QA report are written inside the ignored `exports/` directory.

This server is intended for one local editor. To use it on a teammate’s machine, clone the repository with the video files and run the same command there. Public hosting would need separate authentication, storage, and job infrastructure; exposing this development server is not supported.
