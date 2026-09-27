# Local video editor backend

Run from the repository root:

```sh
python3 creative/editor/server.py
```

Open **http://127.0.0.1:8787/**. Keep the terminal open. Use `--port 8788` if the default port is occupied. Python 3.10+ and FFmpeg/FFprobe are required; there are no Python packages to install. On macOS, Homebrew FFmpeg is detected automatically.

For FAL regeneration, provide `FAL_KEY` in the server environment or use `--fal-key-stdin` to enter it at a hidden terminal prompt. Credentials stay on the server; they are not returned to the browser, written into project files, or included in saved recipes. Generation settings and supported models are available from `/api/generation/config`.

The server listens only on `127.0.0.1`, validates its local hostname and origin, and accepts registered media IDs rather than file paths or FFmpeg arguments. Media HTTP byte ranges support seeking without downloading an entire source first.

## Media library

The library scans `creative/` without changing any source assets. It reads existing JSON manifests and provenance records, then finds additional video, image, and audio files. Each file gets a stable ID derived from its repository-relative path; the original three source IDs (`seedance25`, `kling3`, `veo31`) remain compatible with older recipes.

Titles, models, prompts, source codes, and image references are recovered when recorded in existing manifests. New generation variants also retain their sourceId and direct referenceIds. Missing provenance is shown as missing, never invented. Unlisted QA frames, contact sheets, posters, thumbnails, hidden files, vendor directories and exports are omitted. A manifest may explicitly include a QA asset; hidden/vendor/export paths remain forbidden. Symlinks outside `creative/` cannot be catalogued or served. Nested generated-variant manifests are indexed on refresh.

Videos reuse declared posters when available. Otherwise `/library-poster/{id}.jpg` creates a 480 px JPEG on demand, at 0.2 seconds (or half the duration for very short clips). At most three thumbnail encoders run concurrently; simultaneous requests for the same video share one cached result. Cache fingerprints include source size and modification time; failed or unknown sources return 404. Thumbnails live in ignored `.state/thumbnails/` and do not delay catalog startup.

FFprobe metadata is cached by file size and modification time in ignored `creative/editor/.state/catalog-cache.json`. Video intervals use each source's own duration, normalized to the 24 fps editing grid. Images are reference assets; the exporter currently accepts video clips. Library audio can replace the export soundtrack.

## Export behavior

- An edit is an ordered list of source intervals in whole frames at **24 fps**. Out points are exclusive.
- Clips may be trimmed, reordered, omitted, or reused. An export permits 1–200 clips and at most **1,920 frames / 80 seconds**.
- Each chosen interval is re-encoded as H.264, 1920×1080, 24 fps. Portrait/square assets are letterboxed. Short and variable-rate videos are normalized to the editing grid.
- `audioMode: "source"` uses the audio from each selected clip, with silence where none exists. `"silent"` mutes all clips. `"veo"` uses matching Veo master intervals for the three original comparison sources, and silence for unrelated gallery clips. Missing `audioMode` retains this legacy Veo behavior.
- `soundtrackId` optionally selects an audio asset from the library. It **replaces** all clip audio, starts at zero, and is trimmed to the edit length or padded with silence if shorter. This is not a dialogue/music mixer.
- Audio intervals are decoded to PCM before concatenation and encoded to AAC only once, avoiding an encoder delay at each splice.
- Only files actually used by the edit are required. Exported frame count, dimensions, frame rate, and duration are verified before download becomes available.
- One export runs at a time. Temporary clips are removed on completion or failure. Finished MP4s and JSON recipes remain in ignored `creative/editor/exports/`.

## API

`GET /api/project` returns all usable video sources, per-source durationFrames, frame rate, legacy comparison boundaries, and duration limits.

`GET /api/library` returns `{assets, collections}`. Each asset has `id`, `kind`, `name`, `title`, `url`, `collection`, `model`, `prompt`, `referenceIds`, `durationFrames`, `durationSeconds`, `hasAudio`, and provenance when available. `title` can be a bilingual object; `name` is always a string. The public inventory contains repository-relative paths, never absolute filesystem paths or credentials.

`POST /api/library/refresh` with `{}` rescans assets and returns the updated library. `GET /library/{id}` serves only a registered, safe asset.

Generation routes: `GET /api/generation/config`, `GET /api/generation/jobs`, `POST /api/generation`, and `GET /api/generation/jobs/{id}`. The generation module owns provider-specific validation, job state and model schemas. Each result creates a new variant and preserves its source.

`POST /api/export` accepts `Content-Type: application/json`:

```json
{
  "version": 1,
  "fps": 24,
  "audioMode": "source",
  "segments": [
    {"id": "first", "sourceId": "veo31", "inFrame": 0, "outFrame": 144},
    {"id": "second", "sourceId": "kling3", "inFrame": 144, "outFrame": 240}
  ]
}
```

Returns HTTP 202 with `{id, status, progress}`. Poll `GET /api/export/{id}` for `queued`, `running`, `completed`, or `failed`. A completed job has `downloadUrl`, `recipeUrl`, `durationFrames`, and `audioSourceId`; a failed job has `error`. Another export while busy returns HTTP 409. Export status is held in memory; completed URLs remain downloadable after restart.

Static routes include `/` for the editor, `/media/{sourceId}.mp4` for compatible video URLs, `/exports/{id}.mp4` and `.json` for downloads, and `/board` for the visual-selection board. Allowed media/web files under `/creative/` are served for existing board compatibility. Hidden state is never served.

## Verification

```sh
python3 creative/editor/test_server.py
python3 creative/editor/test_server.py --smoke
python3 creative/editor/test_media_library.py
```

Backend checks cover recipe bounds, byte ranges, HEAD, traversal protection, same-origin checks, export locking and failure cleanup. `--smoke` renders a three-second edit from the actual three comparison films; it checks all 72 frames, both sides of the splices, and Veo waveform correlation. Its output stays in ignored `exports/`.

Library checks cover metadata/reference recovery, stable IDs, hidden files, symlink escapes and per-source duration validation. A generated fixture export checks mixed 30/24 fps clips, native audio, absent-audio silence, and replacing the soundtrack with a short music cue.

This server is for local editing. Teammates can clone the repository with its media and run the same command. Public hosting needs separate authentication, storage and job infrastructure; this development server should not be exposed publicly.
