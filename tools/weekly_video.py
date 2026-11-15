"""Mayuri'z weekly ads: two 9:16 promo videos + covers + content pack, every week.

  <venv>\\python.exe tools\\weekly_video.py               # next week's pair
  <venv>\\python.exe tools\\weekly_video.py --plan-only   # plan + content pack, no render
  ... --week 2026-W48 --hero <product-id> --products id1,id2,...

Video 1 "Showcase" (midweek): one hero piece, revealed on the music's drop,
macro close-ups, what makes it special, brand, call to action.
Video 2 "Creative" (weekend): fast gift-minded montage of up to 6 pieces.

How it works: products come from the PRODUCTS list in index.html (newest
first, never featured before). Music comes only from the licence-checked list
in tools/video_music.json; each candidate is analysed (tempo, beat steadiness,
drops) and the best fit per style wins, never the same track as last week.
Every scene start is snapped to a beat, then Remotion (video/) renders the
plan, ffmpeg makes the social-ready MP4 (H.264, AAC, -14 LUFS, faststart),
and content.md gets storyboard, captions, hashtags and the schedule.

Needs: numpy + pillow (venv at %LOCALAPPDATA%\\MayurizVideo\\venv, see
video/README.md), video/node_modules (npm install), the music files on the PC.
Output: %USERPROFILE%\\Videos\\Mayuriz Weekly\\<week>\\   State: %LOCALAPPDATA%\\MayurizVideo\\
Nothing is posted: the files are for review first.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

REPO = Path(__file__).resolve().parent.parent
VIDEO = REPO / "video"
PUBLIC = VIDEO / "public"
def find_ffmpeg() -> Path:
    """A full ffmpeg build (needs raw-PCM output for beat analysis, x264, loudnorm).
    Remotion's bundled one lacks the f32le muxer, so it's only a last resort."""
    if os.environ.get("MAYURIZ_FFMPEG"):
        return Path(os.environ["MAYURIZ_FFMPEG"])
    if shutil.which("ffmpeg"):
        return Path(shutil.which("ffmpeg"))
    winget = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Packages"
    found = sorted(winget.glob("Gyan.FFmpeg*/ffmpeg-*/bin/ffmpeg.exe")) if winget.exists() else []
    if found:
        return found[-1]
    return VIDEO / "node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe"


FFMPEG = find_ffmpeg()
MUSIC_DIR = Path(os.environ.get("MAYURIZ_MUSIC_DIR", Path.home() / "Music" / "Copyright Free Music"))
OUT_ROOT = Path(os.environ.get("MAYURIZ_VIDEO_OUT", Path.home() / "Videos" / "Mayuriz Weekly"))
STATE_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "MayurizVideo"
STATE = STATE_DIR / "state.json"
FOCUS_OVERRIDES = REPO / "tools" / "video_focus.json"

SITE = "https://mayurisyarntales.online/"
WEBSITE = "mayurisyarntales.online"
EMAIL = "hello@mayurisyarntales.online"
BRAND_FULL = "Mayuri's Yarn Tales"
TAGLINE = "Every Stitch Tells a Story."
FPS = 30
MAX_FRAMES = 30 * FPS
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))

SHOWCASE_HOOKS = [
    ("Made slowly.", "Loved forever."),
    ("Not just crochet.", "It's art."),
    ("A little piece of", "handmade happiness."),
    ("Handmade", "with love."),
    ("Every stitch,", "by hand."),
]
CREATIVE_HOOKS = [
    ["Your next", "favourite", "handmade", "treasure!"],
    ["Little", "gifts,", "made by", "hand!"],
    ["Not just", "crochet.", "It's", "art!"],
    ["Made", "slowly.", "Loved", "forever."],
]
TAG_HASHTAGS = {
    "Scrunchies": "#crochetscrunchie #scrunchies", "Bows": "#crochetbow #hairbow",
    "Claw Clips": "#clawclip #hairaccessories", "Hair Clips": "#hairclips #hairaccessories",
    "Hair Pins": "#hairpins #hairaccessories", "Hair Bands": "#hairband #hairaccessories",
    "Roses": "#crochetrose #crochetflowers", "Flowers": "#crochetflowers #foreverflowers",
    "Garlands": "#crochetgarland #homedecor", "Keychains": "#crochetkeychain #keychain",
    "Charms": "#bagcharm #crochetcharm", "Hearts": "#crochetheart #giftideas",
    "Bookmarks": "#crochetbookmark #booklover", "Coasters": "#crochetcoaster #homedecor",
    "Bangles": "#crochetbangles #handmadejewellery", "Bags": "#crochetbag #handmadebag",
}


def log(msg: str) -> None:
    print(msg, flush=True)


# ------------------------------------------------------------------ products
def load_products() -> list[dict]:
    html = (REPO / "index.html").read_text(encoding="utf-8")
    block = html.split("/* PRODUCTS:START */")[1].split("/* PRODUCTS:END */")[0]
    out = []
    for entry in block.split("{")[1:]:
        entry = entry.split("}")[0]

        def field(k: str) -> str:
            m = re.search(k + r":\s*'((?:[^'\\]|\\.)*)'", entry)
            return re.sub(r"\\(.)", r"\1", m.group(1)) if m else ""
        p = {k: field(k) for k in ("id", "sku", "name", "tag", "desc", "image")}
        if p["id"] and p["image"] and (REPO / p["image"]).exists():
            out.append(p)
    return out


def eligible(p: dict, featured: dict) -> bool:
    return (p["id"] not in featured and not p["name"].lower().startswith("new piece")
            and "-NEW-" not in p["sku"])


def pick_products(items: list[dict], state: dict, hero_id: str | None, ids: list[str] | None):
    by_id = {p["id"]: p for p in items}
    featured = state.get("featured", {})
    if hero_id:
        hero = by_id[hero_id]
    else:
        hero = next((p for p in items if eligible(p, featured)), items[0])
    if ids:
        montage = [by_id[i] for i in ids]
    else:
        pool = [p for p in items if p["id"] != hero["id"] and eligible(p, featured)]
        montage, tags = [], set()
        for p in pool:  # newest first, one per category
            if p["tag"] not in tags:
                montage.append(p)
                tags.add(p["tag"])
            if len(montage) == 6:
                break
        for p in pool:  # top up if the catalogue is short on categories
            if len(montage) == 6:
                break
            if p not in montage:
                montage.append(p)
    return hero, montage


# ------------------------------------------------------------------ images
def focus_points(path: Path) -> list[dict]:
    """Where the crochet is: the most saturated, non-text region (2 points)."""
    im = Image.open(path).convert("RGB")
    small = im.resize((96, round(96 * im.height / im.width)))
    hsv = np.asarray(small.convert("HSV"), dtype=np.float32) / 255
    s, v = hsv[..., 1], hsv[..., 2]
    weight = (s ** 2) * np.clip(v * 1.4, 0, 1)
    h, w = weight.shape
    weight[: int(h * 0.12)] = 0      # headers / logos usually live at the very top
    weight[int(h * 0.92):] = 0
    weight[:, : int(w * 0.06)] = 0
    weight[:, int(w * 0.94):] = 0
    k = np.ones(9) / 9
    blurred = np.apply_along_axis(lambda r: np.convolve(r, k, "same"), 1, weight)
    blurred = np.apply_along_axis(lambda c: np.convolve(c, k, "same"), 0, blurred)
    pts = []
    for _ in range(2):
        y, x = np.unravel_index(np.argmax(blurred), blurred.shape)
        pts.append({"x": round(float(x / w), 3), "y": round(float(y / h), 3)})
        yy, xx = np.mgrid[0:h, 0:w]
        blurred[((yy - y) / h) ** 2 + ((xx - x) / w) ** 2 < 0.2 ** 2] = 0
    return pts


def stage_image(p: dict) -> str:
    """Copy a photo into video/public/weekly, upscaled with Lanczos + light sharpen
    so close-ups stay crisp (Chrome's own scaling is softer)."""
    dst = PUBLIC / "weekly" / Path(p["image"]).name
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(REPO / p["image"]).convert("RGB")
    if im.height < 1800:  # 1800 keeps close-ups crisp without blowing Chrome's memory
        f = 1800 / im.height
        im = im.resize((round(im.width * f), 1800), Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=55, threshold=2))
    im.save(dst, quality=92)
    # Pre-blurred backdrop: blurring a big photo live on every frame crashes
    # Chrome on an 8 GB PC, so the soft version is made once here.
    soft = im.resize((270, round(270 * im.height / im.width)), Image.LANCZOS)
    soft.filter(ImageFilter.GaussianBlur(9)).save(dst.with_name(dst.stem + "-soft.jpg"), quality=88)
    return f"weekly/{dst.name}"


def make_grain() -> None:
    """Tileable film-grain texture (replaces a per-frame SVG noise filter)."""
    path = PUBLIC / "weekly" / "grain.png"
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(7)
    noise = rng.normal(128, 40, (960, 540)).clip(0, 255).astype(np.uint8)  # shown at 2x
    Image.fromarray(noise, "L").save(path)


# ------------------------------------------------------------------ audio
SR, HOP, NFFT = 22050, 512, 2048
AFPS = SR / HOP


def decode(path: Path, offset: float = 0, duration: float | None = None, sr: int = SR) -> np.ndarray:
    cmd = [str(FFMPEG), "-v", "quiet", "-ss", f"{offset:.3f}"]
    if duration:
        cmd += ["-t", f"{duration:.3f}"]
    cmd += ["-i", str(path), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def onset_envelope(y: np.ndarray) -> np.ndarray:
    win = np.hanning(NFFT).astype(np.float32)
    n = 1 + (len(y) - NFFT) // HOP
    frames = np.lib.stride_tricks.as_strided(y, (n, NFFT), (y.strides[0] * HOP, y.strides[0]))
    logm = np.log1p(100 * np.abs(np.fft.rfft(frames * win, axis=1)))
    flux = np.maximum(0, np.diff(logm, axis=0)).sum(axis=1)
    flux = flux - np.convolve(flux, np.ones(16) / 16, mode="same")
    onset = np.maximum(flux, 0)
    return onset / (onset.std() + 1e-9)


def track_beats(y: np.ndarray) -> tuple[float, float, float, np.ndarray, np.ndarray]:
    """Tempo (autocorrelation, prior ~115 BPM) + Ellis DP beat tracker.
    Returns bpm, periodicity, steadiness, beat times (s), onset envelope."""
    onset = onset_envelope(y)
    ac = np.correlate(onset, onset, mode="full")[len(onset) - 1:]
    lags = np.arange(len(ac))
    bpm_of = 60 * AFPS / np.maximum(lags, 1)
    prior = np.exp(-0.5 * (np.log2(bpm_of / 115) / 0.9) ** 2)
    score = np.where((bpm_of >= 70) & (bpm_of <= 180), ac * prior, 0)
    period = int(np.argmax(score))
    n = len(onset)
    cum, back = onset.copy(), np.full(n, -1)
    for t in range(n):
        lo, hi = max(t - 2 * period, 0), t - period // 2
        if hi <= lo:
            continue
        prev = np.arange(lo, hi)
        cand = cum[prev] - 100 * np.log((t - prev) / period) ** 2
        k = int(np.argmax(cand))
        cum[t], back[t] = onset[t] + cand[k], prev[k]
    beats = [int(np.argmax(cum[-period:]) + n - period)]
    while back[beats[-1]] >= 0:
        beats.append(int(back[beats[-1]]))
    beats = np.array(beats[::-1])
    ibi = np.diff(beats)
    steadiness = float(1 - min(1, ibi.std() / ibi.mean())) if len(ibi) > 4 else 0.0
    return (float(bpm_of[period]), float(ac[period] / (ac[0] + 1e-9)), steadiness,
            beats / AFPS, onset)


def loudness_curve(path: Path, step: float = 0.25, limit: float = 120) -> np.ndarray:
    y = decode(path, 0, limit, sr=11025)
    seg = int(11025 * step)
    n = len(y) // seg
    rms = np.sqrt(np.mean(y[: n * seg].reshape(n, seg) ** 2, axis=1))
    return 20 * np.log10(rms + 1e-9)


def find_drop(db: np.ndarray, step: float = 0.25) -> float | None:
    """Biggest jump in loudness (2 s after vs 2 s before), if it's a real one."""
    w = int(2 / step)
    best, at = 0.0, None
    for i in range(int(4 / step), min(len(db) - w, int(90 / step))):
        jump = db[i:i + w].mean() - db[i - w:i].mean()
        if jump > best:
            best, at = jump, i
    return at * step if at is not None and best >= 9 else None


def analyse_track(path: Path, cache: dict) -> dict:
    key = f"{path.name}|{int(path.stat().st_mtime)}"
    if key in cache:
        return cache[key]
    db = loudness_curve(path)
    drop = find_drop(db)
    loud = np.median(db[db > -50]) if np.any(db > -50) else -20
    first_loud = float(np.argmax(db >= loud - 4) * 0.25)
    y = decode(path, max(first_loud, 0), 45)
    bpm, periodicity, steadiness, _, _ = track_beats(y)
    r = {"bpm": round(bpm, 1), "periodicity": round(periodicity, 3), "steadiness": round(steadiness, 3),
         "drop": drop, "first_loud": first_loud, "loud_db": round(float(loud), 1)}
    cache[key] = r
    return r


def style_score(style: str, a: dict) -> float:
    bpm = a["bpm"]
    if style == "creative":
        tempo = np.exp(-0.5 * ((bpm - 112) / 14) ** 2)
        return 2 * a["periodicity"] + 2 * a["steadiness"] + 1.5 * tempo
    tempo = np.exp(-0.5 * ((bpm - 95) / 18) ** 2)
    return 2 * a["periodicity"] + 1.5 * a["steadiness"] + tempo + (1.2 if a["drop"] else 0)


def weeks_between(a: str, b: str) -> int:
    def monday(w: str) -> dt.date:
        y, n = w.split("-W")
        return dt.date.fromisocalendar(int(y), int(n), 1)
    return abs((monday(b) - monday(a)).days) // 7


def pick_music(style: str, state: dict, week: str, exclude: set[str], cache: dict) -> tuple[dict, dict]:
    cfg = json.loads((REPO / "tools" / "video_music.json").read_text(encoding="utf-8"))
    recent = {tid for tid, wk in state.get("music", {}).items() if wk != week and weeks_between(wk, week) <= 2}
    best = None
    for t in cfg["approved"]:
        path = MUSIC_DIR / t["file"]
        if style not in t["styles"] or t["id"] in exclude or not path.exists():
            continue
        a = analyse_track(path, cache)
        s = style_score(style, a) - (3 if t["id"] in recent else 0)
        log(f"  {style:9s} {t['id']:15s} bpm {a['bpm']:6.1f} per {a['periodicity']:.2f} "
            f"steady {a['steadiness']:.2f} drop {a['drop']}  score {s:.2f}")
        if best is None or s > best[0]:
            best = (s, t, a)
    if not best:
        raise SystemExit(f"no approved {style} track found in {MUSIC_DIR}")
    return best[1], best[2]


# ------------------------------------------------------------------ edit plans
def beat_grid(path: Path, start: float, seconds: float = 36) -> tuple[list[int], float, np.ndarray]:
    """Beats (frames from `start`) in the section we use. Decodes 1 s of lead-in
    so a beat sitting exactly on `start` is still found."""
    lead = min(1.0, start)
    y = decode(path, start - lead, seconds + lead)
    bpm, _, _, times, onset = track_beats(y)
    frames = sorted({round((t - lead) * FPS) for t in times if t - lead >= -0.05})
    return [max(0, f) for f in frames], bpm, onset


def accents_from(beats: list[int], onset: np.ndarray, pin: int | None, lead: float) -> list[int]:
    """Every 4th beat, on the phase where the music hits hardest (or the drop)."""
    if not beats:
        return []
    strength = [float(onset[min(len(onset) - 1, int((b / FPS + lead) * AFPS))]) for b in beats]
    if pin is not None and pin in beats:
        phase = beats.index(pin) % 4
    else:
        phase = int(np.argmax([sum(strength[i::4]) for i in range(4)]))
    return beats[phase::4]


def snap(beats: list[int], target: int, after: int) -> int:
    c = [b for b in beats if b > after]
    return min(c, key=lambda b: abs(b - target)) if c else target


def plan_showcase(hero: dict, track: dict, a: dict, week_no: int) -> dict:
    path = MUSIC_DIR / track["file"]
    hook_s = 3.0
    start = a["drop"] - hook_s if a["drop"] and a["drop"] >= hook_s else a["first_loud"]
    beats, bpm, onset = beat_grid(path, start)
    reveal_at = snap(beats, round(hook_s * FPS), 45) if beats else 90
    accents = accents_from(beats, onset, reveal_at, min(1.0, start))
    hook = SHOWCASE_HOOKS[week_no % len(SHOWCASE_HOOKS)]
    first_sentence = re.split(r"(?<=[.!?])\s+", hero["desc"].strip())[0]
    if len(first_sentence) > 78:
        first_sentence = first_sentence[:75].rsplit(" ", 1)[0] + "…"
    steps = [
        ("reveal", 4.6, [hero["name"], f"{hero['tag']} · Handmade"], {"direction": "right"}),
        ("detail", 2.8, ["Close-up", "Every stitch by hand"], {"focus": 0, "direction": "up"}),
        ("detail", 2.8, ["Made to order", "Crafted just for you"], {"focus": 1, "direction": "left"}),
        ("features", 3.6, ["Handmade by Mayuri", "Made to order in India", first_sentence], {}),
        ("brand", 5.0, [TAGLINE, "Handmade crochet · made to order"], {}),
        ("cta", 5.6, ["Find Your Handmade Favourite!", "Explore the Collection | Shop Now", EMAIL], {}),
    ]
    scenes = [{"kind": "hook", "from": 0, "duration": reveal_at, "text": list(hook), "product": 0}]
    cursor = reveal_at
    for kind, secs, text, extra in steps:
        target = cursor + round(secs * FPS)
        end = target if kind == "cta" else snap(beats, target, cursor + round(secs * FPS * 0.6))
        end = min(end, MAX_FRAMES)
        scenes.append({"kind": kind, "from": cursor, "duration": end - cursor, "text": text, "product": 0, **extra})
        cursor = end
    return finish_plan("showcase", scenes, [hero], beats, accents, track, start, bpm,
                       cover={"title": hero["name"], "kicker": "Handmade with love", "product": 0})


def plan_creative(items: list[dict], track: dict, a: dict, week_no: int) -> dict:
    path = MUSIC_DIR / track["file"]
    beats0, _, _ = beat_grid(path, a["first_loud"], 8)
    start = a["first_loud"] + (beats0[0] / FPS if beats0 else 0)  # music starts exactly on a beat
    beats, bpm, onset = beat_grid(path, start)
    if not beats or beats[0] > 3:
        beats = [0] + beats
    accents = accents_from(beats, onset, None, min(1.0, start))
    period = (beats[-1] - beats[0]) / max(1, len(beats) - 1) if len(beats) > 1 else 17
    per_product = 3 if period < 19 else 2
    hook = CREATIVE_HOOKS[week_no % len(CREATIVE_HOOKS)]

    def at(i: int) -> int:
        return beats[i] if i < len(beats) else round(beats[-1] + (i - len(beats) + 1) * period)

    def total_for(n: int) -> int:
        return at(4 + n * per_product + 6 + 5) + round(8 * period) + 12

    n = len(items)
    while n > 3 and total_for(n) > MAX_FRAMES:
        n -= 1
    items = items[:n]
    scenes = [{"kind": "hook", "from": 0, "duration": at(4), "text": hook, "product": 0}]
    b = 4
    dirs = ["right", "left", "up", "down", "left", "right"]
    for i, p in enumerate(items):
        scenes.append({"kind": "flash", "from": at(b), "duration": at(b + per_product) - at(b),
                       "text": [p["name"]], "product": i, "direction": dirs[i % len(dirs)]})
        b += per_product
    scenes.append({"kind": "collage", "from": at(b), "duration": at(b + 6) - at(b),
                   "text": ["Gift something", "made by hand"]})
    b += 6
    scenes.append({"kind": "brand", "from": at(b), "duration": at(b + 5) - at(b),
                   "text": [TAGLINE, BRAND_FULL]})
    b += 5
    end = min(at(b) + round(8 * period) + 12, MAX_FRAMES)
    scenes.append({"kind": "cta", "from": at(b), "duration": end - at(b),
                   "text": ["Find Your Handmade Favourite!", "Explore the Collection | Shop Now", EMAIL]})
    return finish_plan("creative", scenes, items, beats, accents, track, start, bpm,
                       cover={"title": "Handmade Gift Edit", "kicker": "little treasures, made by hand", "product": 0})


def finish_plan(variant, scenes, products, beats, accents, track, start, bpm, cover) -> dict:
    total = scenes[-1]["from"] + scenes[-1]["duration"]
    overrides = json.loads(FOCUS_OVERRIDES.read_text(encoding="utf-8")) if FOCUS_OVERRIDES.exists() else {}
    staged = [{"id": p["id"], "name": p["name"], "tag": p["tag"], "desc": p["desc"],
               "image": stage_image(p), "focus": overrides.get(p["id"]) or focus_points(REPO / p["image"])}
              for p in products]
    music_src = f"music/{track['id']}.mp3"
    (PUBLIC / "music").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(MUSIC_DIR / track["file"], PUBLIC / music_src)
    return {
        "variant": variant, "durationInFrames": total, "website": WEBSITE, "email": EMAIL,
        "products": staged, "scenes": scenes,
        "beats": [b for b in beats if b < total], "accents": [b for b in accents if b < total],
        "music": {"src": music_src, "trimBefore": round(start * FPS), "volume": 0.9},
        "cover": cover,
        "_meta": {"track": track, "start_s": round(start, 2), "bpm": round(bpm, 1)},
    }


# ------------------------------------------------------------------ render + export
def npx(*args: str) -> None:
    cmd = ["npx.cmd" if os.name == "nt" else "npx", "remotion", *args]
    r = subprocess.run(cmd, cwd=VIDEO)
    if r.returncode:
        raise SystemExit(f"remotion {' '.join(args[:2])} failed ({r.returncode})")


def render(comp: str, out: Path, props_path: Path) -> None:
    raw = VIDEO / "out" / "weekly" / f"{out.stem}-raw.mp4"
    raw.parent.mkdir(parents=True, exist_ok=True)
    npx("render", "src/index.ts", comp, str(raw), f"--props={props_path}", "--codec=h264",
        "--crf=14", "--audio-codec=aac", "--audio-bitrate=320k", "--concurrency=2", "--log=error")
    # Social-ready: H.264 High, yuv420p, faststart; loudness to -14 LUFS (Reels/Shorts norm).
    subprocess.run([str(FFMPEG), "-y", "-v", "error", "-i", str(raw),
                    "-vf", "scale=in_range=pc:out_range=tv", "-color_range", "tv",
                    "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-profile:v", "high",
                    "-pix_fmt", "yuv420p", "-r", "30", "-movflags", "+faststart",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    str(out)], check=True)


def still(comp: str, props_path: Path, out_jpg: Path) -> None:
    png = VIDEO / "out" / "weekly" / f"{out_jpg.stem}.png"
    npx("still", "src/index.ts", comp, str(png), f"--props={props_path}", "--log=error")
    Image.open(png).convert("RGB").save(out_jpg, quality=92)


def music_cut(plan: dict, out: Path) -> None:
    m = plan["_meta"]
    subprocess.run([str(FFMPEG), "-y", "-v", "error", "-ss", str(m["start_s"]),
                    "-t", f"{plan['durationInFrames'] / FPS:.2f}", "-i", str(MUSIC_DIR / m["track"]["file"]),
                    "-c:a", "libmp3lame", "-b:a", "256k", str(out)], check=True)


def probe(path: Path) -> dict:
    err = subprocess.run([str(FFMPEG), "-hide_banner", "-i", str(path)], capture_output=True,
                         text=True, encoding="utf-8", errors="replace").stderr
    v = re.search(r"Video: (\w+).*?, (\d{3,4})x(\d{3,4})", err)
    a = re.search(r"Audio: (\w+)", err)
    d = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    return {"codec": v.group(1) if v else None, "w": int(v.group(2)) if v else 0, "h": int(v.group(3)) if v else 0,
            "audio": a.group(1) if a else None,
            "seconds": int(d.group(2)) * 60 + float(d.group(3)) if d else 0,
            "mb": round(path.stat().st_size / 1e6, 1)}


def qc(plan: dict, mp4: Path) -> list[str]:
    info = probe(mp4)
    all_text = " ".join(" ".join(s["text"]) for s in plan["scenes"]) + " " + json.dumps(plan["cover"])
    checks = [
        (info["codec"] == "h264", f"H.264 video ({info['codec']})"),
        ((info["w"], info["h"]) == (1080, 1920), f"1080×1920 vertical ({info['w']}×{info['h']})"),
        (info["audio"] == "aac", f"AAC audio, loudness-normalised ({info['audio']})"),
        (15 <= info["seconds"] <= 30.5, f"15–30 s long ({info['seconds']:.1f} s)"),
        (info["mb"] <= 60, f"file size OK for Reels/Shorts ({info['mb']} MB)"),
        (all(s["duration"] > 0 for s in plan["scenes"]), "every scene has length"),
        (not re.search(r"mayuriz(?!')|mayuris yarn", all_text, re.I), "brand spelled Mayuri's Yarn Tales / Mayuri'z"),
        (plan["website"] == WEBSITE, f"website {WEBSITE} on screen"),
        (not re.search(r"₹|rs\.?\s?\d|price|gst|in stock|cotton|wool|acrylic|\d+\s?cm", all_text, re.I),
         "no prices/materials/sizes/stock claimed"),
    ]
    return [("PASS  " if ok else "FAIL  ") + label for ok, label in checks]


# ------------------------------------------------------------------ content pack
def scene_notes(s: dict, plan: dict) -> tuple[str, str]:
    p = plan["products"][s.get("product", 0)]["name"] if plan["products"] else ""
    v, k = plan["variant"], s["kind"]
    visual = {
        ("showcase", "hook"): f"Blurred macro of the {p} stitches behind the hook line; zoom creeps, then speed-ramps into a white flash.",
        ("showcase", "reveal"): f"On the drop: {p} photo card whips in from the {s.get('direction')} with motion blur, lands, a light sheen sweeps across; name rises word by word.",
        ("showcase", "detail"): f"Full-screen close-up on the piece (focus point {s.get('focus', 0) + 1}), slides in from the {'bottom' if s.get('direction') == 'up' else s.get('direction')}, slow push-in, punch on the strong beat.",
        ("showcase", "features"): "Photo card up top; three lines slide in from the left, one per beat, with round icons.",
        ("showcase", "brand"): "Full Mayuri's Yarn Tales logo wipes on, tagline rises in italic serif, a thread line draws itself.",
        ("showcase", "cta"): "Round product badge, headline, red website pill that pulses on every beat, short logo.",
        ("creative", "hook"): "One bold word-line per beat, background colour flips on each hit; a product polaroid slides up in the corner.",
        ("creative", "flash"): f"{p}: polaroid whips in from the {s.get('direction')} (motion blur), settles with a tilt, kicks on the beat; giant outlined category word drifts behind.",
        ("creative", "collage"): "All pieces pop into a 2×3 grid every half-beat; red ribbon banner slams across.",
        ("creative", "brand"): "Short Mayuri'z logo springs in, yarn-colour dots orbit and pulse, tagline rises.",
        ("creative", "cta"): "Red screen: words slam in on the beats, white website pill kicks, product strip scrolls.",
    }.get((v, k), "")
    transition = {
        "hook": "white flash cut on the drop" if v == "showcase" else "hard cut on the beat",
        "reveal": "lift-and-blur exit into the close-up", "detail": "whip slide on the beat",
        "features": "fade-through on the beat", "brand": "soft fade", "cta": "music fades out over the last 1.2 s",
        "flash": "whip out the opposite side (speed ramp)", "collage": "cut on the beat",
    }.get(k, "")
    return visual, transition


def fmt(f: int) -> str:
    return f"{f / FPS:.1f}s"


def storyboard(plan: dict) -> str:
    rows = ["| # | Time | Scene | On-screen text | Visual & animation | Transition out |",
            "|---|---|---|---|---|---|"]
    for i, s in enumerate(plan["scenes"], 1):
        vis, tr = scene_notes(s, plan)
        text = " / ".join(s["text"]).replace("|", "\\|")
        rows.append(f"| {i} | {fmt(s['from'])}–{fmt(s['from'] + s['duration'])} | {s['kind']} | {text} | {vis} | {tr} |")
    return "\n".join(rows)


def beat_plan(plan: dict) -> str:
    m = plan["_meta"]
    beats, acc = plan["beats"], plan["accents"]
    lines = [f"- Track: **{m['track']['title']}** by {m['track']['artist']} ({m['track']['licence']}), "
             f"used from {m['start_s']:.2f} s, ~{m['bpm']:.0f} BPM, {len(beats)} beats in the cut.",
             f"- Every scene starts on a detected beat; strong beats (every 4th, on the hardest-hitting phase) at "
             f"{', '.join(fmt(a) for a in acc[:8])}{'…' if len(acc) > 8 else ''}."]
    if plan["variant"] == "showcase":
        rev = next(s for s in plan["scenes"] if s["kind"] == "reveal")
        lines.append(f"- The product reveal at {fmt(rev['from'])} lands on the track's drop (full band entry).")
    lines.append("- Website pill, stickers and cards 'kick' (small scale/shadow pulse) on beats; close-ups punch in on strong beats.")
    return "\n".join(lines)


def product_link(p: dict) -> str:
    return f"{SITE}?order={p['id']}#order"


def captions(plan: dict, hero: dict | None) -> dict:
    credit = plan["_meta"]["track"]["credit"]
    if plan["variant"] == "showcase" and hero:
        p = hero
        desc = p["desc"].strip()
        tags = TAG_HASHTAGS.get(p["tag"], "#crochetlove #giftideas")
        return {
            "title": f"{p['name']} | Handmade Crochet",
            "ig": (f"{p['name']} 🧶\n\n{desc}\n\nEvery piece is crocheted by hand by Mayuri and made to order, "
                   f"just for you.\n\nFind your handmade favourite: {WEBSITE}\n📩 {EMAIL}\n\n{credit}\n\n"
                   f"#crochet #handmadeinindia #mayuriz {tags}"),
            "fb": (f"{p['name']} 🧶\n\n{desc}\n\nCrocheted by hand by Mayuri, made to order in India.\n"
                   f"Order this piece: {product_link(p)}\n📩 {EMAIL}\n\n{credit}"),
            "yt_title": f"{p['name']} 🧶 Handmade Crochet | {BRAND_FULL} #shorts",
            "yt_desc": (f"{desc} Crocheted by hand by Mayuri, made to order in India.\n\n"
                        f"Order: {product_link(p)}\nShop: {SITE}\n\n{TAGLINE}\n\n{credit}\n\n#crochet #handmade #shorts"),
            "cta": f"Order the {p['name']} → {product_link(p)}",
            "link": product_link(p),
        }
    names = [p["name"] for p in plan["products"]]
    listing = "\n".join(f"• {n}" for n in names)
    return {
        "title": "Handmade Gift Edit",
        "ig": (f"Little gifts, made by hand 🎁🧶\n\nThis week's picks:\n{listing}\n\nEach one is crocheted by "
               f"Mayuri and made to order, so it's made just for the person you're thinking of.\n\n"
               f"Find your handmade favourite: {WEBSITE}\n📩 {EMAIL}\n\n{credit}\n\n"
               f"#crochet #handmadegifts #giftideas #handmadeinindia #mayuriz"),
        "fb": (f"Little gifts, made by hand 🎁🧶\n\nThis week's picks:\n{listing}\n\nCrocheted by Mayuri, made "
               f"to order in India.\nSee them all: {SITE}\n📩 {EMAIL}\n\n{credit}"),
        "yt_title": f"Handmade Crochet Gift Ideas 🎁 | {BRAND_FULL} #shorts",
        "yt_desc": (f"{', '.join(names)}: crocheted by hand by Mayuri, made to order in India.\n\n"
                    f"Shop: {SITE}\n\n{TAGLINE}\n\n{credit}\n\n#crochet #giftideas #shorts"),
        "cta": f"Explore the collection → {SITE}",
        "link": SITE,
    }


def alt_hooks(variant: str, week_no: int) -> list[str]:
    bank = SHOWCASE_HOOKS if variant == "showcase" else CREATIVE_HOOKS
    used = week_no % len(bank)
    return [" ".join(h) for i, h in enumerate(bank) if i != used][:3]


def schedule(week: str) -> tuple[dt.datetime, dt.datetime]:
    y, n = week.split("-W")
    wed = dt.date.fromisocalendar(int(y), int(n), 3)
    sat = dt.date.fromisocalendar(int(y), int(n), 6)
    return (dt.datetime.combine(wed, dt.time(18, 30), IST), dt.datetime.combine(sat, dt.time(11, 0), IST))


def content_pack(week: str, week_no: int, plans: list[dict], hero: dict, files: dict, qcs: list[list[str]]) -> str:
    when = schedule(week)
    out = [f"# Mayuri'z weekly videos: {week}\n",
           f"Brand: **{BRAND_FULL}** (short mark **Mayuri'z**) · Tagline: *{TAGLINE}* · Website: **{WEBSITE}**\n",
           "## Weekly summary and publishing schedule\n",
           "| Video | Featuring | Publish (IST) | Length | Music |", "|---|---|---|---|---|"]
    for i, (pl, t) in enumerate(zip(plans, when), 1):
        out.append(f"| {i}. {'Product ad (craftsmanship)' if i == 1 else 'Creative ad (gifting)'} | "
                   f"{hero['name'] if i == 1 else ', '.join(p['name'] for p in pl['products'])} | "
                   f"{t.strftime('%a %d %b, %H:%M')} | {pl['durationInFrames'] / FPS:.1f} s | {pl['_meta']['track']['title']} |")
    out.append("\nWhy these times: there isn't enough Instagram/Facebook history yet for real audience analytics "
               "(the accounts started posting on 14 Nov 2026), so these are standard midweek-evening and "
               "weekend-morning slots for an India audience, kept clear of the daily 13:00 and 20:00 posts. "
               "Re-check against Insights after about 4 weeks.\n")
    out.append("Music licence: both tracks are by Kevin MacLeod, CC BY 4.0. Commercial use is allowed **with the "
               "credit line**, which is already inside every caption below; keep it when posting.\n")
    for i, pl in enumerate(plans, 1):
        c = captions(pl, hero if i == 1 else None)
        f = files.get(i, {})
        out += [f"\n---\n\n## VIDEO 0{i}: {'Product Advertisement' if i == 1 else 'Creative Product Advertisement'}\n",
                f"**1. Title:** {c['title']}\n",
                "**2. Alternative opening hooks:**\n" + "\n".join(f"- {h}" for h in alt_hooks(pl['variant'], week_no)) + "\n",
                "**3, 4, 7. Storyboard, on-screen text, transitions and animation:**\n", storyboard(pl) + "\n",
                f"**5. Selected MP3:** `{pl['_meta']['track']['file']}` (exact cut used: `{f.get('music', '')}`)\n",
                "**6. Music and beat sync plan:**\n" + beat_plan(pl) + "\n",
                "**8. Instagram caption:**\n```\n" + c["ig"] + "\n```\n",
                "**9. Facebook caption:**\n```\n" + c["fb"] + "\n```\n",
                f"**10. YouTube Shorts title:** {c['yt_title']}\n\n**YouTube Shorts description:**\n```\n{c['yt_desc']}\n```\n",
                "**11. Hashtags:** " + " ".join(w for w in c["ig"].split() if w.startswith("#")) + "\n",
                f"**12. Product-page link:** {c['link']}\n",
                f"**13. Shopping CTA:** {c['cta']}\n",
                f"**14. Cover image text:** {pl['cover']['kicker']} / **{pl['cover']['title']}** (`{f.get('cover', '')}`)\n",
                f"**Video file:** `{f.get('mp4', '(not rendered)')}`\n",
                "**Quality control:**\n" + "\n".join(f"- {q}" for q in qcs[i - 1]) + "\n"]
        prods = pl["products"] if i == 2 else [pl["products"][0]]
        out.append("**Product information used (from the website list; nothing else is claimed):**\n" +
                   "\n".join(f"- {p['name']} ({p['tag']}): {p['desc']} → {product_link(p)}" for p in prods) + "\n")
    out.append("\n_Not shown because the website doesn't list them yet: prices, materials/yarn, sizes, stock. "
               "Add them to the product list and the videos can include them._\n")
    return "\n".join(out)


# ------------------------------------------------------------------ main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", help="ISO week like 2026-W47 (default: the week of tomorrow)")
    ap.add_argument("--hero")
    ap.add_argument("--products", help="comma-separated ids for video 2")
    ap.add_argument("--plan-only", action="store_true")
    ap.add_argument("--no-state", action="store_true", help="don't mark products/music as used")
    args = ap.parse_args()

    tomorrow = dt.datetime.now(IST).date() + dt.timedelta(days=1)
    iso = tomorrow.isocalendar()
    week = args.week or f"{iso[0]}-W{iso[1]:02d}"
    week_no = int(week.split("-W")[1])
    out_dir = OUT_ROOT / week
    out_dir.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {"featured": {}, "music": {}}
    cache_path = STATE_DIR / "music_cache.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}

    (PUBLIC / "brand").mkdir(parents=True, exist_ok=True)
    for f in (REPO / "media" / "brand").glob("logo-*.svg"):
        shutil.copyfile(f, PUBLIC / "brand" / f.name)

    make_grain()
    items = load_products()
    hero, montage = pick_products(items, state, args.hero, args.products.split(",") if args.products else None)
    log(f"week {week}: hero = {hero['name']}; montage = {', '.join(p['name'] for p in montage)}")

    log("music:")
    t1, a1 = pick_music("showcase", state, week, set(), cache)
    t2, a2 = pick_music("creative", state, week, {t1["id"]}, cache)
    cache_path.write_text(json.dumps(cache, indent=1), encoding="utf-8")
    log(f"  -> video 1: {t1['title']}   video 2: {t2['title']}")

    plans = [plan_showcase(hero, t1, a1, week_no), plan_creative(montage, t2, a2, week_no)]
    files, qcs = {}, []
    for i, (pl, comp) in enumerate(zip(plans, ["AdShowcase", "AdCreative"]), 1):
        slug = "product-ad" if i == 1 else "creative-ad"
        props = VIDEO / "out" / "weekly" / f"{week}-v{i}.json"
        props.parent.mkdir(parents=True, exist_ok=True)
        props.write_text(json.dumps(pl, indent=1, ensure_ascii=False), encoding="utf-8")
        (out_dir / f"video-{i}-plan.json").write_text(json.dumps(pl, indent=1, ensure_ascii=False), encoding="utf-8")
        mp4, cover, music = (out_dir / f"video-{i}-{slug}.mp4", out_dir / f"video-{i}-cover.jpg",
                             out_dir / f"video-{i}-music.mp3")
        files[i] = {"mp4": mp4.name, "cover": cover.name, "music": music.name}
        music_cut(pl, music)
        log(f"video {i}: {len(pl['scenes'])} scenes, {pl['durationInFrames'] / FPS:.1f} s, "
            f"music from {pl['_meta']['start_s']} s @ {pl['_meta']['bpm']} BPM")
        if args.plan_only:
            qcs.append(["(not rendered: --plan-only)"])
            continue
        log(f"rendering video {i}…")
        render(comp, mp4, props)
        still("AdCover", props, cover)
        qcs.append(qc(pl, mp4))
        log("\n".join("  " + q for q in qcs[-1]))

    (out_dir / "content.md").write_text(content_pack(week, week_no, plans, hero, files, qcs), encoding="utf-8")
    if not args.plan_only and not args.no_state and all(q.startswith("PASS") for qq in qcs for q in qq):
        for p in [hero, *plans[1]["products"]]:
            state["featured"][p["id"]] = week
        state["music"][t1["id"]] = week
        state["music"][t2["id"]] = week
        STATE.write_text(json.dumps(state, indent=1), encoding="utf-8")
    log(f"done: {out_dir}")
    if not args.plan_only:
        ok = all(q.startswith("PASS") for qq in qcs for q in qq)
        wed, sat = schedule(week)
        note = (f"🎬 {week} promo videos {'are ready' if ok else 'need a look (a check failed)'}.\n"
                f"1. {hero['name']} (post {wed.strftime('%a %H:%M')})\n"
                f"2. Gift edit, {len(plans[1]['products'])} pieces (post {sat.strftime('%a %H:%M')})\n"
                f"Videos, covers and captions are on the PC: Videos\\Mayuriz Weekly\\{week}")
        try:
            sys.path.insert(0, str(REPO / "tools"))
            import social_daily  # noqa: E402  (shared Telegram helper)
            social_daily.telegram(note)
        except Exception as exc:  # a failed note must never fail the render
            log(f"telegram note skipped: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
