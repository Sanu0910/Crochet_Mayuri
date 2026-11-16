"""Mayuri'z daily reel: one short animated product showcase, posted every day.

  <venv>\\python.exe -X utf8 tools\\daily_reel.py               # make today's reel, post it at 18:00 IST
  ... --at 19:30          post time today (HH:MM IST)
  ... --hero <id>         pick the piece yourself
  ... --no-post           render only (review first)

One piece a day, newest first, each piece once before any repeats; never the
same category two days running. The reel is a ~16 s 9:16 cut of the weekly
"Showcase" ad (video/src/ads/Showcase.tsx): a punchy hook over a blurred
close-up ("Handmade. Limited pieces."), the photo card whipping in on the
music's drop, a macro close-up, the scarcity line, then the call to action.
Music is a licence-approved "showcase" track from tools/video_music.json,
never the same track two days running; its CC BY credit goes in the caption.

Selling words are kept true: every piece is crocheted by hand, so only a few
get made. No stock counts, prices or materials are claimed (the site doesn't
list them; weekly_video.qc() blocks them).

It reuses tools/weekly_video.py (beats, staging, render, QC) and posts with
tools/post_video.py (Instagram Graph API + Facebook via WoopSocial), which
tells the team on Telegram. Nothing is posted if a quality check fails.

Output: %USERPROFILE%\\Videos\\Mayuriz Weekly\\daily\\<date>\\
State:  %LOCALAPPDATA%\\MayurizVideo\\daily_state.json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import weekly_video as w  # noqa: E402

DAILY_STATE = w.STATE_DIR / "daily_state.json"
OUT = w.OUT_ROOT / "daily"
DEFAULT_AT = "18:00"   # clear of the 13:00 / 20:00 poster posts

# Hook (2 lines, before the reveal) and the scarcity close-up line, rotated daily.
HOOKS = [
    ("Handmade.", "Limited pieces."),
    ("Only a few", "made by hand."),
    ("Not mass-made.", "Hand-made."),
    ("Small batch.", "Big love."),
    ("One hook.", "One pair of hands."),
    ("Made to last.", "Made by hand."),
]
DETAIL_LINES = [
    ("Limited pieces", "Every stitch by hand"),
    ("Small batch", "Only a few made each time"),
    ("Made to last", "A keepsake, not a trend"),
    ("Truly handmade", "No two exactly alike"),
]
CAPTION_PUNCH = [
    "Each piece takes hours by hand, so only a few get made. Order yours early.",
    "Not mass-produced: crocheted by hand, one at a time, in limited pieces.",
    "Made to last, made by hand. A little keepsake worth keeping.",
    "Every stitch by hand means limited pieces. Order yours early.",
]


def load_state() -> dict:
    if DAILY_STATE.exists():
        return json.loads(DAILY_STATE.read_text(encoding="utf-8"))
    return {"reeled": {}, "music": {}, "last_tag": ""}


def pick_hero(items: list[dict], state: dict, hero_id: str | None) -> dict:
    if hero_id:
        return next(p for p in items if p["id"] == hero_id)
    ok = [p for p in items if not p["name"].lower().startswith("new piece") and "-NEW-" not in p["sku"]]
    fresh = [p for p in ok if p["id"] not in state["reeled"]]
    # every piece done once: start again with the pieces shown longest ago
    pool = fresh or sorted(ok, key=lambda p: state["reeled"].get(p["id"], ""))
    return next((p for p in pool if p["tag"] != state.get("last_tag")), pool[0])


def pick_track(state: dict, today: str, cache: dict) -> tuple[dict, dict]:
    cfg = json.loads((w.REPO / "tools" / "video_music.json").read_text(encoding="utf-8"))
    last = max(state["music"].items(), key=lambda kv: kv[1], default=(None, ""))[0]
    best = None
    for t in cfg["approved"]:
        path = w.MUSIC_DIR / t["file"]
        if "showcase" not in t["styles"] or not path.exists():
            continue
        a = w.analyse_track(path, cache)
        days_ago = ((dt.date.fromisoformat(today) - dt.date.fromisoformat(state["music"][t["id"]])).days
                    if t["id"] in state["music"] else 99)
        # good fit, but prefer tracks not heard lately; never yesterday's
        s = w.style_score("showcase", a) + min(days_ago, 7) * 0.4 - (10 if t["id"] == last else 0)
        if best is None or s > best[0]:
            best = (s, t, a)
    if not best:
        raise SystemExit(f"no approved showcase track found in {w.MUSIC_DIR}")
    return best[1], best[2]


def plan_daily(hero: dict, track: dict, a: dict, day_no: int) -> dict:
    path = w.MUSIC_DIR / track["file"]
    hook_s = 2.6
    start = a["drop"] - hook_s if a["drop"] and a["drop"] >= hook_s else a["first_loud"]
    beats, bpm, onset = w.beat_grid(path, start, 24)
    reveal_at = w.snap(beats, round(hook_s * w.FPS), 45) if beats else 78
    accents = w.accents_from(beats, onset, reveal_at, min(1.0, start))
    hook = HOOKS[day_no % len(HOOKS)]
    detail = DETAIL_LINES[day_no % len(DETAIL_LINES)]
    steps = [
        ("reveal", 4.2, [hero["name"], f"{hero['tag']} · Handmade"], {"direction": ["right", "left"][day_no % 2]}),
        ("detail", 2.6, list(detail), {"focus": 0, "direction": "up"}),
        ("brand", 2.8, [w.TAGLINE, "Handmade · limited pieces"], {}),
        ("cta", 4.4, ["Limited Pieces. Order Yours!", "Made to order on our website", w.EMAIL], {}),
    ]
    scenes = [{"kind": "hook", "from": 0, "duration": reveal_at, "text": list(hook), "product": 0}]
    cursor = reveal_at
    for kind, secs, text, extra in steps:
        target = cursor + round(secs * w.FPS)
        if kind == "cta":
            end = max(target, 15 * w.FPS + 6)   # Reels / QC floor: 15 s
        else:
            end = w.snap(beats, target, cursor + round(secs * w.FPS * 0.6))
        scenes.append({"kind": kind, "from": cursor, "duration": end - cursor, "text": text, "product": 0, **extra})
        cursor = end
    return w.finish_plan("showcase", scenes, [hero], beats, accents, track, start, bpm,
                         cover={"title": hero["name"], "kicker": "Handmade · limited pieces", "product": 0})


def daily_captions(plan: dict, hero: dict, day_no: int) -> tuple[str, str]:
    c = w.captions(plan, hero)
    punch = CAPTION_PUNCH[day_no % len(CAPTION_PUNCH)]
    ig = c["ig"].replace("\n\nFind your handmade favourite:", f"\n\n✨ {punch}\n\nFind your handmade favourite:", 1)
    # brand sheet: max 5 hashtags -> crochet, handmade, brand, scarcity, product type
    body, _, tags = ig.rpartition("\n\n")
    tag1 = w.TAG_HASHTAGS.get(hero["tag"], "#giftideas").split()[0]
    ig = f"{body}\n\n#crochet #handmadeinindia #mayuriz #limitededition {tag1}"
    return ig, c["fb"].replace("\nOrder this piece:", f"\n✨ {punch}\nOrder this piece:", 1)


def post_time(at: str, now: dt.datetime) -> dt.datetime | None:
    """Today at `at` IST; None (= post now) if that's less than 3 minutes away or past."""
    hh, mm = map(int, at.split(":"))
    when = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    return when if when > now + dt.timedelta(minutes=3) else None


def note(text: str) -> None:
    try:
        import social_daily
        social_daily.telegram(text)
    except Exception as exc:  # a failed note must never hide the result
        w.log(f"telegram note skipped: {exc}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hero")
    ap.add_argument("--at", default=DEFAULT_AT, help="post time today, HH:MM IST")
    ap.add_argument("--no-post", action="store_true")
    args = ap.parse_args()

    now = dt.datetime.now(w.IST)
    today = now.date().isoformat()
    state = load_state()
    if not args.hero and not args.no_post and state.get("last_day") == today:
        w.log(f"already posted a reel today ({today}); nothing to do")
        return 0
    out_dir = OUT / today
    out_dir.mkdir(parents=True, exist_ok=True)
    w.STATE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = w.STATE_DIR / "music_cache.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}

    (w.PUBLIC / "brand").mkdir(parents=True, exist_ok=True)
    for f in (w.REPO / "media" / "brand").glob("logo-*.svg"):
        (w.PUBLIC / "brand" / f.name).write_bytes(f.read_bytes())
    w.make_grain()

    hero = pick_hero(w.load_products(), state, args.hero)
    track, a = pick_track(state, today, cache)
    cache_path.write_text(json.dumps(cache, indent=1), encoding="utf-8")
    day_no = now.date().toordinal()
    plan = plan_daily(hero, track, a, day_no)
    w.log(f"{today}: {hero['name']} with {track['title']}, {plan['durationInFrames'] / w.FPS:.1f} s")

    props = w.VIDEO / "out" / "weekly" / f"daily-{today}.json"
    props.parent.mkdir(parents=True, exist_ok=True)
    props.write_text(json.dumps(plan, indent=1, ensure_ascii=False), encoding="utf-8")
    slug = re.sub(r"[^a-z0-9]+", "-", hero["name"].lower()).strip("-")
    mp4, cover = out_dir / f"reel-{slug}.mp4", out_dir / f"reel-{slug}-cover.jpg"
    w.render("AdShowcase", mp4, props)
    w.still("AdCover", props, cover)
    checks = w.qc(plan, mp4)
    w.log("\n".join("  " + c for c in checks))

    ig, fb = daily_captions(plan, hero, day_no)
    (out_dir / "instagram.txt").write_text(ig, encoding="utf-8")
    (out_dir / "facebook.txt").write_text(fb, encoding="utf-8")
    if not all(x.startswith("PASS") for x in checks):
        w.log("a check failed: not posting")
        note(f"🎬 Today's reel ({hero['name']}) failed a check and was not posted. "
             f"Files: Videos\\Mayuriz Weekly\\daily\\{today}")
        return 1
    if args.no_post:
        w.log(f"rendered, not posted: {mp4}")
        return 0

    when = post_time(args.at, dt.datetime.now(w.IST))
    cmd = [sys.executable, "-X", "utf8", str(w.REPO / "tools" / "post_video.py"), str(mp4),
           "--ig", str(out_dir / "instagram.txt"), "--fb", str(out_dir / "facebook.txt")]
    if when:
        cmd += ["--at", when.isoformat()]
    r = subprocess.run(cmd)
    if r.returncode:
        w.log(f"posting failed ({r.returncode})")
        note(f"🎬 Today's reel ({hero['name']}) could not be posted. See %LOCALAPPDATA%\\MayurizVideo\\daily.log")
        return r.returncode
    state["reeled"][hero["id"]] = today
    state["music"][track["id"]] = today
    state["last_tag"], state["last_day"] = hero["tag"], today
    DAILY_STATE.write_text(json.dumps(state, indent=1), encoding="utf-8")
    w.log(f"posted: {hero['name']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
