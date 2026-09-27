"""No paid API calls: provider lifecycle, secret handling and duplicate billing guards."""
import json
import io
import urllib.error
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from generation import Generator, FalTransport, SubmissionRejected, media_url, queue_url


class Library:
    def __init__(self, folder):
        self.folder = folder
        self.input = folder / "reference.png"
        self.input.write_bytes(b"fixture image")
        self.records = {"image": {"id": "image", "name": "Luna", "kind": "image"},
                        "video": {"id": "video", "name": "Luna film", "kind": "video", "durationFrames": 144}}

    def get(self, key):
        return self.records.get(key)

    def path_for(self, key):
        if key in {"image", "video"}:
            return self.input
        return (self.folder / "outputs" / key / "media.png").resolve() if key else None

    def refresh(self):
        for path in self.folder.glob("outputs/*/media.png"):
            key = path.parent.name
            self.records[key] = {"id": key, "kind": "image", "url": "/library/" + key}
        return {"assets": list(self.records.values()), "collections": []}


class Transport:
    def __init__(self):
        self.calls = []
        self.fail_submit = False

    def json(self, url, payload=None):
        self.calls.append((url, payload))
        if payload is not None:
            if self.fail_submit:
                raise ConnectionError("Connection interrupted.")
            return {"request_id": "remote-request", "status_url": "https://queue.fal.run/model/requests/remote-request/status",
                    "response_url": "https://queue.fal.run/model/requests/remote-request"}
        if url.endswith("/status"):
            return {"status": "COMPLETED"}
        return {"images": [{"url": "https://v3.fal.media/generated.png"}]}

    def download(self, url, destination):
        destination.write_bytes(b"generated image")


class GenerationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.library = Library(self.folder)
        self.transport = Transport()
        self.generator = self.build()
        self.payload = {"sourceId": "image", "model": "nano-banana2", "prompt": "Keep Luna's painted face and change only the light."}

    def build(self, key="private-test-key"):
        return Generator(self.library, key=key, state_dir=self.folder / "state", output_dir=self.folder / "outputs",
                         transport=self.transport, autostart=False, poll_seconds=0)

    def test_disabled_without_key_and_validated_model_frames(self):
        with self.assertRaises(RuntimeError):
            self.build("").submit(self.payload)
        for update in ({"model": "unknown"}, {"sourceId": "missing"}, {"referenceId": "video"},
                       {"sourceId": "video", "sourceFrame": 144}, {"sourceFrame": True}, {"prompt": "short"},
                       {"model": "seedance25", "duration": 200}):
            with self.subTest(update=update), self.assertRaises(ValueError):
                self.generator.submit({**self.payload, **update})
        self.assertFalse(self.transport.calls)

    def test_duplicate_pending_requests_share_job_and_slot_limit(self):
        first = self.generator.submit(self.payload)
        self.assertEqual(first["id"], self.generator.submit(self.payload)["id"])
        for i in range(7):
            self.generator.submit({**self.payload, "prompt": self.payload["prompt"] + str(i)})
        with self.assertRaises(RuntimeError):
            self.generator.submit({**self.payload, "prompt": self.payload["prompt"] + "overflow"})
        self.assertEqual(len(self.generator.list_jobs()["jobs"]), 8)
        self.assertEqual(self.generator.submit(self.payload)["id"], first["id"])

    def test_completed_take_indexed_without_overwriting_or_saving_secret(self):
        job = self.generator.submit(self.payload)
        with patch.object(self.generator, "_verify"):
            self.generator._run(job["id"])
        finished = self.generator.get(job["id"])
        self.assertEqual(finished["status"], "completed")
        self.assertTrue(finished["outputId"])
        self.assertEqual(self.library.input.read_bytes(), b"fixture image")
        self.assertNotIn("statusUrl", finished)
        self.assertNotIn("private-test-key", json.dumps(self.generator.config()))
        for file in self.folder.rglob("*.json"):
            self.assertNotIn("private-test-key", file.read_text())
            self.assertNotIn("data:image", file.read_text())
        self.assertEqual(sum(body is not None for _, body in self.transport.calls), 1)

    def test_uncertain_submission_not_retried_on_restart(self):
        self.transport.fail_submit = True
        job = self.generator.submit(self.payload)
        self.generator._run(job["id"])
        self.assertEqual(self.generator.get(job["id"])["status"], "submission_unknown")
        restarted = self.build()
        self.assertEqual(restarted.get(job["id"])["status"], "submission_unknown")
        self.assertEqual(len(self.transport.calls), 1)

    def test_known_request_resumes_without_second_submission(self):
        job = self.generator.submit(self.payload)
        self.generator._save(job["id"], status="in_progress", requestId="remote-request",
                             statusUrl="https://queue.fal.run/model/requests/remote-request/status",
                             responseUrl="https://queue.fal.run/model/requests/remote-request")
        restarted = self.build()
        with patch.object(restarted, "_verify"):
            restarted._run(job["id"], resume=True)
        self.assertEqual(restarted.get(job["id"])["status"], "completed")
        self.assertTrue(all(body is None for _, body in self.transport.calls))

    def test_ambiguous_responses_do_not_lose_charge_warning_or_retry(self):
        for response in ([], {}, {"request_id": []}, {"request_id": "accepted-but-bad-urls", "status_url": None}):
            with self.subTest(response=response):
                job = self.generator.submit({**self.payload, "prompt": self.payload["prompt"] + str(response)})
                with patch.object(self.transport, "json", return_value=response):
                    self.generator._run(job["id"])
                failed = self.generator.get(job["id"])
                self.assertEqual(failed["status"], "submission_unknown")
                self.assertTrue(failed["mayHaveBeenCharged"])
                if isinstance(response, dict) and isinstance(response.get("request_id"), str):
                    self.assertEqual(failed["requestId"], response["request_id"])
                restarted = self.build()
                self.assertEqual(restarted.get(job["id"])["status"], "submission_unknown")

    def test_definitive_rejection_is_not_marked_charged_and_bad_json_is_unknown(self):
        for error, state, charged in ((SubmissionRejected("FAL credits are insufficient."), "failed", False),
                                      (ValueError("Malformed JSON response."), "submission_unknown", True)):
            job = self.generator.submit({**self.payload, "prompt": self.payload["prompt"] + state})
            with patch.object(self.transport, "json", side_effect=error):
                self.generator._run(job["id"])
            result = self.generator.get(job["id"])
            self.assertEqual(result["status"], state)
            self.assertEqual(result["mayHaveBeenCharged"], charged)

    def test_malformed_state_and_request_types_are_rejected_safely(self):
        state_dir = self.folder / "state"
        state_dir.mkdir(exist_ok=True)
        for index, value in enumerate(([], {"id": {}}, {"id": "0" * 32},
                                       {"id": "1" * 32, "createdAt": "now", "status": [], "model": []})):
            (state_dir / (str(index) + '.json')).write_text(json.dumps(value))
        self.assertEqual(self.build().list_jobs(), {"jobs": []})
        for value in ([], {}, False, 1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.generator.submit({**self.payload, "referenceId": value})
        for invalid in (None, [], {}, 2):
            with self.assertRaises(ValueError):
                queue_url(invalid)
            with self.assertRaises(ValueError):
                media_url(invalid)

    def test_partial_download_stays_hidden_from_gallery(self):
        job = self.generator.submit(self.payload)
        destinations = []
        def interrupted(url, path):
            destinations.append(path)
            path.write_bytes(b"partial")
            raise ConnectionError("Interrupted download.")
        with patch.object(self.transport, "download", side_effect=interrupted):
            self.generator._run(job["id"])
        self.assertTrue(destinations[0].name.startswith('.'))
        self.assertFalse((destinations[0].parent / 'media.png').exists())
        self.assertEqual(self.library.input.read_bytes(), b"fixture image")

    def test_auth_and_download_hosts_are_separate_allowlists(self):
        for url in ("http://queue.fal.run/request", "https://queue.fal.run.evil.test/request",
                    "https://secret@queue.fal.run/request", "https://127.0.0.1/request"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                queue_url(url)
        for url in ("http://v3.fal.media/output", "https://fal.media.evil.test/output", "https://localhost/output"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                media_url(url)
        self.assertEqual(media_url("https://v3.fal.media/file.mp4"), "https://v3.fal.media/file.mp4")

    def test_provider_content_refusal_is_explicit_without_echoing_input(self):
        provider = FalTransport("secret-test")
        body = json.dumps({"detail": [{"type": "content_policy_violation", "input": "secret-test data:image/png;base64,private"}]}).encode()
        error = urllib.error.HTTPError("https://queue.fal.run/model", 422, "Invalid", {}, io.BytesIO(body))
        with patch.object(provider.opener, "open", side_effect=error):
            with self.assertRaises(SubmissionRejected) as raised:
                provider.json("https://queue.fal.run/model")
        self.assertIn("safety filter refused", str(raised.exception))
        self.assertNotIn("secret-test", str(raised.exception))
        self.assertNotIn("data:image", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
