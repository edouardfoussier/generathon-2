"""Decode delivered style tests and create contact sheets for visual inspection."""
from pathlib import Path
import json
import subprocess
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parent
FFMPEG = "/opt/homebrew/bin/ffmpeg"
FFPROBE = "/opt/homebrew/bin/ffprobe"


def main():
    manifest = json.loads((ROOT / "manifest.json").read_text())
    qa = {"images": [], "videos": []}
    frames_dir = ROOT / "qa"
    frames_dir.mkdir(exist_ok=True)
    for asset in manifest["assets"]:
        path = ROOT / asset["localFile"]
        if not path.exists():
            continue
        if asset["kind"] == "image":
            with Image.open(path) as im:
                dimensions = im.size
                im.verify()
            qa["images"].append({"code": asset["code"], "width": dimensions[0], "height": dimensions[1], "decode": "pass"})
            continue
        probe = json.loads(subprocess.check_output([FFPROBE, "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)]))
        duration = float(probe["format"]["duration"])
        video = next(stream for stream in probe["streams"] if stream["codec_type"] == "video")
        decode = subprocess.run([FFMPEG, "-v", "error", "-i", str(path), "-f", "null", "-"], capture_output=True, text=True)
        if decode.returncode:
            raise RuntimeError(decode.stderr)
        canvas = Image.new("RGB", (1600, 1880), "#eee9df")
        draw = ImageDraw.Draw(canvas)
        for i in range(8):
            at = min(duration - .1, i * duration / 8)
            frame = frames_dir / f"{asset['code']}-{i:02d}.jpg"
            subprocess.run([FFMPEG, "-y", "-v", "error", "-ss", str(at), "-i", str(path), "-frames:v", "1", "-q:v", "2", str(frame)], check=True)
            thumb = ImageOps.contain(Image.open(frame), (790, 444))
            x, y = (i % 2) * 800, (i // 2) * 470
            canvas.paste(thumb, (x, y + 25))
            draw.text((x + 8, y + 6), f"{asset['code']} / {at:.1f}s", fill="#252525")
        contact = frames_dir / f"{asset['code']}-contact-sheet.jpg"
        canvas.save(contact, quality=94)
        qa["videos"].append({"code": asset["code"], "duration": duration, "width": video["width"], "height": video["height"], "fps": video["r_frame_rate"], "videoCodec": video["codec_name"], "bytes": path.stat().st_size, "decode": "pass", "sampleContactSheet": str(contact.relative_to(ROOT))})
    (ROOT / "qa-report.json").write_text(json.dumps(qa, indent=2) + "\n")
    print(json.dumps(qa, indent=2))


if __name__ == "__main__":
    main()
