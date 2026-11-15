"""Post one video as a Reel to Instagram + Facebook, now or at a set time.

  py tools/post_video.py VIDEO --ig ig.txt --fb fb.txt [--at 2026-11-15T17:00+05:30] [--dry-run]

1. Re-encodes to Reels spec (H.264/AAC, max 1080 wide, 30 fps, faststart).
2. Uploads once to WoopSocial; its public CDN link is what Instagram fetches.
3. Facebook: a WoopSocial REEL post, scheduled by WoopSocial itself for --at.
4. Instagram (Graph API): the Reel container is created right away (Instagram
   needs a few minutes to process video), then this script waits and publishes
   at --at. Keep it running until then (start it in the background).
Then tells the team on Telegram. Keys: same .mayuriz env files as social_daily.py.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import social_daily as s  # noqa: E402  (Woop client, http helpers, env files, telegram)


def find_ffmpeg() -> str:
    """Full ffmpeg build: PATH first, then the winget install."""
    if shutil.which("ffmpeg"):
        return shutil.which("ffmpeg")
    winget = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Packages"
    found = sorted(winget.glob("Gyan.FFmpeg*/ffmpeg-*/bin/ffmpeg.exe")) if winget.exists() else []
    if not found:
        raise SystemExit("ffmpeg not found: winget install Gyan.FFmpeg")
    return str(found[-1])


def to_reel(src: Path, out: Path) -> None:
    subprocess.run([find_ffmpeg(), "-y", "-v", "error", "-i", str(src),
                    "-vf", "scale='min(1080,iw)':-2,fps=30", "-c:v", "libx264", "-preset", "slow",
                    "-crf", "20", "-profile:v", "high", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                    "-c:a", "aac", "-b:a", "160k", "-ar", "48000", str(out)], check=True)


def graph(path: str, params: dict, token: str) -> dict:
    raw, _ = s.post_json(s.GRAPH + path, {**params, "access_token": token})
    return json.loads(raw)


def graph_get(obj: str, fields: str, token: str) -> dict:
    raw, _ = s.http(f"{s.GRAPH}{obj}?fields={fields}&access_token={urllib.parse.quote(token)}")
    return json.loads(raw)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video", type=Path)
    ap.add_argument("--ig", type=Path, required=True, help="Instagram caption file (UTF-8)")
    ap.add_argument("--fb", type=Path, required=True, help="Facebook caption file (UTF-8)")
    ap.add_argument("--at", help="publish time, ISO 8601 with offset; default now")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    ig_text = args.ig.read_text(encoding="utf-8").strip()
    fb_text = args.fb.read_text(encoding="utf-8").strip()
    when = dt.datetime.fromisoformat(args.at) if args.at else None
    if when and when <= dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=2):
        raise SystemExit("--at must be at least 2 minutes in the future")

    reel = s.STATE_DIR / "reels" / f"{args.video.stem}-reel.mp4"
    reel.parent.mkdir(parents=True, exist_ok=True)
    to_reel(args.video, reel)
    s.log(f"reel ready: {reel} ({reel.stat().st_size // 1024} KB)")
    if args.dry_run:
        print(ig_text, "\n-----\n", fb_text)
        return 0

    woop = s.Woop(s.env_file("woopsocial.env")["WOOPSOCIAL_API_KEY"])
    media_id = woop.upload(reel.read_bytes())
    video_url = f"https://cdn.woopsocial.com/VIDEO/{media_id}/original"
    s.log(f"uploaded to WoopSocial: {media_id}")

    # Facebook: let WoopSocial publish it at the right moment.
    schedule = ({"type": "SCHEDULE_FOR_LATER", "scheduledFor": when.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
                if when else {"type": "PUBLISH_NOW"})
    req = {"content": [{"text": fb_text, "media": [{"type": "MEDIA_LIBRARY", "mediaId": media_id}]}],
           "schedule": schedule,
           "socialAccounts": [{"platform": "FACEBOOK", "socialAccountId": s.FB_ACCOUNT, "postType": "REEL"}]}
    v = woop.tool("posts_validate_simple", {"requestJson": json.dumps(req)})
    if isinstance(v, dict) and not v.get("isValid", True):
        raise SystemExit(f"WoopSocial rejected the Facebook reel: {v.get('errors')}")
    fb_post = woop.tool("posts_create_simple", {"requestJson": json.dumps(req)})
    s.log(f"Facebook reel {'scheduled' if when else 'posted'}: {fb_post.get('id')}")

    # Instagram: create the container now, publish at the time.
    meta = s.env_file("meta.env")
    ig_id, token = meta["META_IG_ID"], meta["META_IG_TOKEN"]
    container = graph(f"{ig_id}/media", {"media_type": "REELS", "video_url": video_url,
                                         "caption": ig_text, "share_to_feed": "true"}, token)["id"]
    for _ in range(60):  # up to ~10 minutes of processing
        st = graph_get(container, "status_code,status", token)
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") == "ERROR":
            raise SystemExit(f"Instagram could not process the video: {st.get('status')}")
        time.sleep(10)
    else:
        raise SystemExit("Instagram still processing after 10 minutes")
    s.log("Instagram reel processed" + (", waiting for publish time" if when else ""))
    if when:
        while (left := (when - dt.datetime.now(dt.timezone.utc)).total_seconds()) > 0:
            time.sleep(min(left, 30))
    pub = graph(f"{ig_id}/media_publish", {"creation_id": container}, token)["id"]
    link = graph_get(pub, "permalink", token).get("permalink", pub)
    s.log(f"Instagram reel live: {link}")
    s.telegram(f"🎬 Reel posted.\nInstagram: {link}\nFacebook: WoopSocial, "
               f"{(when or dt.datetime.now(s.IST)).astimezone(s.IST).strftime('%H:%M')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
