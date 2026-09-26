#!/usr/bin/env python3
"""Backend checks. Add --smoke for a three-source, three-second real MP4 export."""

import array
import copy
import http.client
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest

import server


SMOKE = "--smoke" in sys.argv
if SMOKE:
    sys.argv.remove("--smoke")


def recipe():
    return {"version": 1, "fps": 24, "segments": [
        {"id": "first", "sourceId": "veo31", "inFrame": 0, "outFrame": 24},
    ]}


class RecipeTests(unittest.TestCase):
    def test_accepts_reordering_and_reuse_without_mutating_input(self):
        data = recipe()
        data["segments"] = [
            {"id": "b", "sourceId": "kling3", "inFrame": 24, "outFrame": 48},
            {"id": "a", "sourceId": "veo31", "inFrame": 0, "outFrame": 24},
            {"id": "c", "sourceId": "seedance25", "inFrame": 24, "outFrame": 48},
        ]
        untouched = copy.deepcopy(data)
        result = server.validate_recipe(data)
        self.assertEqual(result, untouched)
        result["segments"][0]["inFrame"] = 30
        self.assertEqual(data, untouched)

    def test_rejects_bad_frames_sources_versions_and_duration(self):
        for field, value in [("inFrame", True), ("inFrame", 0.5), ("inFrame", -1),
                             ("outFrame", 0), ("outFrame", 1825),
                             ("sourceId", "../../etc/passwd"), ("id", "")]:
            with self.subTest(field=field, value=value):
                data = recipe()
                data["segments"][0][field] = value
                with self.assertRaises(server.ValidationError):
                    server.validate_recipe(data)
        for field, value in [("version", True), ("version", 2), ("fps", 30),
                             ("segments", []), ("segments", None)]:
            data = recipe()
            data[field] = value
            with self.assertRaises(server.ValidationError):
                server.validate_recipe(data)
        data = recipe()
        data["segments"] *= 2
        with self.assertRaisesRegex(server.ValidationError, "unique"):
            server.validate_recipe(data)
        data["segments"] = [{"id": str(i), "sourceId": "veo31", "inFrame": 0, "outFrame": 1824}
                            for i in range(2)]
        with self.assertRaisesRegex(server.ValidationError, "80-second"):
            server.validate_recipe(data)
        data["segments"] = [{"id": str(i), "sourceId": "veo31", "inFrame": 0, "outFrame": 1}
                            for i in range(201)]
        with self.assertRaises(server.ValidationError):
            server.validate_recipe(data)

    def test_exact_80_second_boundary_is_valid(self):
        data = recipe()
        data["segments"] = [
            {"id": "a", "sourceId": "veo31", "inFrame": 0, "outFrame": 1824},
            {"id": "b", "sourceId": "kling3", "inFrame": 0, "outFrame": 96},
        ]
        server.validate_recipe(data)
        data["segments"][1]["outFrame"] += 1
        with self.assertRaises(server.ValidationError):
            server.validate_recipe(data)


class RangeTests(unittest.TestCase):
    def test_closed_open_and_suffix_ranges(self):
        self.assertEqual(server.parse_range("bytes=2-5", 10), (2, 5))
        self.assertEqual(server.parse_range("bytes=2-", 10), (2, 9))
        self.assertEqual(server.parse_range("bytes=-3", 10), (7, 9))
        self.assertEqual(server.parse_range("bytes=-30", 10), (0, 9))
        self.assertEqual(server.parse_range("bytes=2-30", 10), (2, 9))

    def test_unsatisfiable_and_multiple_ranges(self):
        for value in ("bytes=10-", "bytes=8-2", "bytes=-0", "bytes=-", "bytes=0-1,4-5", "cats=0-1"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                server.parse_range(value, 10)
        with self.assertRaises(ValueError):
            server.parse_range("bytes=0-1", 0)


class ExportFailureTests(unittest.TestCase):
    def test_encoder_failure_releases_lock_and_removes_temporary_files(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "invalid.mp4"
            source.write_bytes(b"invalid video data")
            output = Path(folder) / "exports"
            manager = server.ExportManager({key: source for key in server.SOURCE_NAMES}, output)
            job = manager.submit(recipe())
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                job = manager.get(job["id"])
                if job["status"] == "failed" and manager.active_id is None:
                    break
                time.sleep(0.02)
            self.assertEqual(job["status"], "failed")
            self.assertIn("FFmpeg", job["error"])
            self.assertIsNone(manager.active_id)
            self.assertEqual(list(output.iterdir()), [])


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.data = bytes(range(256)) * 8
        cls.media = Path(cls.temp.name) / "fake.mp4"
        cls.media.write_bytes(cls.data)
        cls.manager = server.ExportManager({key: cls.media for key in server.SOURCE_NAMES},
                                           Path(cls.temp.name) / "exports")
        cls.http = server.EditorServer(("127.0.0.1", 0), cls.manager)
        cls.thread = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        cls.temp.cleanup()

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.http.server_port, timeout=5)
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        result = response.status, dict(response.headers), response.read()
        connection.close()
        return result

    def test_project_and_byte_ranges(self):
        status, _, body = self.request("GET", "/api/project")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["audioSourceId"], "veo31")
        for spec, expected in [("bytes=4-9", self.data[4:10]),
                               ("bytes=-5", self.data[-5:]),
                               ("bytes=2045-", self.data[2045:])]:
            with self.subTest(spec=spec):
                status, headers, body = self.request("GET", "/media/veo31.mp4", headers={"Range": spec})
                self.assertEqual(status, 206)
                self.assertEqual(body, expected)
                self.assertEqual(int(headers["Content-Length"]), len(expected))
                self.assertIn("Content-Range", headers)
        status, headers, body = self.request("HEAD", "/media/veo31.mp4", headers={"Range": "bytes=4-9"})
        self.assertEqual((status, body, headers["Content-Length"]), (206, b"", "6"))
        status, headers, body = self.request("GET", "/media/veo31.mp4", headers={"Range": "bytes=2048-"})
        self.assertEqual(status, 416)
        self.assertEqual(headers["Content-Range"], "bytes */2048")

    def test_rejects_traversal_wrong_hosts_cross_origin_and_invalid_payloads(self):
        for path in ("/../server.py", "/%2e%2e/%2e%2e/.git/config", "/creative/%2e%2e/.git/config",
                     "/media/../../README.md", "/exports/../../README.md"):
            with self.subTest(path=path):
                self.assertEqual(self.request("GET", path)[0], 404)
        self.assertEqual(self.request("GET", "/api/project", headers={"Host": "attacker.example"})[0], 403)
        self.assertEqual(self.request("GET", "/api/project", headers={"Origin": "https://attacker.example"})[0], 403)
        self.assertEqual(self.request("POST", "/api/export", "{}", {"Content-Type": "text/plain"})[0], 415)
        for payload in ("not-json", "[]", "{}", json.dumps({"version": 1, "fps": 24, "segments": []})):
            self.assertEqual(self.request("POST", "/api/export", payload,
                                         {"Content-Type": "application/json"})[0], 400)
        self.assertEqual(self.request("GET", "/api/export/unknown")[0], 404)

    def test_busy_is_explicit(self):
        with self.manager.lock:
            self.manager.active_id = "test-busy"
        try:
            status, _, body = self.request("POST", "/api/export", json.dumps(recipe()),
                                          {"Content-Type": "application/json"})
            self.assertEqual(status, 409)
            self.assertIn("already running", json.loads(body)["error"])
        finally:
            with self.manager.lock:
                self.manager.active_id = None


@unittest.skipUnless(SMOKE, "Pass --smoke for the real three-model export check.")
class RealExportSmokeTest(unittest.TestCase):
    def test_three_sources_frame_boundaries_and_common_soundtrack(self):
        ffmpeg, ffprobe = server.find_program("ffmpeg"), server.find_program("ffprobe")
        output_dir = server.HERE / "exports"
        manager = server.ExportManager(output_dir=output_dir)
        data = {"version": 1, "fps": 24, "segments": [
            {"id": "basket", "sourceId": "seedance25", "inFrame": 697, "outFrame": 721},
            {"id": "salsa", "sourceId": "kling3", "inFrame": 937, "outFrame": 961},
            {"id": "return", "sourceId": "veo31", "inFrame": 1585, "outFrame": 1609},
        ]}
        job = manager.submit(data)
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            job = manager.get(job["id"])
            if job["status"] in {"completed", "failed"}:
                break
            time.sleep(0.25)
        self.assertEqual(job["status"], "completed", job)
        output = output_dir / f"{job['id']}.mp4"
        info = json.loads(subprocess.check_output([
            ffprobe, "-v", "error", "-count_frames", "-show_entries",
            "stream=codec_type,nb_read_frames,width,height,avg_frame_rate:format=duration",
            "-of", "json", str(output),
        ]))
        video = next(s for s in info["streams"] if s["codec_type"] == "video")
        self.assertEqual(int(video["nb_read_frames"]), 72)
        self.assertEqual(video["avg_frame_rate"], "24/1")
        self.assertEqual((video["width"], video["height"]), (1920, 1080))
        self.assertLess(abs(float(info["format"]["duration"]) - 3), 0.01)

        def frame(path, number):
            return subprocess.check_output([
                ffmpeg, "-v", "error", "-i", str(path), "-vf",
                f"select=eq(n\\,{number}),scale=64:36", "-frames:v", "1",
                "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1",
            ])

        errors = []
        for index, segment in enumerate(data["segments"]):
            for offset in (0, 23):
                wanted = frame(server.SOURCES[segment["sourceId"]], segment["inFrame"] + offset)
                actual = frame(output, index * 24 + offset)
                self.assertEqual(len(actual), 64 * 36 * 3)
                mean_error = sum(abs(a - b) for a, b in zip(actual, wanted)) / len(actual)
                errors.append(round(mean_error, 4))
                self.assertLess(mean_error, 4, f"Wrong frame at model splice {index}, offset {offset}")

        # The output's audio must match the Veo intervals, even where the image
        # source is Seedance/Kling. Compare decoded waveforms after AAC encoding.
        audio_filter = ";".join(
            f"[0:a]atrim=start_sample={s['inFrame'] * 2000}:end_sample={s['outFrame'] * 2000},"
            f"asetpts=PTS-STARTPTS[a{i}]" for i, s in enumerate(data["segments"]))
        audio_filter += ";[a0][a1][a2]concat=n=3:v=0:a=1[out]"
        expected = subprocess.check_output([
            ffmpeg, "-v", "error", "-i", str(server.SOURCES["veo31"]), "-filter_complex", audio_filter,
            "-map", "[out]", "-ar", "48000", "-ac", "1", "-f", "f32le", "pipe:1",
        ])
        actual = subprocess.check_output([
            ffmpeg, "-v", "error", "-i", str(output), "-vn", "-ar", "48000", "-ac", "1",
            "-f", "f32le", "pipe:1",
        ])
        x, y = array.array("f"), array.array("f")
        x.frombytes(expected)
        y.frombytes(actual)
        length = min(len(x), len(y))
        dot = sum(x[i] * y[i] for i in range(length))
        norm = math.sqrt(sum(v * v for v in x[:length]) * sum(v * v for v in y[:length]))
        correlation = dot / norm
        self.assertGreater(correlation, 0.97)
        report = {"passed": True, "video": str(output.relative_to(server.REPO)),
                  "durationSeconds": 3, "frames": 72, "frameMeanAbsoluteErrors": errors,
                  "audioSource": "veo31", "audioCorrelation": round(correlation, 6)}
        (output_dir / "smoke-test-report.json").write_text(json.dumps(report, indent=2) + "\n")
        print("\nSMOKE:", json.dumps(report), flush=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
