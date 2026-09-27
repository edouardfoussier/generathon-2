"""Local, non-destructive FAL scene generation. Secrets stay in server memory.

REST schemas verified against official FAL documentation on 2026-09-27.
The queue POST is deliberately never retried: an ambiguous response may have
already incurred a charge. Known remote requests resume polling after restart.
"""
from __future__ import annotations

import base64
import json
import mimetypes
import os
from pathlib import Path
import re
import shutil
import subprocess
import threading
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit
import uuid

HERE = Path(__file__).resolve().parent
MODELS = {
    "seedance25": {"id": "seedance25", "name": "Seedance 2.5 · 720p", "kind": "video",
                   "durations": [4, 5, 6, 8, 10, 12, 15], "requiresReference": True,
                   "endpoint": "bytedance/seedance-2.5/image-to-video"},
    "kling25": {"id": "kling25", "name": "Kling 2.5 Turbo Pro", "kind": "video",
                "durations": [5, 10], "requiresReference": True,
                "endpoint": "fal-ai/kling-video/v2.5-turbo/pro/image-to-video"},
    "nano-banana2": {"id": "nano-banana2", "name": "Nano Banana 2 · 2K", "kind": "image",
                     "durations": [], "requiresReference": True,
                     "endpoint": "fal-ai/nano-banana-2/edit"},
}
ACTIVE = {"queued", "preparing", "submitting", "in_queue", "in_progress", "downloading", "reconnecting"}
SAFE_ID = re.compile(r"^[a-zA-Z0-9_-]{1,150}$")


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def queue_url(value):
    if not isinstance(value, str):
        raise ValueError("Unexpected FAL queue address.")
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or parsed.hostname != "queue.fal.run"
            or parsed.port not in {None, 443} or parsed.username or parsed.password):
        raise ValueError("Unexpected FAL queue address.")
    return value


def media_url(value):
    if not isinstance(value, str):
        raise ValueError("Unexpected FAL output host.")
    parsed = urlsplit(value)
    host = parsed.hostname or ""
    if (parsed.scheme != "https" or parsed.port not in {None, 443}
            or parsed.username or parsed.password
            or not (host == "fal.media" or host.endswith(".fal.media")
                    or host == "storage.googleapis.com")):
        raise ValueError("Unexpected FAL output host.")
    return value


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise RuntimeError("Unexpected provider redirect; request stopped.")


class SubmissionRejected(RuntimeError):
    """A definitive HTTP rejection; unlike network/parse errors, not ambiguous."""


class FalTransport:
    def __init__(self, key):
        self.key = key
        self.opener = urllib.request.build_opener(NoRedirect())

    def json(self, url, payload=None):
        queue_url(url)
        headers = {"Authorization": "Key " + self.key, "Accept": "application/json"}
        data = None
        if payload is not None:
            headers.update({"Content-Type": "application/json", "X-Fal-No-Retry": "1"})
            data = json.dumps(payload).encode()
        request = urllib.request.Request(url, data=data, headers=headers)
        try:
            with self.opener.open(request, timeout=90) as response:
                body = response.read(8 * 1024 * 1024 + 1)
                if len(body) > 8 * 1024 * 1024:
                    raise RuntimeError("Provider response too large.")
                return json.loads(body)
        except urllib.error.HTTPError as error:
            messages = {401: "FAL authentication failed. Check the server API key.",
                        402: "FAL credits are insufficient. Add credits to the FAL account.",
                        403: "FAL refused this model or request. Check model access in FAL.",
                        422: "FAL rejected these generation parameters or reference. Check the request in FAL.",
                        429: "FAL rate limit reached. Wait before submitting another take."}
            # Read only an error category; never forward provider-echoed inputs,
            # base64 references, prompts or credentials to browser/log output.
            message = messages.get(error.code, f"FAL returned HTTP {error.code}.")
            if error.code == 422:
                try:
                    details = json.loads(error.read(65536)).get("detail", [])
                    if isinstance(details, list) and any(isinstance(d, dict) and d.get("type") == "content_policy_violation" for d in details):
                        message = "FAL's model safety filter refused this reference (people/privacy or content check). The original is unchanged. Use a permitted reference; this attempt will not be retried."
                except (ValueError, AttributeError):
                    pass
            error_type = SubmissionRejected if 400 <= error.code < 500 and error.code != 408 else RuntimeError
            raise error_type(message) from None
        except (urllib.error.URLError, TimeoutError):
            raise ConnectionError("FAL connection interrupted. Check the provider queue before retrying a submission.") from None

    def download(self, url, destination):
        media_url(url)
        # No Authorization header is sent to the media CDN.
        with self.opener.open(urllib.request.Request(url), timeout=120) as response, destination.open("wb") as output:
            written = 0
            while True:
                chunk = response.read(256 * 1024)
                if not chunk:
                    break
                written += len(chunk)
                if written > 300 * 1024 * 1024:
                    raise RuntimeError("Generated file exceeds the 300 MB download limit.")
                output.write(chunk)
            if not written:
                raise RuntimeError("FAL returned an empty output file.")


class Generator:
    def __init__(self, library, key=None, state_dir=None, output_dir=None, transport=None,
                 poll_seconds=6, autostart=True):
        self.library = library
        self.key = os.environ.get("FAL_KEY", "") if key is None else key
        self.state_dir = Path(state_dir or HERE / ".state" / "generation")
        self.output_dir = Path(output_dir or HERE / "generated")
        self.transport = transport or FalTransport(self.key)
        self.poll_seconds = poll_seconds
        self.lock = threading.RLock()
        self.slots = threading.BoundedSemaphore(2)
        self.jobs = {}
        self.autostart = autostart
        for path in self.state_dir.glob("*.json"):
            try:
                job = json.loads(path.read_text())
                if (not isinstance(job, dict) or not isinstance(job.get("id"), str)
                        or not re.fullmatch(r"[a-f0-9]{32}", job["id"])
                        or path.stem != job["id"] or not isinstance(job.get("createdAt"), str)
                        or not isinstance(job.get("status"), str)
                        or not isinstance(job.get("model"), str) or job["model"] not in MODELS):
                    continue
                if job.get("status") in ACTIVE:
                    if job.get("requestId") and self.key:
                        job["status"] = "reconnecting"
                    else:
                        job.update(status="interrupted", error="Server stopped. No automatic resubmission; check FAL before retrying.")
                self.jobs[job["id"]] = job
            except (ValueError, OSError):
                continue
        if autostart:
            for job in list(self.jobs.values()):
                if job["status"] == "reconnecting":
                    threading.Thread(target=self._run, args=(job["id"], True), daemon=True).start()

    def config(self):
        return {"configured": bool(self.key), "provider": "fal", "concurrency": 2,
                "models": [{k: v for k, v in model.items() if k != "endpoint"} for model in MODELS.values()],
                "message": "FAL key loaded in server memory." if self.key else "Start the server with --fal-key-stdin or FAL_KEY."}

    def _public(self, job):
        return {k: v for k, v in job.items() if k not in {"statusUrl", "responseUrl"}}

    def list_jobs(self):
        with self.lock:
            return {"jobs": [self._public(j) for j in sorted(self.jobs.values(), key=lambda j: j["createdAt"], reverse=True)]}

    def get(self, job_id):
        with self.lock:
            return self._public(self.jobs[job_id]) if job_id in self.jobs else None

    def _save(self, job_id, **changes):
        with self.lock:
            job = self.jobs[job_id]
            job.update(changes, updatedAt=now())
            self.state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
            target = self.state_dir / (job_id + ".json")
            temporary = target.with_suffix(".tmp")
            temporary.write_text(json.dumps(job, indent=2, ensure_ascii=False))
            temporary.replace(target)

    def submit(self, payload):
        if not isinstance(payload, dict):
            raise ValueError("Generation request must be an object.")
        if not self.key:
            raise RuntimeError("FAL is not configured. Start the server with --fal-key-stdin or FAL_KEY.")
        model_id = payload.get("model")
        model = MODELS.get(model_id) if isinstance(model_id, str) else None
        if not model:
            raise ValueError("Choose a supported generation model.")
        prompt = payload.get("prompt")
        if not isinstance(prompt, str) or not 10 <= len(prompt.strip()) <= 12000:
            raise ValueError("Write a scene prompt of 10 to 12,000 characters.")
        source_id = payload.get("sourceId")
        source = self.library.get(source_id) if isinstance(source_id, str) else None
        if not source or source.get("kind") not in {"image", "video"}:
            raise ValueError("Select an existing image or video from the gallery.")
        reference_id = payload.get("referenceId")
        if reference_id is not None and not isinstance(reference_id, str):
            raise ValueError("The reference must be an image in the gallery.")
        reference_id = reference_id or None
        if reference_id and (not isinstance(reference_id, str) or not self.library.get(reference_id)
                             or self.library.get(reference_id).get("kind") != "image"):
            raise ValueError("The reference must be an image in the gallery.")
        source_frame = payload.get("sourceFrame", 0)
        if type(source_frame) is not int or source_frame < 0:
            raise ValueError("The source frame must be a non-negative integer.")
        if source["kind"] == "video" and source_frame >= source.get("durationFrames", 0):
            raise ValueError("The reference frame is beyond the source video.")
        duration = payload.get("duration", 5) if model["kind"] == "video" else None
        if model["kind"] == "video" and (type(duration) is not int or duration not in model["durations"]):
            raise ValueError("Choose a duration supported by the selected model.")
        with self.lock:
            # A double click or repeated HTTP request must not incur a second charge.
            signature = (source_id, reference_id, source_frame, model["id"], duration, prompt.strip())
            for existing in self.jobs.values():
                other = tuple(existing.get(k) for k in ("sourceId", "referenceId", "sourceFrame", "model", "duration", "prompt"))
                if existing["status"] in ACTIVE and other == signature:
                    return self._public(existing)
            if sum(j["status"] in ACTIVE for j in self.jobs.values()) >= 8:
                raise RuntimeError("Eight generations are already pending. Wait for a result.")
            job_id = uuid.uuid4().hex
            self.jobs[job_id] = {"id": job_id, "status": "queued", "sourceId": source_id,
                                 "referenceId": reference_id, "sourceFrame": source_frame,
                                 "model": model["id"], "kind": model["kind"], "duration": duration,
                                 "prompt": prompt.strip(), "createdAt": now()}
            self._save(job_id)
            response = self.get(job_id)
        if self.autostart:
            threading.Thread(target=self._run, args=(job_id,), daemon=True).start()
        return response

    def _reference(self, job, folder):
        source = self.library.get(job["sourceId"])
        reference = self.library.path_for(job["referenceId"] or job["sourceId"])
        if reference is None or not reference.is_file():
            raise RuntimeError("Reference media is no longer available.")
        if not job["referenceId"] and source["kind"] == "video":
            frame = folder / "start-frame.png"
            ffmpeg = shutil.which("ffmpeg")
            if not ffmpeg:
                raise RuntimeError("FFmpeg is required to extract a reference frame.")
            result = subprocess.run([ffmpeg, "-v", "error", "-ss", str(job["sourceFrame"] / 24),
                                     "-i", str(reference), "-frames:v", "1", "-y", str(frame)],
                                    capture_output=True, timeout=45)
            if result.returncode or not frame.is_file():
                raise RuntimeError("Could not extract the selected source frame.")
            reference = frame
        if reference.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            raise ValueError("Choose a PNG, JPEG or WebP reference.")
        if reference.stat().st_size > 30 * 1024 * 1024:
            raise ValueError("Reference images must be 30 MB or smaller.")
        mime = mimetypes.guess_type(reference.name)[0] or "image/png"
        return f"data:{mime};base64," + base64.b64encode(reference.read_bytes()).decode()

    def _payload(self, job, reference):
        payload = {"prompt": job["prompt"]}
        if job["model"] == "nano-banana2":
            payload.update(image_urls=[reference], num_images=1, resolution="2K", output_format="png", aspect_ratio="auto")
        else:
            payload.update(image_url=reference, duration=str(job["duration"]))
            if job["model"] == "seedance25":
                payload.update(resolution="720p", generate_audio=False, aspect_ratio="auto", codec="H264")
        return payload

    def _verify(self, path, kind):
        ffprobe = shutil.which("ffprobe")
        if not ffprobe:
            raise RuntimeError("FFprobe is required to validate the generated media.")
        result = subprocess.run([ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                                capture_output=True, timeout=30)
        if result.returncode:
            raise RuntimeError("The generated media could not be decoded.")
        info = json.loads(result.stdout)
        stream = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)
        if not stream or stream.get("width", 0) < 32 or stream.get("height", 0) < 32:
            raise RuntimeError("The generated file contains no usable image or video.")
        if kind == "video" and float(info.get("format", {}).get("duration", 0)) <= 0:
            raise RuntimeError("The generated video has no duration.")

    def _run(self, job_id, resume=False):
        with self.slots:
            with self.lock:
                job = self.jobs[job_id]
            folder = self.output_dir / job_id
            submitted = bool(job.get("requestId"))
            submitting = False
            try:
                folder.mkdir(parents=True, exist_ok=True)
                if not resume:
                    self._save(job_id, status="preparing")
                    reference = self._reference(job, folder)
                    payload = self._payload(job, reference)
                    self._save(job_id, status="submitting")
                    submitting = True
                    response = self.transport.json("https://queue.fal.run/" + MODELS[job["model"]]["endpoint"], payload)
                    request_id = response.get("request_id", "") if isinstance(response, dict) else ""
                    if not isinstance(request_id, str) or not SAFE_ID.fullmatch(request_id):
                        raise RuntimeError("FAL returned no valid request ID. Check the provider dashboard before retrying.")
                    submitted = True
                    # Preserve the billing receipt even if the remaining response is malformed.
                    self._save(job_id, requestId=request_id)
                    self._save(job_id, statusUrl=queue_url(response.get("status_url")),
                               responseUrl=queue_url(response.get("response_url")), status="in_queue")
                    submitting = False
                deadline = time.monotonic() + 3600
                while time.monotonic() < deadline:
                    try:
                        result = self.transport.json(job["statusUrl"])
                    except ConnectionError:
                        self._save(job_id, status="reconnecting")
                        time.sleep(self.poll_seconds * 2)
                        continue
                    status = result.get("status")
                    if result.get("error"):
                        raise RuntimeError("FAL could not generate this take. Review the request in your FAL history.")
                    if status == "COMPLETED":
                        break
                    if status not in {"IN_QUEUE", "IN_PROGRESS"}:
                        raise RuntimeError("Unexpected FAL job status. Check the provider dashboard.")
                    new_status = "in_queue" if status == "IN_QUEUE" else "in_progress"
                    if job["status"] != new_status:
                        self._save(job_id, status=new_status)
                    time.sleep(self.poll_seconds)
                else:
                    raise RuntimeError("FAL is still pending after one hour. Check the saved request ID before retrying.")
                self._save(job_id, status="downloading")
                response = self.transport.json(job["responseUrl"])
                output = response["images"][0] if job["kind"] == "image" else response["video"]
                path = folder / ("media.png" if job["kind"] == "image" else "media.mp4")
                temporary = path.with_name(".pending-" + path.name)
                self.transport.download(media_url(output["url"]), temporary)
                self._verify(temporary, job["kind"])
                temporary.replace(path)
                source = self.library.get(job["sourceId"])
                source_name = source.get("name", "Scene") if source else "Scene"
                manifest = {"assets": [{"file": path.name, "kind": job["kind"],
                                       "title": str(source_name) + " · " + MODELS[job["model"]]["name"],
                                       "model": MODELS[job["model"]]["name"], "provider": "fal",
                                       "prompt": job["prompt"], "sourceId": job["sourceId"],
                                       "referenceId": job["referenceId"], "referenceIds": [job["referenceId"]] if job["referenceId"] else [],
                                       "requestId": job["requestId"], "createdAt": job["createdAt"],
                                       "reviewStatus": "candidate", "teamApproved": False}]}
                (folder / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
                snapshot = self.library.refresh()
                record = next((a for a in snapshot["assets"] if self.library.path_for(a["id"]) == path.resolve()), None)
                if not record:
                    raise RuntimeError("Generation downloaded but gallery indexing failed. The file is preserved on disk.")
                self._save(job_id, status="completed", outputId=record["id"], url=record["url"], completedAt=now())
            except Exception as error:
                # Never persist raw provider bodies/URLs or exception repr (may contain credentials).
                if isinstance(error, (RuntimeError, ValueError, ConnectionError)):
                    message = str(error)[:350]
                    if self.key:
                        message = message.replace(self.key, "[redacted]")
                else:
                    message = "Generation could not complete locally. Inspect the saved FAL request ID before retrying."
                state = "submission_unknown" if submitting and not isinstance(error, SubmissionRejected) else "failed"
                self._save(job_id, status=state, error=message, mayHaveBeenCharged=submitted or (submitting and not isinstance(error, SubmissionRejected)))
