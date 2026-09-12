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

**Commands:** `/help`, `/whoami`, `/film` (re-render the video). The
always-on version below also has `/recent` and `/undo`.

## Two ways to run it

The bot is the same either way; only how often it checks differs.

### Scheduled — free, 5–15 minutes (what's set up)

`telegram-uploader.yml.example` runs `poll_once.py` on GitHub Actions every
five minutes: it wakes, publishes whatever arrived, and exits. The
repository is public so Actions minutes are free, and because the job runs
*inside* the repo it already has permission to push — **no personal access
token needed**.

To switch it on:

1. **Settings → Secrets and variables → Actions**
   - Secret `TELEGRAM_TOKEN` — the token from [@BotFather](https://t.me/BotFather)
   - Variable `ALLOWED_USER_IDS` — e.g. `924868395,5770732970`
2. Copy `bot/telegram-uploader.yml.example` to
   `.github/workflows/telegram-uploader.yml` and commit it.

To switch it off, delete that workflow file.

Two things to know about scheduled workflows: GitHub disables them after 60
days with no repository activity, and `*/5` is a best effort — under load a
run can be ten minutes late. Neither matters much for a shop that gains a few
pieces a week.

### Always on — instant, needs a host

`main.py` is the same bot as a long-running process that holds a connection
open, so uploads land in seconds and the category can be a tap on a button
rather than a hashtag. It needs somewhere to run (Railway, Fly, a Raspberry
Pi) and, because it is outside the repository, a GitHub token:

| Variable | What |
|---|---|
| `TELEGRAM_TOKEN` | from [@BotFather](https://t.me/BotFather) |
| `GITHUB_TOKEN` | fine-grained PAT — **Contents: read and write**, plus **Actions: read and write** for `/film`, scoped to this repository only |
| `ALLOWED_USER_IDS` | comma-separated Telegram user IDs |

```bash
pip install -r requirements.txt
TELEGRAM_TOKEN=... GITHUB_TOKEN=... ALLOWED_USER_IDS=123,456 python main.py
```

Only one of the two may be live at a time — two pollers fight over the same
updates and both misbehave.

> **`GIT_BRANCH` matters.** GitHub Pages publishes this repo from
> `claude/website-mobile-redesign-xfmicu`, *not* from `main` — that's what
> both entry points default to, because a push anywhere else won't appear on
> the site. If Pages is ever repointed at `main`, change it to match or
> uploads will silently go nowhere visible.

### Group privacy must be off

In BotFather: `/mybots` → the bot → Bot Settings → Group Privacy → **Turn
off**. On by default, a bot in a group only receives messages that mention
it, so your photos never arrive.

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
