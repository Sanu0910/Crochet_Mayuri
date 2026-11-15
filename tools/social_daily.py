"""Mayuri'z daily social post: one product poster -> Instagram + Facebook.

Runs by itself (Windows Task Scheduler, see tools/install-social.ps1) at
13:00 and 20:00 IST. No AI involved at run time: it picks the next piece from
the live site, draws a poster with Pillow, posts it and tells the team.

  py tools/social_daily.py            # post the next piece now
  py tools/social_daily.py --dry-run  # only make the poster, post nothing

Order: newest pieces first (top of the PRODUCTS list), skipping pieces still
called "New Piece" or in the NEW group, never the same category twice in a
row, never a piece twice.

Instagram goes through Meta's Graph API (META_IG_ID / META_IG_TOKEN in
%USERPROFILE%\\.mayuriz\\meta.env). Facebook goes through WoopSocial
(WOOPSOCIAL_API_KEY in woopsocial.env), because posts from the unpublished
MayuriZ Meta app stay hidden. The poster is uploaded to WoopSocial once and
its public CDN link is what Instagram downloads.

State and log: %LOCALAPPDATA%\\MayurizSocial\\ (state.json, social.log,
posters/). Optional reminders for the Telegram note: todo.txt in the same
folder, one line per open to-do.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

SITE = "https://mayurisyarntales.online/"
EMAIL = "hello@mayurisyarntales.online"
GRAPH = "https://graph.facebook.com/v23.0/"
WOOP = "https://api.woopsocial.com/mcp"
FB_ACCOUNT = "195397615435644928"          # WoopSocial id of the Facebook Page
CHAT = "-1003843804840"                    # team Telegram group
HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"
STATE_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "MayurizSocial"
STATE = STATE_DIR / "state.json"
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))

# pieces already shown in the intro carousel (14 Nov 2026)
ALREADY_POSTED = ["mixed-rose-bouquet", "marigold-ruffle-scrunchie", "golden-sunflower",
                  "classic-red-bow", "heart-keychain-pair", "ruby-bow-handbag", "ocean-blue-scrunchie"]

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

INK, ACCENT, CREAM, GREY = (29, 29, 31), (200, 86, 74), (249, 236, 228), (110, 110, 115)


def log(msg: str) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    line = f"{dt.datetime.now(IST):%Y-%m-%d %H:%M} {msg}"
    print(line)
    with open(STATE_DIR / "social.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def env_file(name: str) -> dict:
    out = {}
    p = Path.home() / ".mayuriz" / name
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^([A-Z_]+)=(.*)$", line.strip())
            if m:
                out[m.group(1)] = m.group(2).strip()
    return out


def http(url: str, data: bytes | None = None, headers: dict | None = None, method: str | None = None,
         timeout: int = 60):
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), dict(r.headers)


def post_json(url: str, body: dict, headers: dict | None = None):
    raw, hdrs = http(url, json.dumps(body).encode(), {"content-type": "application/json", **(headers or {})})
    return raw, hdrs


# ---------------------------------------------------------------- products
def products() -> list[dict]:
    raw, _ = http(f"{SITE}index.html?t={int(time.time())}")
    html = raw.decode("utf-8")
    block = html.split("/* PRODUCTS:START */")[1].split("/* PRODUCTS:END */")[0]
    out = []
    for entry in block.split("{")[1:]:
        entry = entry.split("}")[0]

        def field(k):
            m = re.search(k + r":\s*'((?:[^'\\]|\\.)*)'", entry)
            return re.sub(r"\\(.)", r"\1", m.group(1)) if m else ""
        p = {k: field(k) for k in ("id", "sku", "name", "tag", "desc", "image")}
        if p["id"] and p["image"]:
            out.append(p)
    if len(out) < 5:
        raise RuntimeError(f"only {len(out)} products parsed from the live site")
    return out


def pick(items: list[dict], state: dict) -> dict | None:
    fresh = [p for p in items if p["id"] not in state["posted"]
             and not p["name"].lower().startswith("new piece") and "-NEW-" not in p["sku"]]
    if not fresh:
        return None
    for p in fresh:
        if p["tag"] != state.get("last_tag"):
            return p
    return fresh[0]


# ---------------------------------------------------------------- poster
def font(name: str, size: int, weight: str) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(FONTS / name), size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def fit_text(text: str, name: str, weight: str, start: int, max_w: int) -> ImageFont.FreeTypeFont:
    size = start
    while size > 30:
        f = font(name, size, weight)
        if f.getlength(text) <= max_w:
            return f
        size -= 4
    return font(name, size, weight)


def poster(p: dict) -> bytes:
    W, H, PH = 1080, 1350, 1040
    raw, _ = http(SITE + p["image"])
    photo = Image.open(BytesIO(raw)).convert("RGB")
    canvas = Image.new("RGB", (W, H), CREAM)
    # photo area: whole photo shown (its own text never cut), blurred copy behind
    bg = ImageOps.fit(photo, (W, PH), Image.LANCZOS).filter(ImageFilter.GaussianBlur(36))
    fg = photo.copy()
    fg.thumbnail((W, PH), Image.LANCZOS)
    bg.paste(fg, ((W - fg.width) // 2, (PH - fg.height) // 2))
    canvas.paste(bg, (0, 0))
    d = ImageDraw.Draw(canvas)
    # name
    nf = fit_text(p["name"], "Caveat.ttf", "Bold", 84, W - 120)
    d.text((W / 2, PH + 62), p["name"], font=nf, fill=INK, anchor="mm")
    # website pill
    pf = font("Inter.ttf", 34, "Bold")
    label = "mayurisyarntales.online"
    tw = pf.getlength(label)
    x0, y0 = (W - tw) / 2 - 34, PH + 118
    d.rounded_rectangle((x0, y0, x0 + tw + 68, y0 + 64), radius=32, fill=ACCENT)
    d.text((W / 2, y0 + 32), label, font=pf, fill=(255, 255, 255), anchor="mm")
    # email
    ef = font("Inter.ttf", 30, "SemiBold")
    d.text((W / 2, PH + 236), EMAIL, font=ef, fill=ACCENT, anchor="mm")
    out = BytesIO()
    canvas.save(out, "JPEG", quality=90)
    return out.getvalue()


def captions(p: dict) -> tuple[str, str]:
    desc = p["desc"].strip()
    tags = TAG_HASHTAGS.get(p["tag"], "#crochetlove #giftideas")
    ig = (f"{p['name']} 🧶\n\n{desc}\n\nHandmade by Mayuri, made to order in India.\n"
          f"Order on our website: mayurisyarntales.online\n📩 {EMAIL}\n\n"
          f"#crochet #handmadeinindia #mayuriz {tags}")
    fb = (f"{p['name']} 🧶\n\n{desc}\n\nHandmade by Mayuri, made to order in India.\n"
          f"Order yours: {SITE}\n📩 {EMAIL}")
    return ig, fb


# ---------------------------------------------------------------- WoopSocial (MCP over HTTP)
class Woop:
    def __init__(self, key: str):
        self.url = WOOP + "?api_key=" + urllib.parse.quote(key)
        self.session = None
        self.n = 0
        self._rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                                 "clientInfo": {"name": "mayuriz-daily", "version": "1"}})
        self._rpc("notifications/initialized", {}, notify=True)

    def _rpc(self, method, params, notify=False):
        body = {"jsonrpc": "2.0", "method": method, "params": params}
        if not notify:
            self.n += 1
            body["id"] = self.n
        headers = {"accept": "application/json, text/event-stream"}
        if self.session:
            headers["mcp-session-id"] = self.session
        raw, hdrs = post_json(self.url, body, headers)
        sid = {k.lower(): v for k, v in hdrs.items()}.get("mcp-session-id")
        self.session = sid or self.session
        if notify:
            return None
        text = raw.decode("utf-8").strip()
        if not text.startswith("{"):
            text = [l[5:] for l in text.splitlines() if l.startswith("data:")][-1]
        j = json.loads(text)
        if "error" in j:
            raise RuntimeError(f"WoopSocial {method}: {j['error']}")
        return j["result"]

    def tool(self, name, args):
        res = self._rpc("tools/call", {"name": name, "arguments": args})
        txt = "".join(c.get("text", "") for c in res.get("content", []))
        if res.get("isError"):
            raise RuntimeError(f"WoopSocial {name}: {txt[:400]}")
        try:
            return json.loads(txt)
        except ValueError:
            return txt

    def upload(self, data: bytes) -> str:
        projects = self.tool("projects_list", {})
        project = (projects if isinstance(projects, list) else projects.get("data", []))[0]["id"]
        s = self.tool("media_uploads_create_session", {"projectId": project, "fileSizeInBytes": len(data)})
        size = s.get("partSizeInBytes") or len(data)
        for i, part in enumerate(s["parts"]):
            http(part["uploadUrl"], data[i * size:(i + 1) * size], method="PUT", timeout=120)
        sid = s.get("uploadSessionId") or s.get("sessionId") or s.get("id")
        c = self.tool("media_uploads_complete_session", {"uploadSessionId": sid})
        return c.get("mediaId") or c.get("id") or c["media"]["id"]

    def post_facebook(self, media_id: str, text: str, alt: str) -> str:
        req = {"content": [{"text": text, "media": [{"type": "MEDIA_LIBRARY", "mediaId": media_id, "altText": alt}]}],
               "schedule": {"type": "PUBLISH_NOW"},
               "socialAccounts": [{"platform": "FACEBOOK", "socialAccountId": FB_ACCOUNT, "postType": "IMAGE"}]}
        v = self.tool("posts_validate_simple", {"requestJson": json.dumps(req)})
        if isinstance(v, dict) and not v.get("isValid", True):
            raise RuntimeError(f"WoopSocial rejected the post: {v.get('errors')}")
        p = self.tool("posts_create_simple", {"requestJson": json.dumps(req)})
        for _ in range(24):
            time.sleep(5)
            g = self.tool("posts_get", {"postId": p["id"]})
            st = [a.get("deliveryStatus") for a in g.get("socialAccountPosts", [])]
            if st and all(s in ("PUBLISHED", "FAILED") for s in st):
                if "FAILED" in st:
                    raise RuntimeError(f"Facebook delivery failed: {json.dumps(g.get('socialAccountPosts'))[:400]}")
                return p["id"]
        raise RuntimeError("Facebook delivery still pending after 2 minutes")


# ---------------------------------------------------------------- Instagram (Graph API)
def post_instagram(ig_id: str, token: str, image_url: str, caption: str) -> str:
    def call(path, params):
        raw, _ = post_json(GRAPH + path, {**params, "access_token": token})
        return json.loads(raw)
    c = call(f"{ig_id}/media", {"image_url": image_url, "caption": caption})["id"]
    for _ in range(20):
        raw, _ = http(f"{GRAPH}{c}?fields=status_code&access_token={urllib.parse.quote(token)}")
        st = json.loads(raw).get("status_code")
        if st == "FINISHED":
            break
        if st == "ERROR":
            raise RuntimeError("Instagram could not process the image")
        time.sleep(3)
    pub = call(f"{ig_id}/media_publish", {"creation_id": c})["id"]
    raw, _ = http(f"{GRAPH}{pub}?fields=permalink&access_token={urllib.parse.quote(token)}")
    return json.loads(raw).get("permalink", pub)


# ---------------------------------------------------------------- Telegram
def telegram(text: str) -> None:
    token = env_file("bot.env").get("TELEGRAM_TOKEN")
    if not token:
        return
    try:
        post_json(f"https://api.telegram.org/bot{token}/sendMessage",
                  {"chat_id": CHAT, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True})
    except Exception as e:  # never let a note failure hide a successful post
        log(f"telegram note failed: {e}")


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- main
def main() -> int:
    dry = "--dry-run" in sys.argv
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {"posted": {}}
    for pid in ALREADY_POSTED:
        state["posted"].setdefault(pid, {"at": "2026-11-14", "note": "intro carousel"})

    p = pick(products(), state)
    if not p:
        log("nothing left to post")
        return 0
    img = poster(p)
    (STATE_DIR / "posters").mkdir(exist_ok=True)
    (STATE_DIR / "posters" / f"{p['id']}.jpg").write_bytes(img)
    ig_text, fb_text = captions(p)
    if dry:
        log(f"DRY RUN: poster for {p['id']} saved to {STATE_DIR / 'posters' / (p['id'] + '.jpg')}")
        print("\n--- Instagram caption ---\n" + ig_text + "\n\n--- Facebook caption ---\n" + fb_text)
        return 0

    meta, woop_env = env_file("meta.env"), env_file("woopsocial.env")
    woop = Woop(woop_env["WOOPSOCIAL_API_KEY"])
    media_id = woop.upload(img)
    image_url = f"https://cdn.woopsocial.com/IMAGE/{media_id}/original"
    alt = f"{p['name']}: {p['desc']}"[:900]

    result, errors = {"at": dt.datetime.now(IST).isoformat(timespec="seconds")}, []
    try:
        result["ig"] = post_instagram(meta["META_IG_ID"], meta["META_IG_TOKEN"], image_url, ig_text)
    except Exception as e:
        errors.append(f"Instagram: {e}")
    try:
        result["fb"] = woop.post_facebook(media_id, fb_text, alt)
    except Exception as e:
        errors.append(f"Facebook: {e}")

    if "ig" in result or "fb" in result:       # anything went out: never post this piece again
        state["posted"][p["id"]] = result
        state["last_tag"] = p["tag"]
    STATE.write_text(json.dumps(state, indent=1), encoding="utf-8")

    left = len([x for x in products() if x["id"] not in state["posted"]])
    done = " + ".join(n for n, k in (("Instagram", "ig"), ("Facebook", "fb")) if k in result)
    lines = [f"📣 <b>Daily post:</b> {esc(p['name'])}"]
    if done:
        lines.append(f"{done} ✅")
    if "ig" in result:
        lines.append(result["ig"])
    lines += [f"⚠️ {esc(e)[:300]}" for e in errors]
    lines.append(f"<i>{left} pieces still to post.</i>")
    todo = STATE_DIR / "todo.txt"
    if todo.exists():
        items = [l.strip() for l in todo.read_text(encoding="utf-8").splitlines() if l.strip()]
        if items:
            lines.append("\n<b>Still to do:</b>\n" + "\n".join("• " + esc(i) for i in items[:6]))
    telegram("\n".join(lines))
    log(f"{p['id']}: {done or 'nothing posted'}" + (f" | {'; '.join(errors)}" if errors else ""))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
