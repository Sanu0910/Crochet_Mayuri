# Mayuri'z uploader bot

Send a photo to Telegram, tap a category, and the piece is on the site a
minute later. The bot does exactly what a person would do by hand: resize
the photo into `images/`, add an entry to the `PRODUCTS` list in
`index.html`, add a matching scene to `video/src/theme.ts`, commit, push.

```
photo + caption  →  [category buttons]  →  commit + push  →  GitHub Pages
```

## Using it

Send a photo. First line of the caption is the name, put a category hashtag
anywhere in it, and add a description underneath if you want one:

```
Ocean Blue Ruffle Scrunchie #scrunchies
Deep teal ruffles on a soft white band.
```

Categories: `#scrunchies` `#bows` `#flowers` `#clips` `#keychains`
`#garlands` `#hearts`

Without a description the bot writes a plain one you can edit later. Every
upload gets a "New" badge. Forget the hashtag and it asks for one rather
than guessing.

### Commands

| | |
|---|---|
| `/list` | every piece, by category — the names the other commands expect |
| `/status` | how many pieces, whether the film still matches, the last change |
| `/caption <name> \| <new wording>` | reword a piece without touching the code |
| `/rename <name> \| <new name>` | fix a name |
| `/remove <name>` | take a piece and its photo down |
| `/film` | re-render the video |
| `/whoami`, `/help` | |

`/caption` and `/rename` leave the id and the photo file alone, since those
are what the gallery, the film and any existing link already point at.

The always-on version also has `/recent` and `/undo`.

### It reacts

The photo you sent gets a reaction as it goes: 👀 picked up, 🎉 published,
🤔 something was wrong. Telegram only allows reactions from a fixed list, so
this is best effort and never fails an upload.

### It tells you what it's doing

An upload gets one message that fills itself in as the work happens, rather
than a burst of separate notifications for a job that takes three seconds:

```
🧶 Ocean Blue Ruffle Scrunchie

✅ Reading the caption — Scrunchies
✅ Saving the photo — ocean-blue-ruffle-scrunchie.jpg (156 KB)
✅ Adding it to the gallery — 24 pieces now
✅ Adding it to the film — scene added
✅ Pushing to GitHub — commit a1b2c3d
✅ Rebuilding the site — live in a minute or two
```

The last two lines are filled in by `announce.py` after the push has really
happened, so the message reports what landed rather than what was intended.
If a step fails, the checklist stops there and says why.

## How it runs

Two halves, because neither can do the job alone.

```
photo → Cloudflare Worker  → 👀 and a reply, in under a second
                           → pokes GitHub
       GitHub Actions      → resize, edit, commit, push, rebuild (~30s)
                           → fills in the checklist it promised
```

**The Worker** (`worker/worker.js`) is always awake, so it can answer
immediately. It can't resize a photo or commit to a repository, so it hands
that on.

**GitHub Actions** (`poll_once.py`) does the real work. It only exists in
bursts, which is exactly why it can't be the part that answers you.

Before the Worker existed this ran on a `*/5` schedule and a photo took
5–15 minutes to appear — when GitHub ran the schedule at all. On this
repository it never did: ninety minutes, zero scheduled runs. The hourly
`schedule:` that remains is a safety net for if the Worker is ever removed,
and no-ops while the webhook is live.

### Setting up the Worker

1. **A Cloudflare account** (free) → Workers & Pages → *Create* → *Start
   with Hello World* → *Deploy*. Then *Edit code*, paste all of
   `bot/worker/worker.js` over what's there, and deploy again.

2. **Settings → Variables**. Three secrets:

   | | |
   |---|---|
   | `TELEGRAM_TOKEN` | from [@BotFather](https://t.me/BotFather) |
   | `GITHUB_TOKEN` | fine-grained PAT, **Contents: read and write**, this repo only |
   | `WEBHOOK_SECRET` | any long random string you invent |

   and two plain variables:

   | | |
   |---|---|
   | `GITHUB_REPO` | `Sanu0910/Crochet_Mayuri` |
   | `ALLOWED_USER_IDS` | `924868395,5770732970` |

3. **Point Telegram at it.** Open this once in a browser, with your own
   values filled in:

   ```
   https://api.telegram.org/bot<TELEGRAM_TOKEN>/setWebhook?url=<WORKER_URL>&secret_token=<WEBHOOK_SECRET>
   ```

   `{"ok":true}` means done. Check any time with `/getWebhookInfo`.

4. **Group Privacy off** in BotFather (`/mybots` → Bot Settings → Group
   Privacy → Turn off), or photos posted in a group never reach the bot at
   all.

To undo it: `https://api.telegram.org/bot<TOKEN>/deleteWebhook`. Polling
then works again on the hourly schedule.

### Why the GitHub token comes back

The scheduled-only version needed none, because it ran *inside* the
repository. The Worker runs outside it, so it needs its own key. Any instant
option has this cost — a hosted `bot/main.py` would too.

### Always on instead — instant, needs a host

`main.py` is the same bot as a long-running process holding a connection
open. Categories become buttons to tap rather than hashtags. It needs a host
(~$5/month) and the same three variables. Only one of the three modes may be
live at a time: two things polling the same bot fight over updates.

> **`GIT_BRANCH` matters.** GitHub Pages publishes this repo from
> `claude/website-mobile-redesign-xfmicu`, *not* from `main`. If Pages is
> ever repointed at `main`, change it to match or uploads go nowhere visible.

## What it does not do

- **It doesn't re-render the film.** Adding a product puts it in the film's
  scene list, but rendering needs Chrome and a few minutes of CPU. `/film`
  hands that to `.github/workflows/render-film.yml`, which renders,
  compresses, refreshes the poster and pushes — about five minutes.
- **It doesn't check what's in the photo.** Whatever you send goes up.
- **It doesn't create categories.** They're fixed in `catalogue.py` and must
  match the `CATEGORIES` list in `index.html`. Adding one is a code change.

## The markers

Both product lists carry `PRODUCTS:START` / `PRODUCTS:END` comments. The bot
inserts between them and refuses to touch a file where they're missing,
rather than guessing and corrupting the page. Don't remove them.

New entries are placed with the rest of their category so the gallery stays
grouped, or at the end of the list if the category is empty.

## Tests

The half that edits the site is tested; the half that talks to Telegram is
not (it needs a live bot).

```bash
cd bot
python test_site_edit.py   # inserting into both product lists
python test_publish.py     # a whole upload against a throwaway git remote
```

`test_publish.py` clones the real repo, so it also fails if a change to
`index.html` would break the bot.
