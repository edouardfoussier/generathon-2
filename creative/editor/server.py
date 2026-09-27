#!/usr/bin/env python3
"""Local multicamera review editor. Python standard library + FFmpeg only."""

from __future__ import annotations

import argparse
import copy
import getpass
import json
import mimetypes
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit
import uuid

from media_library import MediaLibrary


HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
FPS = 24
DURATION_FRAMES = 1824
MAX_EXPORT_FRAMES = 1920  # The hackathon's 80-second limit.
MAX_SEGMENTS = 200
MAX_BODY = 256 * 1024
BOUNDARIES = [0, 144, 240, 360, 528, 624, 696, 780, 816, 864, 936,
              1128, 1224, 1320, 1512, 1584, 1680, 1728, 1824]
SOURCE_NAMES = {"seedance25": "Seedance 2.5", "kling3": "Kling 3 Pro", "veo31": "Veo 3.1"}
SOURCES = {
    key: REPO / "creative" / "model-comparison-v3" / "renders" / f"converse-v3-{key}.mp4"
    for key in SOURCE_NAMES
}
ID_RE = re.compile(r"^[a-f0-9]{32}$")
STATIC_EXTENSIONS = {".html", ".css", ".js", ".json", ".png", ".jpg", ".jpeg",
                     ".webp", ".svg", ".ico", ".mp4", ".webm", ".mp3", ".wav",
                     ".woff", ".woff2", ".ttf", ".vtt"}


class ValidationError(ValueError):
    pass


class ExportBusy(RuntimeError):
    pass


def validate_recipe(payload, sources=None, duration_frames=DURATION_FRAMES, source_durations=None, audio_ids=None):
    """Return a fresh, canonical recipe, accepting frame numbers, never paths."""
    source_ids = set(SOURCES if sources is None else sources)
    if not isinstance(payload, dict):
        raise ValidationError("Expected a JSON object.")
    if type(payload.get("version")) is not int or payload["version"] != 1:
        raise ValidationError("Recipe version must be 1.")
    if type(payload.get("fps")) is not int or payload["fps"] != FPS:
        raise ValidationError("The timeline must use 24 frames per second.")
    segments = payload.get("segments")
    if not isinstance(segments, list) or not 1 <= len(segments) <= MAX_SEGMENTS:
        raise ValidationError(f"Choose between 1 and {MAX_SEGMENTS} clips.")
    cleaned, used_ids, total = [], set(), 0
    for index, segment in enumerate(segments):
        if not isinstance(segment, dict):
            raise ValidationError(f"Clip {index + 1} must be an object.")
        segment_id = segment.get("id")
        if not isinstance(segment_id, str) or not 1 <= len(segment_id) <= 100:
            raise ValidationError(f"Clip {index + 1} needs an id of 1–100 characters.")
        if segment_id in used_ids:
            raise ValidationError("Clip ids must be unique.")
        used_ids.add(segment_id)
        source = segment.get("sourceId")
        if not isinstance(source, str) or source not in source_ids:
            raise ValidationError(f"Clip {index + 1} has an unknown video source.")
        start, end = segment.get("inFrame"), segment.get("outFrame")
        if type(start) is not int or type(end) is not int:
            raise ValidationError(f"Clip {index + 1} must use whole frame numbers.")
        limit = (source_durations or {}).get(source, duration_frames)
        if not 0 <= start < end <= limit:
            raise ValidationError(f"Clip {index + 1} is outside its source video.")
        total += end - start
        cleaned.append({"id": segment_id, "sourceId": source, "inFrame": start, "outFrame": end})
    if total > MAX_EXPORT_FRAMES:
        raise ValidationError("The assembled video must stay within the 80-second limit.")
    result = {"version": 1, "fps": FPS, "segments": cleaned}
    if "audioMode" in payload:
        if not isinstance(payload["audioMode"], str) or payload["audioMode"] not in {"source", "veo", "silent"}:
            raise ValidationError("Choose source, veo, or silent audio.")
        result["audioMode"] = payload["audioMode"]
    soundtrack = payload.get("soundtrackId")
    if soundtrack is not None:
        if not isinstance(soundtrack, str) or soundtrack not in (audio_ids or set()):
            raise ValidationError("Unknown soundtrack. Choose an audio file from the gallery.")
        result["soundtrackId"] = soundtrack
    return result


def parse_range(value, size):
    """Return inclusive byte bounds, or raise ValueError for unsatisfiable ranges."""
    match = re.fullmatch(r"bytes=(\d*)-(\d*)", value.strip())
    if not match or size <= 0 or not any(match.groups()):
        raise ValueError("Unsupported byte range")
    first, last = match.groups()
    if not first:
        suffix = int(last)
        if suffix <= 0:
            raise ValueError("Empty suffix range")
        return max(0, size - suffix), size - 1
    start = int(first)
    end = min(int(last), size - 1) if last else size - 1
    if start >= size or end < start:
        raise ValueError("Range is outside the file")
    return start, end


def find_program(name):
    found = shutil.which(name)
    if found:
        return found
    fallback = Path("/opt/homebrew/bin") / name
    if fallback.is_file():
        return str(fallback)
    raise RuntimeError(f"{name} is required. Install FFmpeg, then restart the editor.")


class ExportManager:
    def __init__(self, source_paths=None, output_dir=None, duration_frames=DURATION_FRAMES, library=None):
        self.sources = {key: Path(path) for key, path in (source_paths or SOURCES).items()}
        self.output_dir = Path(output_dir or HERE / "exports")
        self.duration_frames = duration_frames
        self.library = library
        self.source_durations = {}
        self.jobs = {}
        self.lock = threading.Lock()
        self.active_id = None

    def refresh_sources(self):
        if self.library:
            self.sources = self.library.sources()
            self.source_durations = {key: self.library.duration_for(key) for key in self.sources}

    def submit(self, payload):
        self.refresh_sources()
        audio_ids = {asset['id'] for asset in self.library.snapshot()['assets'] if asset['kind'] == 'audio'} if self.library else set()
        recipe = validate_recipe(payload, self.sources, self.duration_frames, self.source_durations, audio_ids)
        used = {segment['sourceId'] for segment in recipe['segments']}
        if recipe.get('audioMode', 'veo') == 'veo' and any(key in SOURCE_NAMES for key in used):
            used.add('veo31')
        missing = [key for key in used if key not in self.sources or not self.sources[key].is_file()]
        if missing:
            raise RuntimeError("Source videos are missing: " + ", ".join(missing))
        # Fail synchronously and helpfully if the encoder is not installed.
        ffmpeg, ffprobe = find_program("ffmpeg"), find_program("ffprobe")
        with self.lock:
            if self.active_id is not None:
                raise ExportBusy("An export is already running. Wait for it to finish.")
            export_id = uuid.uuid4().hex
            self.active_id = export_id
            self.jobs[export_id] = {"id": export_id, "status": "queued", "progress": 0}
        thread = threading.Thread(target=self._run,
                                  args=(export_id, recipe, ffmpeg, ffprobe), daemon=True)
        thread.start()
        return self.get(export_id)

    def get(self, export_id):
        with self.lock:
            job = self.jobs.get(export_id)
            return copy.deepcopy(job) if job else None

    def _update(self, export_id, **values):
        with self.lock:
            self.jobs[export_id].update(values)

    @staticmethod
    def _command(args):
        result = subprocess.run(args, capture_output=True, text=True, timeout=900)
        if result.returncode:
            tail = "\n".join(result.stderr.strip().splitlines()[-8:])
            raise RuntimeError("FFmpeg could not complete this export. " + tail[-1800:])
        return result.stdout

    def _run(self, export_id, recipe, ffmpeg, ffprobe):
        self._update(export_id, status="running", progress=1)
        final_path = self.output_dir / f"{export_id}.mp4"
        recipe_path = self.output_dir / f"{export_id}.json"
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix=f"work-{export_id}-", dir=self.output_dir) as temp:
                work = Path(temp)
                segments = recipe["segments"]
                total_frames = sum(s["outFrame"] - s["inFrame"] for s in segments)
                done_frames = 0
                clip_paths = []
                for index, segment in enumerate(segments):
                    length = segment["outFrame"] - segment["inFrame"]
                    clip_path = work / f"clip-{index:03d}.mp4"
                    # Accurate input seeking decodes from the preceding keyframe.
                    # All source renders are CFR 24 fps; output is an exact frame count.
                    self._command([
                        ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
                        "-ss", f"{segment['inFrame'] / FPS:.9f}",
                        "-i", str(self.sources[segment["sourceId"]]),
                        "-map", "0:v:0", "-an", "-frames:v", str(length),
                        "-vf", "setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=decrease,"
                               "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,tpad=stop_mode=clone:stop_duration=1,fps=24",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                        "-pix_fmt", "yuv420p", "-r", "24", "-g", "48", "-bf", "0",
                        "-threads", "2", "-video_track_timescale", "12288", str(clip_path),
                    ])
                    clip_paths.append(clip_path)
                    done_frames += length
                    self._update(export_id, progress=round(5 + 76 * done_frames / total_frames))

                # Decode each chosen interval to PCM; missing audio becomes exact-length
                # silence. AAC is encoded once after concatenation, without splice gaps.
                audio_path = work / "soundtrack.wav"
                soundtrack = recipe.get('soundtrackId')
                if soundtrack:
                    music = self.library.path_for(soundtrack)
                    if not music:
                        raise RuntimeError("The selected soundtrack is no longer available.")
                    self._command([ffmpeg, '-v', 'error', '-nostdin', '-y', '-i', str(music),
                                   '-vn', '-af', f"aresample=48000,apad,atrim=end_sample={total_frames * 2000}",
                                   '-c:a', 'pcm_s16le', '-ar', '48000', '-ac', '2', str(audio_path)])
                else:
                    audio_clips = []
                    for index, segment in enumerate(segments):
                        audio_clip = work / f'audio-{index:03d}.wav'
                        length = segment['outFrame'] - segment['inFrame']
                        mode = recipe.get('audioMode', 'veo')
                        source_id = segment['sourceId'] if mode == 'source' else 'veo31' if mode == 'veo' and segment['sourceId'] in SOURCE_NAMES else None
                        source_path = self.sources.get(source_id)
                        has_audio = False
                        if source_path:
                            inspection = json.loads(self._command([ffprobe, '-v', 'error', '-show_entries', 'stream=codec_type', '-of', 'json', str(source_path)]))
                            has_audio = any(stream.get('codec_type') == 'audio' for stream in inspection.get('streams', []))
                        if has_audio:
                            inputs = ['-i', str(source_path)]
                            filters = f"aresample=48000,atrim=start_sample={segment['inFrame'] * 2000}:end_sample={segment['outFrame'] * 2000},asetpts=PTS-STARTPTS,apad,atrim=end_sample={length * 2000}"
                        else:
                            inputs = ['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo']
                            filters = f'atrim=end_sample={length * 2000}'
                        self._command([ffmpeg, '-v', 'error', '-nostdin', '-y', *inputs,
                                       '-vn', '-af', filters, '-c:a', 'pcm_s16le', '-ar', '48000', '-ac', '2', str(audio_clip)])
                        audio_clips.append(audio_clip)
                    audio_concat = work / 'audio.txt'
                    audio_concat.write_text(''.join(f"file '{path.name}'\n" for path in audio_clips))
                    self._command([ffmpeg, '-v', 'error', '-nostdin', '-y', '-f', 'concat', '-safe', '1',
                                   '-i', str(audio_concat), '-c:a', 'copy', str(audio_path)])
                self._update(export_id, progress=88)
                concat_file = work / "clips.txt"
                # Only our generated fixed filenames enter the concat manifest.
                concat_file.write_text("".join(f"file '{path.name}'\n" for path in clip_paths))
                assembled = work / "assembled.mp4"
                self._command([ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
                               "-f", "concat", "-safe", "1", "-i", str(concat_file),
                               "-i", str(audio_path), "-map", "0:v:0", "-map", "1:a:0",
                               "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                               "-t", f"{total_frames / FPS:.9f}", "-movflags", "+faststart",
                               str(assembled)])
                self._update(export_id, progress=96)
                inspection = json.loads(self._command([
                    ffprobe, "-v", "error", "-count_frames", "-show_entries",
                    "stream=codec_type,nb_read_frames,width,height,avg_frame_rate:format=duration",
                    "-of", "json", str(assembled),
                ]))
                video = next(stream for stream in inspection["streams"] if stream["codec_type"] == "video")
                if int(video["nb_read_frames"]) != total_frames:
                    raise RuntimeError("Export verification failed: the video frame count did not match the edit.")
                if video["width"] != 1920 or video["height"] != 1080 or video["avg_frame_rate"] != "24/1":
                    raise RuntimeError("Export verification failed: unexpected video format.")
                if abs(float(inspection["format"]["duration"]) - total_frames / FPS) > 0.05:
                    raise RuntimeError("Export verification failed: unexpected duration.")
                os.replace(assembled, final_path)
                recipe_path.write_text(json.dumps(recipe, ensure_ascii=False, indent=2) + "\n")
                self._update(export_id, status="completed", progress=100,
                             durationFrames=total_frames, audioSourceId=recipe.get("soundtrackId") or recipe.get("audioMode", "veo"),
                             downloadUrl=f"/exports/{export_id}.mp4",
                             recipeUrl=f"/exports/{export_id}.json")
        except Exception as error:
            for path in (final_path, recipe_path):
                try:
                    path.unlink(missing_ok=True)
                except OSError:
                    pass
            self._update(export_id, status="failed", error=str(error)[-2200:])
        finally:
            with self.lock:
                if self.active_id == export_id:
                    self.active_id = None


class EditorServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, manager=None, library=None):
        self.library = library or (MediaLibrary(REPO, SOURCES) if manager is None else None)
        self.manager = manager or ExportManager(library=self.library)
        self._generator = None
        self._generator_lock = threading.Lock()
        super().__init__(address, EditorHandler)

    @property
    def generator(self):
        with self._generator_lock:
            if self._generator is None:
                if self.library is None:
                    raise RuntimeError("Generation needs the local media library.")
                from generation import Generator
                self._generator = Generator(self.library)
            return self._generator


class EditorHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "ConverseLocalEditor/1.0"

    def log_message(self, format, *args):
        # Keep the useful local request log without including request bodies.
        print(f"[{time.strftime('%H:%M:%S')}] {format % args}", flush=True)

    def _send(self, status, body=b"", content_type="application/json; charset=utf-8", headers=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD" and body:
            self.wfile.write(body)

    def _json(self, status, payload):
        self._send(status, json.dumps(payload, ensure_ascii=False).encode())

    def _allowed_host(self):
        host = self.headers.get("Host", "")
        try:
            parsed = urlsplit("http://" + host)
            return (parsed.hostname in {"127.0.0.1", "localhost", "::1"}
                    and parsed.port == self.server.server_port
                    and not parsed.username and not parsed.password)
        except ValueError:
            return False

    def _check_request(self):
        if not self._allowed_host():
            self.close_connection = True
            self._json(403, {"error": "This editor only accepts its local hostname and port."})
            return False
        origin = self.headers.get("Origin")
        if origin and origin != f"http://{self.headers.get('Host')}":
            self.close_connection = True
            self._json(403, {"error": "Cross-origin requests are not allowed."})
            return False
        return True

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        if not self._check_request():
            return
        try:
            path = unquote(urlsplit(self.path).path)
            if "\x00" in path:
                raise ValueError("Invalid path")
            if path == "/api/project":
                self.server.manager.refresh_sources()
                self._json(200, {
                    "fps": FPS, "durationFrames": self.server.manager.duration_frames,
                    "maxExportFrames": MAX_EXPORT_FRAMES, "audioSourceId": "veo31",
                    "sources": [{"id": key, "name": SOURCE_NAMES.get(key) or (self.server.library.get(key) or {}).get('name', key),
                                 "url": f"/media/{key}.mp4", "durationFrames": self.server.manager.source_durations.get(key, self.server.manager.duration_frames)}
                                for key in self.server.manager.sources],
                    "boundariesFrames": BOUNDARIES,
                })
                return
            if path == '/api/library':
                self._json(200, self.server.library.snapshot() if self.server.library else {'assets': [], 'collections': []})
                return
            if path == '/api/generation/config':
                self._json(200, self.server.generator.config())
                return
            if path == '/api/generation/jobs':
                self._json(200, self.server.generator.list_jobs())
                return
            if path.startswith('/api/generation/jobs/'):
                job_id = path.removeprefix('/api/generation/jobs/')
                job = self.server.generator.get(job_id) if re.fullmatch(r'[a-zA-Z0-9_-]{1,100}', job_id) else None
                self._json(200 if job else 404, job or {'error': 'Generation not found.'})
                return
            if path.startswith("/api/export/"):
                export_id = path.removeprefix("/api/export/")
                job = self.server.manager.get(export_id) if ID_RE.fullmatch(export_id) else None
                self._json(200 if job else 404, job or {"error": "Export not found."})
                return
            if path == "/board":
                self._send(302, headers={"Location": "/creative/selection/index.html"})
                return
            file_path, attachment = self._resolve_file(path)
            if file_path is None or not file_path.is_file():
                self._json(404, {"error": "File not found."})
                return
            self._serve_file(file_path, attachment)
        except (BrokenPipeError, ConnectionResetError):
            pass  # Browsers routinely cancel superseded video range requests.
        except (ValueError, OSError):
            self._json(400, {"error": "Invalid file request."})
        except (RuntimeError, ImportError) as error:
            self._json(503, {"error": str(error)})

    def _resolve_file(self, path):
        manager = self.server.manager
        if path.startswith('/library-poster/'):
            name = path.removeprefix('/library-poster/')
            match = re.fullmatch(r'([A-Za-z0-9_-]{1,80})\.jpg', name)
            return (self.server.library.poster_path(match[1]) if match and self.server.library else None), False
        if path.startswith('/library/'):
            key = path.removeprefix('/library/')
            return (self.server.library.path_for(key) if self.server.library else None), False
        if path.startswith("/media/"):
            name = path.removeprefix("/media/")
            key = name[:-4] if name.endswith(".mp4") else ""
            return (self.server.library.path_for(key) if self.server.library else manager.sources.get(key)), False
        if path.startswith("/exports/"):
            name = path.removeprefix("/exports/")
            match = re.fullmatch(r"([a-f0-9]{32})\.(mp4|json)", name)
            return (manager.output_dir / name, True) if match else (None, False)
        if path.startswith("/creative/"):
            base = REPO / "creative"
            relative = path.removeprefix("/creative/")
        else:
            base = HERE
            relative = "index.html" if path in {"", "/"} else path.lstrip("/")
        candidate = (base / relative).resolve()
        if not candidate.is_relative_to(base.resolve()) or candidate.suffix.lower() not in STATIC_EXTENSIONS:
            return None, False
        if any(part.startswith(".") for part in Path(relative).parts) or "exports" in Path(relative).parts:
            return None, False
        return candidate, False

    def _serve_file(self, path, attachment=False):
        size = path.stat().st_size
        start, end, status = 0, size - 1, 200
        requested_range = self.headers.get("Range")
        if requested_range:
            try:
                start, end = parse_range(requested_range, size)
                status = 206
            except ValueError:
                self._send(416, headers={"Content-Range": f"bytes */{size}", "Accept-Ranges": "bytes"})
                return
        self.send_response(status)
        self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(max(0, end - start + 1)))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-cache")
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        if attachment:
            self.send_header("Content-Disposition", f'attachment; filename="converse-edit-{path.stem[:8]}{path.suffix}"')
        self.end_headers()
        if self.command == "HEAD":
            return
        remaining = end - start + 1
        with path.open("rb") as file:
            file.seek(start)
            while remaining > 0:
                chunk = file.read(min(256 * 1024, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)

    def do_POST(self):
        if not self._check_request():
            return
        route = urlsplit(self.path).path
        if route not in {"/api/export", "/api/library/refresh", "/api/generation"}:
            self.close_connection = True
            self._json(404, {"error": "Unknown API route."})
            return
        if self.headers.get("Transfer-Encoding"):
            self.close_connection = True
            self._json(400, {"error": "Chunked request bodies are not accepted."})
            return
        if self.headers.get("Content-Type", "").split(";", 1)[0].strip() != "application/json":
            self.close_connection = True
            self._json(415, {"error": "Send an application/json recipe."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = -1
        if not 0 < length <= MAX_BODY:
            self.close_connection = True
            self._json(413, {"error": "Recipe body must be between 1 byte and 256 KB."})
            return
        try:
            # A short socket timeout bounds an incomplete/malicious local upload.
            self.connection.settimeout(10)
            body = self.rfile.read(length)
            if len(body) != length:
                raise ValidationError("Incomplete request body.")
            payload = json.loads(body)
            if not isinstance(payload, dict):
                raise ValidationError('Expected a JSON object.')
            if route == '/api/library/refresh':
                result = self.server.library.refresh() if self.server.library else {'assets': [], 'collections': []}
                self.server.manager.refresh_sources()
                self._json(200, result)
            elif route == '/api/generation':
                self._json(202, self.server.generator.submit(payload))
            else:
                self._json(202, self.server.manager.submit(payload))
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as error:
            self._json(400, {"error": str(error)})
        except ExportBusy as error:
            self._json(409, {"error": str(error)})
        except (RuntimeError, OSError, ImportError) as error:
            self._json(503, {"error": str(error)})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8787, help="Local HTTP port (default: 8787)")
    parser.add_argument("--fal-key-stdin", action="store_true", help="Read the FAL key without echo; keep it only in server memory")
    args = parser.parse_args()
    if args.fal_key_stdin:
        os.environ["FAL_KEY"] = getpass.getpass("FAL API key (hidden, memory only): ").strip()
    if not 1 <= args.port <= 65535:
        parser.error("Port must be between 1 and 65535.")
    server = EditorServer(("127.0.0.1", args.port))
    print(f"Editor: http://127.0.0.1:{args.port}/", flush=True)
    print("MP4 exports use FFmpeg. Keep this terminal open; Ctrl-C stops the local server.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping editor.", flush=True)
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
