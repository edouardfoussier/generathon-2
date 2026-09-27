#!/usr/bin/env python3
"""Seed the Luna/Rafa scene workshop from the actual refinement-v4 edit.

Local-only: reads existing manifests/prompts/media, extracts JPEG posters,
full-resolution frames and edited scene previews, and writes project.json.
Never calls a generation provider.
Re-running intentionally resets project.json to its provenance-backed baseline.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CREATIVE = REPO / "creative"
FPS = 24
REPORT = CREATIVE / "refinement-v4/qa/render-report.json"
REF_MANIFEST = CREATIVE / "continuity-study/manifest.json"
FILM_A = CREATIVE / "refinement-v4/renders/converse-refinement-v4-music-a-76s.mp4"
FILM_B = CREATIVE / "refinement-v4/renders/converse-refinement-v4-music-b-76s.mp4"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def url(path: Path) -> str:
    return "/" + path.resolve().relative_to(REPO).as_posix()


def frames(seconds: float) -> int:
    result = round(seconds * FPS)
    if abs(result / FPS - seconds) > 1e-8:
        raise ValueError(f"Non-frame-aligned time: {seconds}")
    return result


def character(identifier, label, age, position, color):
    return {"id": identifier, "label": label, "age": age, "position": position, "color": color}


LUNA = character("luna", "Luna", 15, [-0.45, 0, 0.1], "#747a54")
RAFA16 = character("rafa", "Rafa · 16 ans", 16, [0, 0, 0], "#e5dbc6")
RAFA23 = character("rafa", "Rafa · 23 ans", 23, [-0.65, 0, 0], "#b26842")
ELENA22 = character("elena", "Elena · 22 ans", 22, [0.65, 0, 0], "#875d91")
RAFA24 = character("rafa", "Rafa · 24 ans", 24, [-0.55, 0, 0], "#4c5757")
ELENA23 = character("elena", "Elena · 23 ans", 23, [0.55, 0, 0], "#ece1cb")
RAFA25 = character("rafa", "Rafa · 25 ans", 25, [-0.5, 0, 0], "#b99365")
ELENA24 = character("elena", "Elena · 24 ans", 24, [0.55, 0, -0.2], "#9b7a79")
BABY = character("mother-baby", "Leur fille · future Maman", 0, [-0.4, 1.05, 0.3], "#efe3bc")
RAFA41 = character("rafa", "Rafa · 41 ans", 41, [0.65, 0, 0], "#7c9cb0")
MOM16 = character("mother", "Maman · 16 ans", 16, [-0.65, 0, 0.15], "#6e90ac")
MOM47 = character("mother", "Maman · 47 ans", 47, [1.7, 0, -1.5], "#99846b")


# Camera/blocking is an editable spatial starting point, not solved from footage.
# Y is vertical; one unit is approximately one metre; floor is Y=0.
def block(location, people, position, target, fov=45, warmth=0.72, intensity=1.1):
    return {
        "location": location,
        "characters": deepcopy(people),
        "camera": {"position": position, "target": target, "fov": fov},
        "lighting": {"warmth": warmth, "intensity": intensity},
    }


SPECS = [
    ("opening", "Le grenier", "Luna cherche les vêtements d’hiver ; son agacement précède la découverte.", "opening", block("attic", [LUNA], [2.6, 1.7, 5.4], [-0.3, 1.05, 0], 47)),
    ("shoebox", "La boîte", "Elle ouvre la boîte et découvre la paire héritée et la photographie de Rafa.", "opening", block("attic", [LUNA], [0.8, 2.5, 2.8], [-0.25, 0.65, 0.25], 42)),
    ("photograph-insert", "La photographie · insert", "Rapprochement éditorial sur la photographie, extrait du même plan de découverte.", "opening", block("attic", [LUNA], [0.5, 2.0, 1.7], [-0.25, 0.75, 0.25], 34)),
    ("phone", "Une question au téléphone", "Luna photographie le tirage paysage puis attend une réponse qui ne lui apprend pas à connaître Rafa.", "phone", block("attic", [LUNA], [1.0, 1.65, 2.3], [-0.25, 1.05, 0.15], 40)),
    ("putting-on-shoes", "La paire héritée", "Luna enfile les Converse de Rafa ; le lien avec les souvenirs se prépare.", "opening", block("attic", [LUNA], [1.2, 0.55, 2.4], [-0.2, 0.3, 0.25], 38)),
    ("laces-insert", "Lacets et toile · insert", "Détail recadré des lacets et de la toile ; ce n’est pas une nouvelle prise générée.", "opening", block("attic", [LUNA], [0.65, 0.35, 1.35], [-0.2, 0.16, 0.3], 32)),
    ("first-memory", "Le premier souvenir", "L’appui dans le grenier devient un appui sur le terrain ; Rafa adolescent est révélé.", "opening", block("basketball", [RAFA16], [2.8, 1.2, 5.0], [0, 1.0, 0], 46, 0.55, 1.2)),
    ("basketball", "Le tir de Rafa", "Un tir, le filet, un sourire et la réception : l’énergie de Rafa à seize ans.", "basketball", block("basketball", [RAFA16], [3.5, 1.65, 5.5], [0, 1.25, 0], 48, 0.55, 1.2)),
    ("shoes-meet", "Les chaussures se rencontrent", "Les Converse noires de Rafa rencontrent la paire rouge d’Elena sur la piste.", "salsa", block("salsa", [RAFA23, ELENA22], [0.25, 0.5, 2.6], [0, 0.18, 0], 38, 0.85, 1.15)),
    ("salsa", "La rencontre avec Elena", "Un regard timide, une main offerte et les premiers pas à deux. Le rendu original FG01 est conservé.", "salsa", block("salsa", [RAFA23, ELENA22], [0.5, 1.65, 4.4], [0, 1.2, 0], 44, 0.85, 1.15)),
    ("dance-step", "Le pas de danse", "Le mouvement des chaussures conclut la danse et prépare le saut dans le temps.", "salsa", block("salsa", [RAFA23, ELENA22], [0.7, 0.55, 2.8], [0, 0.25, 0], 37, 0.85, 1.15)),
    ("wedding", "Le mariage", "Rafa et Elena mariés se retrouvent devant la porte, dans une ellipse brève et tendre.", "wedding", block("wedding", [RAFA24, ELENA23], [0, 1.7, 5.0], [0, 1.1, 0], 44, 0.68, 1.2)),
    ("newborn", "Une nouvelle famille", "Rafa porte leur fille nouveau-née, future mère de Luna ; Elena se penche près d’eux.", "newborn", block("nursery", [RAFA25, ELENA24, BABY], [1.5, 1.6, 3.8], [-0.1, 1.1, 0.05], 42, 0.83, 0.95)),
    ("handover", "La transmission", "En 1995, Rafa offre la paire à sa fille adolescente et ajuste le lacet d’un geste attentionné.", "handover", block("handover", [RAFA41, MOM16], [0.5, 1.3, 4.2], [0, 0.8, 0], 46, 0.78, 1.0)),
    ("shared-smile", "Le sourire partagé", "Le père et sa fille échangent un sourire après le geste du lacet.", "handover", block("handover", [RAFA41, MOM16], [0.35, 1.55, 3.0], [0, 1.0, 0], 39, 0.78, 1.0)),
    ("daughter-reaction", "Le regard de sa fille · insert", "Rapprochement éditorial sur la réaction de la jeune mère ; l’appel de Maman commence sur ce souvenir.", "handover", block("handover", [RAFA41, MOM16], [-0.65, 1.5, 2.5], [-0.5, 1.0, 0.1], 32, 0.78, 1.0)),
    ("luna-return", "Retour à Luna", "La voix de sa mère ramène Luna au grenier ; le visage original FG01 reste la référence.", "return", block("attic", [LUNA], [0.9, 1.45, 2.8], [-0.35, 1.1, 0.05], 37)),
    ("photo-return", "La photo retrouve sa place", "Luna replace délicatement la photographie dans la boîte, les chaussures restant à ses pieds.", "return", block("attic", [LUNA], [0.9, 2.2, 2.6], [-0.3, 0.75, 0.15], 40)),
    ("tell-me", "Raconte-moi Grandpa", "Luna demande à sa mère de lui parler de Rafa ; Maman répond par un sourire.", "return", block("attic", [LUNA, MOM47], [-1.8, 1.6, 3.3], [0.65, 1.2, -0.65], 46)),
    ("endline", "Conserve what matters", "Carton éditorial : une chaussure existante et une composition typographique, sans nouvelle génération.", "endcard", block("product", [], [0, 0.6, 2.5], [0, 0.35, 0], 38, 0.75, 1.1)),
]


def load_prompt(key: str):
    if key == "opening":
        path = CREATIVE / "continuity-video-v1/jobs/opening-g.json"
        data = read(path)
        return data["prompt"], data["codes"], path, "prompt", data.get("assetId"), "generated-sequence"
    if key == "phone":
        path = CREATIVE / "refinement-v4/plan.json"
        data = next(item for item in read(path)["scenes"] if item["id"] == "phone-attic-v2")
        return data["prompt"], data["referenceCodes"], path, "scenes[id=phone-attic-v2].prompt", data.get("assetId"), "generated-sequence"
    if key == "endcard":
        # There was no generative prompt. Do not invent one for the interface.
        return "", ["CS02G"], CREATIVE / "gpt-full-film-v1/graphics/provenance.json", None, None, "editorial-composition"
    path = CREATIVE / f"gpt-full-film-v1/jobs/{key}.json"
    data = read(path)
    return data["prompt"], data["referenceCodes"], path, "prompt", data.get("assetId"), "generated-sequence"


def reference(code: str, lookup: dict) -> dict:
    if code == "FG01-PHYSICAL-PRINT-FRAME":
        path = CREATIVE / "refinement-v4/qa/fg01-physical-print-reference.jpg"
        return {"id": code, "label": "Photographie paysage de Rafa · raccord FG01", "url": url(path), "role": "prop"}
    entry = lookup[code]
    path = CREATIVE / "continuity-study" / entry["localFile"]
    if not path.is_file():
        raise FileNotFoundError(path)
    roles = {"characters": "character", "locations": "location", "shoes": "product"}
    return {"id": code, "label": entry["title"]["fr"], "url": url(path), "role": roles[entry["group"]]}


def resolve_recorded_path(recorded: str) -> Path:
    # The historical render report contains an absolute author-machine prefix.
    # Re-anchor its repository-relative media path for another local checkout.
    marker = "/creative/"
    if marker not in recorded:
        raise ValueError(f"Expected a creative media path: {recorded}")
    return CREATIVE / recorded.split(marker, 1)[1]


def make_poster(task: tuple[int, float, Path], ffmpeg: str) -> None:
    _, time, destination = task
    subprocess.run([
        ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{time:.8f}",
        "-i", str(FILM_A), "-frames:v", "1", "-vf", "scale=480:270", "-q:v", "4", str(destination),
    ], check=True, capture_output=True)


def make_image(task: tuple[int, float, Path], ffmpeg: str) -> None:
    _, time, destination = task
    subprocess.run([
        ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{time:.8f}",
        "-i", str(FILM_A), "-frames:v", "1", "-q:v", "2", str(destination),
    ], check=True, capture_output=True)


def make_preview(task: tuple[int, int, Path], ffmpeg: str) -> None:
    first, count, destination = task
    # Accurate input seeking followed by re-encoding preserves the actual v4
    # picture, editorial recrops, phone captions, transitions and score A mix.
    # Limit encoder threads as several short previews are processed in parallel.
    subprocess.run([
        ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{first / FPS:.8f}",
        "-i", str(FILM_A), "-map", "0:v:0", "-map", "0:a:0?",
        "-t", f"{count / FPS:.8f}", "-frames:v", str(count),
        "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-threads", "2",
        "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "160k",
        "-ar", "48000", "-ac", "2", "-movflags", "+faststart", str(destination),
    ], check=True, capture_output=True)


def build(skip_posters: bool = False, skip_videos: bool = False, skip_images: bool = False):
    report = read(REPORT)
    shots = report["shots"]
    if len(shots) != 20 or len(SPECS) != len(shots):
        raise ValueError("Expected the twenty actual v4 editorial segments.")
    if not FILM_A.is_file() or not FILM_B.is_file():
        raise FileNotFoundError("The two complete v4 masters must exist.")
    lookup = {row["code"]: row for row in read(REF_MANIFEST)["assets"]}
    poster_dir = HERE / "assets/posters"
    poster_dir.mkdir(parents=True, exist_ok=True)
    clip_dir = HERE / "assets/clips"
    clip_dir.mkdir(parents=True, exist_ok=True)
    image_dir = HERE / "assets/images"
    image_dir.mkdir(parents=True, exist_ok=True)
    scenes, poster_tasks, preview_tasks, image_tasks = [], [], [], []
    for index, (shot, spec) in enumerate(zip(shots, SPECS), 1):
        slug, title, description, prompt_key, blocking = spec
        scene_id = f"s{index:02d}-{slug}"
        source = resolve_recorded_path(shot["source"])
        if not source.is_file():
            raise FileNotFoundError(source)
        prompt, codes, prompt_path, selector, asset_id, kind = load_prompt(prompt_key)
        first = frames(shot["start"])
        last = first + frames(shot["duration"])
        timeline_first = frames(shot["timelineStart"])
        timeline_last = frames(shot["timelineEnd"])
        poster_path = poster_dir / f"{scene_id}.jpg"
        preview_path = clip_dir / f"{scene_id}.mp4"
        image_path = image_dir / f"{scene_id}.jpg"
        # Choose an exact native frame within the completed v4 master. Its crop,
        # phone captions and end-card typography therefore match the actual edit.
        poster_frame = timeline_first + (timeline_last - timeline_first) // 2
        poster_tasks.append((index, poster_frame / FPS, poster_path))
        image_tasks.append((index, poster_frame / FPS, image_path))
        preview_tasks.append((timeline_first, timeline_last - timeline_first, preview_path))
        aliases = []
        if source.name == "luna-original.mp4":
            aliases.append({
                "mediaUrl": url(source),
                "originalMediaUrl": "/creative/gpt-full-film-v1/videos/return.mp4",
                "originalRangeSeconds": [0, 4],
                "explanation": "FG01-L baseline excerpt; inherits the recorded return generation prompt, not a new Luna generation.",
            })
        if source.name == "salsa-original.mp4":
            aliases.append({
                "mediaUrl": url(source),
                "originalMediaUrl": "/creative/gpt-full-film-v1/videos/salsa.mp4",
                "originalRangeSeconds": [1.5, 6.5],
                "explanation": "FG01-S baseline excerpt between the opening and closing foot inserts; inherits the recorded salsa prompt.",
            })
        provenance = {
            "editReportUrl": url(REPORT),
            "editReportShotIndex": index - 1,
            "timelineInFrame": timeline_first,
            "timelineOutFrame": timeline_last,
            "originalEditLabel": shot["label"],
            "kind": kind,
            "promptSourceUrl": url(prompt_path),
            "promptSelector": selector,
            "promptIsExactRecordedText": bool(prompt),
            "promptScope": "No generation prompt: local crop and typography." if kind == "editorial-composition" else "Exact full source-sequence prompt, inherited by this editorial extract; not a separate generation request for this segment.",
            "sourceGenerationAssetId": asset_id,
            "sourceGenerationModel": None if kind == "editorial-composition" else "Seedance 2.5",
            "referenceImageFamily": "GPT Image 2.5 Sunburst / G continuity",
            "referenceManifestUrl": url(REF_MANIFEST),
            "aliases": aliases,
            "editorialReframe": bool(shot.get("crop")),
            "cropFilter": shot.get("crop"),
            "posterSourceUrl": url(FILM_A),
            "posterFrame": poster_frame,
            "imageSourceUrl": url(FILM_A),
            "imageFrame": poster_frame,
            "imageTreatment": "Full native 1280×720 JPEG from the exact same v4 A frame as the thumbnail poster; no generative processing or upscaling.",
            "previewSourceUrl": url(FILM_A),
            "previewTimelineInFrame": timeline_first,
            "previewTimelineOutFrame": timeline_last,
            "previewTreatment": "Local frame-aligned excerpt of the already rendered v4 A master, H.264 CRF20 fast / AAC. Retains the actual editorial crop, captions and original v4 A music/dialogue mix. Not a new generation or a new audio mix.",
            "blockingOrigin": "Manually seeded editable spatial previz, inferred from the recorded action and reference geography; not camera tracking or reconstruction of generated footage.",
        }
        if kind == "editorial-composition":
            provenance["editorialInstructions"] = "Crop the complete inherited shoe profile from CS02G, arrange on sampled warm paper, and typeset CONVERSE / CONSERVE WHAT MATTERS."
            provenance["compositionSourceUrl"] = "/creative/gpt-full-film-v1/render.py"
        scenes.append({
            "id": scene_id,
            "title": title,
            "description": description,
            "duration": shot["duration"],
            "source": {"url": url(source), "inFrame": first, "outFrame": last, "fps": FPS},
            "poster": url(poster_path),
            "image": url(image_path),
            "previewVideo": {"url": url(preview_path), "inFrame": 0, "outFrame": timeline_last - timeline_first, "fps": FPS},
            "prompt": prompt,
            "references": [reference(code, lookup) for code in codes],
            "blocking": blocking,
            "provenance": provenance,
        })
    if sum(frames(scene["duration"]) for scene in scenes) != 1824:
        raise ValueError("The actual v4 sequence must total 1824 frames / 76 seconds.")
    if not skip_posters or not skip_videos or not skip_images:
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            raise RuntimeError("Local ffmpeg is required for poster/preview extraction.")
    if not skip_posters:
        with ThreadPoolExecutor(max_workers=3) as pool:
            list(pool.map(lambda task: make_poster(task, ffmpeg), poster_tasks))
    if not skip_images:
        with ThreadPoolExecutor(max_workers=3) as pool:
            list(pool.map(lambda task: make_image(task, ffmpeg), image_tasks))
    if not skip_videos:
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda task: make_preview(task, ffmpeg), preview_tasks))
    project = {
        "id": "luna-rafa-v4",
        "title": "Luna & Rafa — Conserve what matters",
        "version": 1,
        "fps": FPS,
        "duration": 76,
        "sourceFilm": {"urlA": url(FILM_A), "urlB": url(FILM_B)},
        "scenes": scenes,
        "provenance": {
            "baselineFilmUrl": "/creative/gpt-full-film-v1/renders/converse-gpt-seedance25-full-76s.mp4",
            "editReportUrl": url(REPORT),
            "selectionStatus": "Latest produced v4 working edit. RF06 phone take is integrated; original FG01 faces retained. No saved user preference between soundtrack A and B is inferred.",
            "pictureIdenticalAcrossSoundtracks": report["soundtrackComparisonPictureVerifiedIdentical"],
            "notTheEarlierPhotographicEditor": "/creative/editor uses the older model-comparison-v3 masters; it is not this v4 selection.",
            "style": "Existing source media are gouache / watercolor 2D. Blocking is a new editable 3D previz only, not newly generated replacement footage.",
            "sourcePromptPolicy": "Keep exact historical generation prompts, including their 2D style restrictions. Adapt style intentionally for a later 3D request; do not present edited text as the historical original.",
            "blockingCoordinates": {"unit": "metres", "upAxis": "Y", "groundY": 0, "warmthRange": [0, 1], "lightIntensityRange": [0, 2]},
            "posterPolicy": "480×270 JPEGs decoded from the midpoint native frame of each actual v4 editorial segment; no image generation.",
            "imagePolicy": "Full-resolution 1280×720 JPEGs from exactly the same native frames as the posters, for the Image tab. No upscaling or generative processing.",
            "previewVideoPolicy": "Twenty locally derived scene excerpts from v4 A at the original 1280×720 / 24 fps. Existing editorial framing and v4 A music/dialogue are preserved. Preview clips are re-encoded H.264/AAC for exact intervals and browser playback; no new generation, replacement voice or remix.",
            "proposalNotUsedAsShotCount": "/creative/refinement-v4/v4-shot-plan.md contains 38 proposed beats, not 38 existing video assets.",
        },
    }
    (HERE / "project.json").write_text(json.dumps(project, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return project


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-posters", action="store_true", help="Preserve any existing JPEG posters.")
    parser.add_argument("--skip-videos", action="store_true", help="Preserve any existing scene-preview MP4s.")
    parser.add_argument("--skip-images", action="store_true", help="Preserve any existing full-resolution JPEG scene images.")
    args = parser.parse_args()
    project = build(skip_posters=args.skip_posters, skip_videos=args.skip_videos, skip_images=args.skip_images)
    print(json.dumps({"project": str(HERE / "project.json"), "scenes": len(project["scenes"]), "duration": project["duration"], "postersGenerated": not args.skip_posters, "imagesGenerated": not args.skip_images, "previewVideosGenerated": not args.skip_videos}, indent=2))
