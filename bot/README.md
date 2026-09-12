# Mayuri'z uploader bot

Send a photo to Telegram, tap a category, and the piece is on the site a
minute later. The bot does exactly what a person would do by hand: resize
the photo into `images/`, add an entry to the `PRODUCTS` list in
`index.html`, add a matching scene to `video/src/theme.ts`, commit, push.

```
photo + caption  →  [category buttons]  →  commit + push  →  GitHub Pages
```

## Using it

**Add a piece.** Send a photo. Put the name on the first line of the
caption and, if you want one, a description on the second:

```
Ocean Blue Ruffle Scrunchie
Deep teal ruffles on a soft white band.
```

Then tap a category. Without a description the bot writes a plain one you
can edit later. Every upload gets a "New" badge.

**Commands**

| | |
|---|---|
| `/recent` | the last few changes |
| `/undo` | undo the most recent change (reverts and pushes) |
| `/film` | re-render the video with everything currently in the shop |
| `/whoami` | your Telegram ID and this chat's ID |
| `/help` | the above |

## What it does not do

- **It doesn't re-render the film.** Adding a product puts it in the film's
  scene list, but rendering needs Chrome and a few minutes of CPU, which is
  more than the bot's host should carry. `/film` hands that to GitHub
  Actions (`.github/workflows/render-film.yml`) instead, which renders,
  compresses, refreshes the poster and pushes — about five minutes.
- **It doesn't check what's in the photo.** Whatever you send goes up.
  `/undo` is the safety net.
- **It doesn't create categories.** They're fixed in `catalogue.py` and must
  match the `CATEGORIES` list in `index.html`. Adding one is a code change.

## Running it

Needs three environment variables:

| Variable | What |
|---|---|
| `TELEGRAM_TOKEN` | from [@BotFather](https://t.me/BotFather) |
| `GITHUB_TOKEN` | fine-grained PAT, see below |
| `ALLOWED_USER_IDS` | comma-separated Telegram user IDs allowed to publish |

Optional: `GITHUB_REPO` (default `Sanu0910/Crochet_Mayuri`), `GIT_BRANCH`,
`SITE_URL` (shown in the confirmation message), `WORKDIR`.

> **`GIT_BRANCH` matters.** GitHub Pages publishes this repo from
> `claude/website-mobile-redesign-xfmicu`, *not* from `main` — that's what
> the bot defaults to, because a push anywhere else won't appear on the
> site. If Pages is ever repointed at `main`, change this variable to match
> or uploads will silently go nowhere visible.

**The GitHub token** should be a fine-grained personal access token scoped
to this one repository, with:

- **Contents: Read and write** — to push the photo and the edits
- **Actions: Read and write** — only needed for `/film`

Nothing else. Make it at
<https://github.com/settings/personal-access-tokens>.

**Locally:**

```bash
pip install -r requirements.txt
TELEGRAM_TOKEN=... GITHUB_TOKEN=... ALLOWED_USER_IDS=123,456 python main.py
```

**On Railway:** deploy this directory as a service, set the three variables,
and that's it. It long-polls Telegram, so it needs no public URL and no
webhook.

### Two things that catch people out

1. **Group privacy must be off.** In BotFather: `/mybots` → the bot → Bot
   Settings → Group Privacy → Turn off. On by default, a bot in a group only
   receives messages that mention it, so your photos never arrive.
2. **Only one instance may poll at a time.** Two copies running (say, a local
   one and the deployed one) fight over updates and both misbehave.

### If you don't know your Telegram user ID

Message the bot `/whoami`, or just send it anything — an unrecognised user
gets told their own ID so it can be added to `ALLOWED_USER_IDS`.

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
